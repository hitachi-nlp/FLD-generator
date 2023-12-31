import random
import re
from enum import Enum
from abc import abstractmethod, ABC
from statistics import mean, stdev
from typing import Dict, List, Optional, Union, Iterable, Tuple, Any, Set, Tuple
import logging
import copy
from collections import defaultdict
from pprint import pprint, pformat

from FLD_generator.word_banks import POS, VerbForm, AdjForm, NounForm, WordForm, ATTR
from FLD_generator.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLD_generator.formula import Formula
from FLD_generator.proof import ProofTree, ProofNode
from FLD_generator.utils import flatten_dict, weighted_sampling, make_pretty_msg
from FLD_generator.translators.base import Translator
from FLD_generator.word_banks.base import WordBank
from FLD_generator.translation_distractors import build as build_translation_distractor, TranslationDistractorGenerationFailure
from FLD_generator.utils import (
    provable_from_incomplete_facts,
    disprovable_from_incomplete_facts,
    is_consistent_formula_set_with_logs,
    have_smaller_proofs_with_logs,
)
from FLD_generator.formula_checkers import (
    is_consistent_set,
    is_provable,
    is_disprovable,
    is_unknown,
)
import line_profiling

logger = logging.getLogger(__name__)

_DUMMY_SENTENCE = 'this is a dummy sntence'


class ProofStance(Enum):
    PROVED = 'PROVED'
    DISPROVED = 'DISPROVED'
    UNKNOWN = 'UNKNOWN'


class WorldAssumption(Enum):
    CWA = 'CWA'
    OWA = 'OWA'


def _generate_random_sentence(translator: Translator) -> Optional[str]:
    acceptable_formula_reps = translator.acceptable_formulas
    for formula_rep in random.sample(acceptable_formula_reps, len(acceptable_formula_reps)):
        nls, _ = translator.translate([Formula(formula_rep)], [])
        if nls[0][1] is not None:
            return nls[0][1]
    return None


def _make_world_assump_label(proof_stance: ProofStance,
                             world_assump: WorldAssumption,
                             version: str = '0.0') -> Any:
    if version == '0.0':
        if world_assump == WorldAssumption.CWA:
            if proof_stance == ProofStance.PROVED:
                return True
            elif proof_stance == ProofStance.DISPROVED:
                return False
            elif proof_stance == ProofStance.UNKNOWN:
                return False
            else:
                raise ValueError()
        elif world_assump == WorldAssumption.OWA:
            if proof_stance == ProofStance.PROVED:
                return True
            elif proof_stance == ProofStance.DISPROVED:
                return False
            elif proof_stance == ProofStance.UNKNOWN:
                return 'Unknown'
            else:
                raise ValueError()
        else:
            raise ValueError()
    elif version in ['0.1', '0.2']:
        if world_assump == WorldAssumption.CWA:
            if proof_stance == ProofStance.PROVED:
                return 'PROVED'
            elif proof_stance == ProofStance.DISPROVED:
                return 'DISPROVED'
            elif proof_stance == ProofStance.UNKNOWN:
                return 'DISPROVED'
            else:
                raise ValueError()
        elif world_assump == WorldAssumption.OWA:
            if proof_stance == ProofStance.PROVED:
                return 'PROVED'
            elif proof_stance == ProofStance.DISPROVED:
                return 'DISPROVED'
            elif proof_stance == ProofStance.UNKNOWN:
                return 'UNKNOWN'
            else:
                raise ValueError()
        else:
            raise ValueError()
    else:
        raise ValueError()


def _make_proof_stance_label(proof_stance: ProofStance,
                             version: str = '0.0') -> Any:
    if version == '0.0':
        if proof_stance == ProofStance.PROVED:
            return 'PROOF'
        elif proof_stance == ProofStance.DISPROVED:
            return 'DISPROOF'
        elif proof_stance == ProofStance.UNKNOWN:
            return 'UNKNOWN'
        else:
            raise ValueError()
    elif version in ['0.1', '0.2']:
        return proof_stance.value
    else:
        raise ValueError()


class _DistractorFakeNode(ABC):

    @property
    @abstractmethod
    def translation(self) -> Optional[str]:
        pass

    @property
    def children(self):
        return []

    @property
    def assump_children(self):
        return []

    @property
    def parent(self):
        return None

    @property
    def assump_parent(self):
        return None


class _FormulaDistractorNode(_DistractorFakeNode):

    def __init__(self, distractor: Formula):
        self._formula = distractor

    @property
    def formula(self) -> Optional[Formula]:
        return self._formula

    @property
    def translation(self) -> str:
        return self.formula.translation or self.formula.rep


class _TranslationDistractorNode(_DistractorFakeNode):

    def __init__(self, translation: str):
        self._translation = translation

    @property
    def translation(self) -> str:
        return self._translation


Node = Union[ProofNode, _DistractorFakeNode]


def _is_identical_node(this: Node, that: Node) -> bool:

    if isinstance(this, _TranslationDistractorNode) and isinstance(that, _TranslationDistractorNode):
        raise NotImplementedError()

    if isinstance(this, _TranslationDistractorNode) and not isinstance(that, _TranslationDistractorNode):
        return False
    elif not isinstance(this, _TranslationDistractorNode) and isinstance(that, _TranslationDistractorNode):
        return False

    return this.formula == that.formula


def _to_range(lower: int, upper: int) -> List[int]:
    return list(range(lower, upper + 1))


class NLProofSDataset:

    def __init__(self,
                 pipeline: ProofTreeGenerationPipeline,
                 depth_range: Tuple[int, int],
                 branch_extensions_range: Tuple[int, int],
                 proof_stances: Optional[List[str]] = None,
                 world_assump: str = 'OWA',
                 depth_weights: List[float] = None,
                 depth_1_reference_weight: Optional[float] = None,
                 force_fix_illegal_intermediate_constants=False,
                 unknown_ratio: float = 1 / 3.,
                 use_collapsed_translation_nodes_for_unknown_tree=False,
                 swap_ng_words: Optional[Set[str]] = None,
                 word_bank: Optional[WordBank] = None,
                 distractors_range: Optional[List[int]] = None,
                 translation_distractors_range: Optional[Tuple[int, int]] = None,
                 allow_inconsistency=False,
                 allow_smaller_proofs=False,
                 version: str = '0.2',
                 log_stats=True,
                 raise_if_translation_not_found=True):

        self.pipeline = pipeline

        proof_stances = proof_stances or ['PROVED', 'DISPROVED', 'UNKNOWN']
        self.proof_stances = [ProofStance(proof_stance) for proof_stance in proof_stances]
        self.world_assump = WorldAssumption(world_assump)
        self.unknown_ratio = unknown_ratio

        self.depths = _to_range(*depth_range)

        if depth_weights is not None:
            if len(depth_weights) != len(self.depths):
                raise ValueError()
        else:
            depth_weights = [1.0] * len(self.depths)
        depth_weights = [weight / sum(depth_weights) for weight in depth_weights]
        self._depth_weights = depth_weights
        logger.info('using depth weight: %s', str(self._depth_weights))

        self._depth_1_reference_weight = depth_1_reference_weight
        self._force_fix_illegal_intermediate_constants = force_fix_illegal_intermediate_constants

        self.branch_extension_steps = _to_range(*branch_extensions_range)
        self.num_distractors = _to_range(*distractors_range) if distractors_range is not None else [0]
        self.num_translation_distractors = _to_range(*translation_distractors_range) if branch_extensions_range is not None else [0]
        self.allow_inconsistency = allow_inconsistency
        self.allow_smaller_proofs = allow_smaller_proofs
        self.log_stats = log_stats,
        self.pipeline.log_stats = log_stats
        self.version = version
        self.raise_if_translation_not_found = raise_if_translation_not_found

        self.use_collapsed_translation_nodes_for_unknown_tree = use_collapsed_translation_nodes_for_unknown_tree
        if self.use_collapsed_translation_nodes_for_unknown_tree:
            self.word_swap_distractor = build_translation_distractor(
                'word_swap',
                word_bank=word_bank,
                swap_ng_words=swap_ng_words,
            )
        else:
            self.word_swap_distractor = None

    @profile
    def generate(self,
                 size: int,
                 conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=False,
                 conclude_hypothesis_from_random_sent_if_proof_is_unknown=False,
                 add_randome_sentence_if_context_is_null=True) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]], List[str], Dict[str, Any]]]:
        """ Generate dataset

        See discussions.md for the options.
        """
        sample_cum_stats = defaultdict(int)
        all_sample_stats = defaultdict(list)
        i_sample = 0
        while i_sample < size:
            # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! i_sample', i_sample)

            logger.info('\n\n')
            logger.info(make_pretty_msg(title='generate a dataset instance', status='start', boundary_level=5))

            # -- generate settings --
            proof_stance = self._sample_proof_stance()
            depth_idx = weighted_sampling(self._depth_weights)
            depth = self.depths[depth_idx]
            if proof_stance == ProofStance.UNKNOWN:
                depth += 1

            _num_distractors = random.sample(self.num_distractors, 1)[0]
            _num_translation_distractors = random.sample(self.num_translation_distractors, 1)[0]
            _branch_extension_steps = random.sample(self.branch_extension_steps, 1)[0]

            # -- make proof tree and distractors  --
            proof_tree, root_negation_formula, formula_distractors, translation_distractors, others, pipeline_stats = self.pipeline.run(
                depth,
                _branch_extension_steps,
                _num_distractors,
                _num_translation_distractors,
                depth_1_reference_weight=self._depth_1_reference_weight,
                allow_inconsistency=self.allow_inconsistency,
                allow_smaller_proofs=self.allow_smaller_proofs,
                force_fix_illegal_intermediate_constants=self._force_fix_illegal_intermediate_constants,
                raise_if_translation_not_found=self.raise_if_translation_not_found,
            )

            # -- sample stance --
            if len(proof_tree.leaf_nodes) == 0:
                # For some very rare case, this occurs.
                # Since we do not expect this behaviour, we raise error for future debug
                raise Exception(proof_tree.format_str)

            # -- sample nodes --
            if proof_stance == ProofStance.UNKNOWN:
                if random.random() < 0.5:
                    hypothesis_formula = proof_tree.root_node.formula
                    hypothesis = self._get_sent_from_node(proof_tree.root_node)
                else:
                    hypothesis_formula = root_negation_formula
                    hypothesis = root_negation_formula.translation or root_negation_formula.rep

                could_make_unknown = False
                for _ in range(10):
                    # dead_leaf_nodes = random.sample(proof_tree.leaf_nodes, max(1, int(len(proof_tree.leaf_nodes) * 0.3)))
                    dead_leaf_nodes = random.sample(proof_tree.leaf_nodes, 1)
                    if is_unknown(
                        [node.formula for node in proof_tree.leaf_nodes
                         if node not in dead_leaf_nodes],
                        hypothesis_formula,
                    ):
                        could_make_unknown = True
                        break
                if not could_make_unknown:
                    logger.warning('skip the sample because we could not make UNKNOWN proof by sub-sampling nodes.')
                    continue

            elif proof_stance == ProofStance.PROVED:
                hypothesis_formula = proof_tree.root_node.formula
                hypothesis = self._get_sent_from_node(proof_tree.root_node)
                dead_leaf_nodes = []

            elif proof_stance == ProofStance.DISPROVED:
                hypothesis_formula = root_negation_formula
                hypothesis = root_negation_formula.translation or root_negation_formula.rep
                dead_leaf_nodes = []

            alive_leaf_nodes = [node for node in proof_tree.leaf_nodes
                                if node not in dead_leaf_nodes]

            # dead nodes = missing nodes + collapsed nodes
            missing_leaf_nodes, collapsed_leaf_nodes = self._divide_into_missing_and_collapsed_nodes(dead_leaf_nodes)

            # -- make texts --
            context, formula_context, proof_text, formula_proof_text, node2id, id2node = self._make_text(
                proof_tree,
                proof_stance,

                dead_leaf_nodes=dead_leaf_nodes,
                missing_leaf_nodes=missing_leaf_nodes,
                collapsed_leaf_nodes=collapsed_leaf_nodes,

                node2id=None,
                id2node=None,

                formula_distractors=formula_distractors,
                translation_distractors=translation_distractors,

                add_randome_sentence_if_context_is_null=add_randome_sentence_if_context_is_null,
                conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=conclude_hypothesis_from_subtree_roots_if_proof_is_unknown,
                conclude_hypothesis_from_random_sent_if_proof_is_unknown=conclude_hypothesis_from_random_sent_if_proof_is_unknown,
            )

            # -- make negative proofs --
            negative_tree, negative_tree_missing_leaf_nodes = None, None
            all_negative_tree_attrs = [val for name, val in others.items()
                                       if name.find('negative_tree') >= 0]
            if len(all_negative_tree_attrs) > 0:
                negative_tree_attrs = random.choice(all_negative_tree_attrs)
                negative_tree, negative_tree_dead_leaf_nodes = negative_tree_attrs['tree'], negative_tree_attrs['missing_nodes']

            if negative_tree is not None:
                negative_tree_missing_leaf_nodes = negative_tree_dead_leaf_nodes
                negative_tree_collapsed_leaf_nodes = []

                if len(negative_tree_missing_leaf_nodes) == 0:
                    negative_proof_stance = ProofStance.PROVED
                else:
                    negative_proof_stance = ProofStance.UNKNOWN

                negative_hypothesis_formula = negative_tree.root_node.formula
                negative_hypothesis = self._get_sent_from_node(negative_hypothesis_formula)

                _, _, negateive_proof_text, _, _, _ = self._make_text(
                    negative_tree,
                    ProofStance.UNKNOWN,

                    dead_leaf_nodes=negative_tree_dead_leaf_nodes,
                    missing_leaf_nodes=negative_tree_missing_leaf_nodes,
                    collapsed_leaf_nodes=negative_tree_collapsed_leaf_nodes,

                    node2id=node2id,
                    id2node=id2node,

                    add_randome_sentence_if_context_is_null=add_randome_sentence_if_context_is_null,
                    conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=conclude_hypothesis_from_subtree_roots_if_proof_is_unknown,
                    conclude_hypothesis_from_random_sent_if_proof_is_unknown=conclude_hypothesis_from_random_sent_if_proof_is_unknown,
                )

            else:
                negative_hypothesis_formula, negative_hypothesis, negateive_proof_text, negative_proof_stance = None, None, None, None

            # -- compute depth --
            if proof_stance == ProofStance.UNKNOWN:
                proof_depth = None
            else:
                if proof_tree.root_node.argument.id.startswith('reference'):
                    proof_depth = 0
                else:
                    proof_depth = proof_tree.depth

            all_positive_formulas = [leaf_node.formula for leaf_node in alive_leaf_nodes]
            all_negative_formulas = formula_distractors
            all_formulas = all_positive_formulas + all_negative_formulas

            stance_msg = None
            if proof_stance == ProofStance.PROVED:
                # assert is_provable(all_positive_formulas, hypothesis_formula)
                if not is_provable(all_positive_formulas, hypothesis_formula):
                    logger.critical('\n== all_positive_formulas ==\n' + pformat(all_formulas))
                    logger.critical('\n== hypothesis_formula ==\n' + hypothesis_formula.rep)
                    logger.critical('\n== tree ==\n' + proof_tree.format_str)
                    # import pudb; pudb.set_trace()
                    stance_msg = 'the hypothesis can not be proved even the label is PROVED. This is unexpected and implies bugs.'
            elif proof_stance == ProofStance.DISPROVED:
                # assert is_disprovable(all_positive_formulas, hypothesis_formula)
                if not is_disprovable(all_positive_formulas, hypothesis_formula):
                    logger.critical('\n== all_positive_formulas ==\n' + pformat(all_formulas))
                    logger.critical('\n== hypothesis_formula ==\n' + hypothesis_formula.rep)
                    logger.critical('\n== tree ==\n' + proof_tree.format_str)
                    # import pudb; pudb.set_trace()
                    stance_msg = 'the hypothesis can not be disproved even the label is DISPROVED. This is unexpected and implies bugs.'
            elif proof_stance == ProofStance.UNKNOWN:
                # assert is_unknown(all_positive_formulas, hypothesis_formula)
                if not is_unknown(all_positive_formulas, hypothesis_formula):
                    logger.critical('\n== all_positive_formulas ==\n' + pformat(all_formulas))
                    logger.critical('\n== hypothesis_formula ==\n' + hypothesis_formula.rep)
                    logger.critical('\n== tree ==\n' + proof_tree.format_str)
                    # import pudb; pudb.set_trace()
                    stance_msg = 'the hypothesis can be (dis)proved even the label is UNKNOWN. This is unexpected and implies bugs.'
            if stance_msg is not None:
                logger.fatal('proof_tree leaf nodes:')
                logger.fatal(pformat(proof_tree.leaf_nodes))

                logger.fatal('all_positive_formulas:')
                for formula in all_negative_formulas:
                    logger.fatal('    %s', formula.rep)

                logger.fatal('hypothesis:')
                logger.fatal('    %s', hypothesis_formula.rep)

                logger.fatal('proof_tree:')
                logger.fatal(proof_tree.format_str)

                raise Exception(stance_msg)

            if not self.allow_inconsistency:
                _is_consistent, logs = is_consistent_formula_set_with_logs(
                    all_formulas, [], [],
                )
                if not _is_consistent:
                    for msg in logs:
                        logger.info(msg)
                    raise Exception('Unexpected.')

            if not self.allow_smaller_proofs:
                _have_smaller_proofs, logs = have_smaller_proofs_with_logs(
                    all_positive_formulas, [], [],
                    hypothesis_formula,
                    hypothesis_formula,
                    distractor_formulas=all_negative_formulas,
                )
                if _have_smaller_proofs:
                    for log in logs:
                        logger.info(log)
                    raise Exception('Unexpected.')

            # -- make output json --
            world_assump_label = _make_world_assump_label(proof_stance, self.world_assump, version=self.version)
            world_assump_negative_label = _make_world_assump_label(negative_proof_stance, self.world_assump, version=self.version) if negative_proof_stance is not None else None

            stance_label = _make_proof_stance_label(proof_stance, version=self.version)
            negative_stance_label = _make_proof_stance_label(negative_proof_stance, version=self.version) if negative_proof_stance is not None else None

            dataset_json = {
                'version': self.version,

                'hypothesis': hypothesis,
                'hypothesis_formula': hypothesis_formula.rep,
                'context': context,
                'context_formula': formula_context,
                'proofs': [proof_text] if proof_text is not None else [],
                'proofs_formula': [formula_proof_text] if formula_proof_text is not None else [],

                'negative_hypothesis': negative_hypothesis,
                'negative_hypothesis_formula': negative_hypothesis_formula.rep if negative_hypothesis_formula is not None else None,
                'negative_proofs': [negateive_proof_text] if negateive_proof_text is not None else [],
                'negative_original_tree_depth': negative_tree.depth if negative_tree is not None else None,

                'original_tree_depth': proof_tree.depth,

                # We follow ProofWriter to define proof depth as tree depth - 1
                'depth': proof_depth,

                'num_formula_distractors': len(formula_distractors),
                'num_translation_distractors': len(translation_distractors),
                'num_all_distractors': len(formula_distractors) + len(translation_distractors),
            }
            if self.version in ['0.0', '0.1']:
                dataset_json.update({
                    'proof_stance': stance_label,
                    'negative_proof_stance': negative_stance_label,

                    'answer': world_assump_label,
                    'negative_answer': world_assump_negative_label,
                })
            else:
                dataset_json.update({
                    'proof_label': stance_label,
                    'negative_proof_label': negative_stance_label,

                    'world_assump_label': world_assump_label,
                    'negative_world_assump_label': world_assump_negative_label,
                })

            # Update statistics
            if self.log_stats:
                sample_stats = flatten_dict(pipeline_stats)
                sample_stats[f'answer.{world_assump_label}'] = 1
                sample_stats[f'proof_stance.{proof_stance.value}'] = 1
                sample_stats['word_count_hypothesis'] = len(hypothesis.split(' '))
                sample_stats['word_count_context'] = len(context.split(' '))
                sample_stats['word_count_proof'] = len(proof_text.split(' ')) if proof_text is not None else None
                sample_stats['word_count_all'] = (sample_stats['word_count_hypothesis'] + sample_stats['word_count_context'] + sample_stats['word_count_proof']) if sample_stats['word_count_proof'] is not None else None
                sample_stats['tree'] = 1

                for name, count in sample_stats.items():
                    if count is None:
                        continue
                    sample_cum_stats[name] += count

                for name, count in sample_stats.items():
                    if name.find('argument') >= 0 or name.find('translation') >= 0:
                        continue
                    if count is None:
                        continue
                    all_sample_stats[name].append(count)

                sample_avg_stats = {
                    name: count / sample_cum_stats['tree']
                    for name, count in sample_cum_stats.items()
                    if name != 'tree'
                }

                sample_std_stats = {
                    name: stdev(count_list) if len(count_list) >= 2 else None
                    for name, count_list in all_sample_stats.items()
                }

                gathered_stats = flatten_dict({'cum': sample_cum_stats, 'avg': sample_avg_stats, 'std': sample_std_stats})
            else:
                gathered_stats = {}

            i_sample += 1
            yield dataset_json,\
                proof_tree,\
                formula_distractors,\
                translation_distractors,\
                gathered_stats

    def _sample_proof_stance(self) -> ProofStance:
        if random.random() < self.unknown_ratio:
            return ProofStance.UNKNOWN
        else:
            if random.random() < 1 / 2.:
                return ProofStance.PROVED
            else:
                return ProofStance.DISPROVED

    def _make_text(self,

                   proof_tree: ProofTree,
                   proof_stance: ProofStance,

                   dead_leaf_nodes: Optional[List[ProofNode]] = None,
                   missing_leaf_nodes: Optional[List[ProofNode]] = None,
                   collapsed_leaf_nodes: Optional[List[ProofNode]] = None,

                   node2id: Optional[Dict[Node, str]] = None,
                   id2node: Optional[Dict[str, Node]] = None,

                   formula_distractors: Optional[List[Formula]] = None,
                   translation_distractors: Optional[List[str]] = None,

                   add_randome_sentence_if_context_is_null=False,
                   conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=True,
                   conclude_hypothesis_from_random_sent_if_proof_is_unknown=False) -> Tuple[str, Optional[str], Dict[Node, str], Dict[str, Node]]:

        dead_leaf_nodes = dead_leaf_nodes or []
        missing_leaf_nodes = missing_leaf_nodes or []
        collapsed_leaf_nodes = collapsed_leaf_nodes or []
        if set(dead_leaf_nodes) != set(missing_leaf_nodes).union(collapsed_leaf_nodes):
            raise ValueError()

        formula_distractors = formula_distractors or []
        translation_distractors = translation_distractors or []

        transformed_proof_nodes = self._identify_transformed_proof_nodes(
            proof_tree,
            dead_leaf_nodes,
            missing_leaf_nodes,
            collapsed_leaf_nodes,
        )

        transformed_proof_and_distractor_nodes: List[Node] = list(transformed_proof_nodes)\
            + [_FormulaDistractorNode(distractor) for distractor in formula_distractors]\
            + [_TranslationDistractorNode(distractor_translation) for distractor_translation in translation_distractors]

        if len(transformed_proof_and_distractor_nodes) == 0:
            if add_randome_sentence_if_context_is_null:
                random_sentence = None
                if self.pipeline.translator is not None:
                    random_sentence = _generate_random_sentence(self.pipeline.translator)
                random_sentence = random_sentence or _DUMMY_SENTENCE
                transformed_proof_and_distractor_nodes = [_FormulaDistractorNode(Formula(random_sentence))]
                logger.info('Adding a random sentence into context because context have no sentence. The randome sentence is: "%s"', random_sentence)
            else:
                raise NotImplementedError('We must add something to context because null context will lead to error in NLProofS learning.')

        node2id, id2node = self._make_node_ids(
            transformed_proof_and_distractor_nodes,
            proof_tree,
            node2id=node2id,
            id2node=id2node,
        )

        def _my_make_context_text(formula_rep: bool) -> str:
            return self._make_context_text(id2node, missing_leaf_nodes, formula_rep=formula_rep)

        def _my_make_proof_text(formula_rep: bool) -> str:
            return self._make_proof_text(
                proof_tree,
                transformed_proof_and_distractor_nodes,
                transformed_proof_nodes,
                node2id,
                id2node,
                proof_stance,
                conclude_hypothesis_from_subtree_roots_if_proof_is_unknown,
                conclude_hypothesis_from_random_sent_if_proof_is_unknown,
                formula_rep=formula_rep,
            )

        context_text = _my_make_context_text(False)
        formula_context_text = _my_make_context_text(True)

        proof_text = _my_make_proof_text(False)
        formula_proof_text = _my_make_proof_text(True)

        return (
            context_text,
            formula_context_text,
            proof_text,
            formula_proof_text,
            node2id,
            id2node,
        )

    def _divide_into_missing_and_collapsed_nodes(self, dead_leaf_nodes: List[ProofNode]) -> Tuple[List[ProofNode], List[ProofNode]]:
        missing_leaf_nodes = []
        collapsed_leaf_nodes = []

        for dead_node in dead_leaf_nodes:
            if self.use_collapsed_translation_nodes_for_unknown_tree:
                if random.random() <= 0.5 and dead_node.formula.translation is not None:
                    try:
                        collapased_translations = self.word_swap_distractor.generate(
                            [dead_node.formula.translation],
                            1,
                            best_effort=False,
                        )
                        collapased_translation = collapased_translations[0]
                        logger.info('Make collapsed translation node as:\norig     : "%s"\ncollapsed: "%s"', dead_node.formula.translation, collapased_translation)
                        dead_node.formula.translation = collapased_translation
                        if dead_node.formula.translation_name is not None:
                            dead_node.formula.translation_name = dead_node.formula.translation_name + '.collapsed'

                        collapsed_leaf_nodes.append(dead_node)
                    except TranslationDistractorGenerationFailure:
                        logger.warning('Could not collapse the translation "%s". Will be treated as missing nodes.', dead_node.formula.translation)
                        missing_leaf_nodes.append(dead_node)
                else:
                    missing_leaf_nodes.append(dead_node)
            else:
                missing_leaf_nodes.append(dead_node)

        return missing_leaf_nodes, collapsed_leaf_nodes

    def _identify_transformed_proof_nodes(self,
                                          proof_tree: ProofTree,
                                          dead_leaf_nodes: List[ProofNode],
                                          missing_leaf_nodes: List[ProofNode],
                                          collapsed_leaf_nodes: List[ProofNode]) -> List[Node]:
        transformed_proof_nodes: List[Node] = []
        dead_nodes = copy.copy(dead_leaf_nodes)
        missinge_nodes = copy.copy(missing_leaf_nodes)
        collapsed_nodes = copy.copy(collapsed_leaf_nodes)
        for node in proof_tree.depth_first_traverse():
            if self._is_root(node, proof_tree) or self._is_int(node, proof_tree):
                # add children
                for child_node in node.children:
                    if child_node in dead_nodes:
                        if child_node in missinge_nodes:
                            continue
                        elif child_node in collapsed_nodes:
                            if child_node not in transformed_proof_nodes:
                                transformed_proof_nodes.append(child_node)
                        else:
                            raise Exception()
                    else:
                        if child_node not in transformed_proof_nodes:
                            transformed_proof_nodes.append(child_node)

                # add the parent
                if any(child in dead_nodes for child in node.children):
                    # if a child is dead, then the parent will be also dead.
                    dead_nodes.append(node)
                    missinge_nodes.append(node)
                else:
                    transformed_proof_nodes.append(node)
        return transformed_proof_nodes

    def _make_node_ids(self,
                       transformed_proof_and_distractor_nodes: List[Node],
                       proof_tree: ProofTree,
                       node2id: Optional[Dict[Node, str]] = None,
                       id2node: Optional[Dict[str, Node]] = None) -> Tuple[Dict[Node, str], Dict[str, Node]]:
        node2id = node2id or {}
        id2node = id2node or {}

        # build node ids
        i_sent = 1
        i_assump = 1

        _node2id: Dict[Node, str] = {}
        _id2node: Dict[str, Node] = {}
        for node in transformed_proof_and_distractor_nodes:
            for already_mapped_node, already_mapped_node_id in node2id.items():
                if _is_identical_node(node, already_mapped_node):
                    _node2id[node] = already_mapped_node_id
                    _id2node[already_mapped_node_id] = node

        for node in random.sample(transformed_proof_and_distractor_nodes, len(transformed_proof_and_distractor_nodes)):
            if self._is_int(node, proof_tree):
                continue
            if node in _node2id:
                continue

            while True:

                if self._is_root(node, proof_tree):
                    id_ = 'hypothesis'

                elif self._is_assump(node):
                    id_ = f'assump{i_assump}'
                    i_assump += 1

                elif self._is_leaf(node, proof_tree):
                    id_ = f'sent{i_sent}'
                    i_sent += 1

                elif self._is_distractor(node):
                    id_ = f'sent{i_sent}'
                    i_sent += 1

                else:
                    raise Exception()

                if id_ == 'hypothesis' or id_ not in id2node:
                    break

            _node2id[node] = id_
            _id2node[id_] = node

        i_int = 1
        for node in proof_tree.depth_first_traverse():
            if node not in transformed_proof_and_distractor_nodes:
                continue
            if not self._is_int(node, proof_tree):
                continue
            if node in _node2id:
                continue

            while True:
                id_ = f'int{i_int}'
                i_int += 1

                if id_ not in id2node:
                    break

            _node2id[node] = id_
            _id2node[id_] = node

        return _node2id, _id2node

    def _make_context_text(self,
                           id2node: Dict[str, Node],
                           missing_leaf_nodes: List[ProofNode],
                           formula_rep=False) -> str:
        context_id2nodes = {id_: node for id_, node in id2node.items()
                            if id_.startswith('sent') and node not in missing_leaf_nodes}

        def node2sent(node) -> str:
            if formula_rep:
                if isinstance(node, _TranslationDistractorNode):
                    return self._get_sent_from_node(node)
                else:
                    return node.formula.rep
            else:
                return self._get_sent_from_node(node)

        return ' '.join([
            f'{id_}: {node2sent(node)}'
            for id_, node in sorted(context_id2nodes.items(),
                                    key=lambda id_node: int(re.sub('sent([0-9]*)', r'\g<1>', id_node[0])))

        ])

    def _make_proof_text(self,
                         proof_tree: ProofTree,
                         transformed_proof_and_distractor_nodes: List[Node],
                         transformed_proof_nodes: List[Node],
                         node2id: Dict[Node, str],
                         id2node: Dict[str, Node],
                         proof_stance: ProofStance,
                         conclude_hypothesis_from_subtree_roots_if_proof_is_unknown: bool,
                         conclude_hypothesis_from_random_sent_if_proof_is_unknown: bool,
                         formula_rep=False) -> Optional[str]:
        # make proof string
        proof_elems = []
        for node in proof_tree.depth_first_traverse():
            if node not in transformed_proof_and_distractor_nodes:
                continue

            if self._is_root(node, proof_tree):
                assump_ids = [node2id[assump_child] for assump_child in node.assump_children]
                child_ids = [node2id[child] for child in node.children]
                premise_str = ' & '.join([f'[{_id}]' for _id in assump_ids] + child_ids)
                conclusion_str = 'hypothesis'

            elif self._is_assump(node):
                premise_str = 'void'
                assump_id = node2id[node]
                if formula_rep:
                    conclusion_str = f'{assump_id}: {node.formula.rep}'
                else:
                    conclusion_str = f'{assump_id}: {self._get_sent_from_node(node)}'

            elif self._is_leaf(node, proof_tree):
                continue

            elif self._is_int(node, proof_tree):
                node_id = node2id[node]
                assump_ids = [node2id[assump_child] for assump_child in node.assump_children]
                child_ids = [node2id[child] for child in node.children]
                premise_str = ' & '.join([f'[{_id}]' for _id in assump_ids] + child_ids)
                if formula_rep:
                    conclusion_str = f'{node_id}: {node.formula.rep}'
                else:
                    conclusion_str = f'{node_id}: {self._get_sent_from_node(node)}'

            elif self._is_distractor(node):
                continue
            else:
                raise Exception()

            proof_text = ' -> '.join([premise_str, conclusion_str])

            proof_elems.append(proof_text)

        if proof_stance == ProofStance.UNKNOWN:
            if conclude_hypothesis_from_subtree_roots_if_proof_is_unknown and conclude_hypothesis_from_random_sent_if_proof_is_unknown:
                raise ValueError()

            if conclude_hypothesis_from_subtree_roots_if_proof_is_unknown:

                subtree_root_nodes: List[Node] = []
                for node in transformed_proof_nodes:
                    _is_root = True

                    for other_node in transformed_proof_nodes:
                        if other_node == node:
                            continue

                        if node in other_node.descendants:
                            _is_root = False
                            break

                    if _is_root:
                        subtree_root_nodes.append(node)

                # We do not consider leaf nodes.
                # Since ther are indistinguishable from formula_distractors, the prover can not specify them.
                subtree_root_nodes_wo_leaf = [node
                                              for node in subtree_root_nodes
                                              if not self._is_leaf(node, proof_tree)]

                if len(subtree_root_nodes_wo_leaf) == 0:
                    sent_ids = [id_ for id_ in id2node.keys() if id_.startswith('sent')]
                    hypothesis_premises = random.sample(sent_ids, 1)
                else:
                    hypothesis_premises = [node2id[node] for node in subtree_root_nodes_wo_leaf]

                proof_elems.append(' & '.join(hypothesis_premises) + ' -> hypothesis')

            elif conclude_hypothesis_from_random_sent_if_proof_is_unknown:

                sent_ids = [id_ for id_ in id2node.keys() if id_.startswith('sent')]
                hypothesis_premises = random.sample(sent_ids, 1)
                proof_elems.append(' & '.join(hypothesis_premises) + ' -> hypothesis')

            if len(proof_elems) > 0 and proof_elems[-1].find('void ->') >= 0:
                # if the final step of proof for unknown is "void -> assump"
                # it does not have enought context to deducu such step.
                # Thus, we exclude the step.
                proof_elems = proof_elems[:-1]

        if len(proof_elems) == 0:
            return None
        else:
            return '; '.join(proof_elems) + ';'

    def _is_root(self, node: Node, proof_tree: ProofTree) -> bool:
        return isinstance(node, ProofNode) and node == proof_tree.root_node

    def _is_leaf(self, node: Node, proof_tree: ProofTree) -> bool:
        return isinstance(node, ProofNode) and node.is_leaf

    def _is_assump(self, node: Node) -> bool:
        return isinstance(node, ProofNode) and node.is_assump

    def _is_int(self, node: Node, proof_tree: ProofTree) -> bool:
        return isinstance(node, ProofNode)\
            and (not self._is_root(node, proof_tree) and not self._is_leaf(node, proof_tree) and not self._is_assump(node))

    def _is_distractor(self, node: Node) -> bool:
        return isinstance(node, _DistractorFakeNode)

    def _get_sent_from_node(self, node: Node) -> str:
        if isinstance(node, ProofNode):
            text = node.formula.translation or node.formula.rep
        else:
            text = node.translation
        return text
