import random
from enum import Enum
from abc import abstractmethod, ABC
from statistics import mean, stdev
from typing import Dict, List, Optional, Union, Iterable, Tuple, Any
import logging
import copy
from collections import defaultdict
from pprint import pprint

from FLNL.word_banks import POS, VerbForm, AdjForm, NounForm, WordForm, ATTR
from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.formula import Formula
from FLNL.proof import ProofTree, ProofNode
from FLNL.utils import flatten_dict
from FLNL.translators.base import Translator
from FLNL.word_banks.base import WordBank
from FLNL.translation_distractors import build as build_translation_distractor
import kern_profiler

logger = logging.getLogger(__name__)


class ProofStance(Enum):
    PROOF = 'PROOF'
    DISPROOF = 'DISPROOF'
    UNKNOWN = 'UNKNOWN'


class WorldAssumption(Enum):
    CWA = 'CWA'
    OWA = 'OWA'


def _generate_random_sentence(translator: Translator):
    acceptable_formula_reps = translator.acceptable_formulas
    for formula_rep in random.sample(acceptable_formula_reps, len(acceptable_formula_reps)):
        nls, _ = translator.translate([Formula(formula_rep)])
        if nls[0][1] is not None:
            return nls[0][1]
    return 'Love Love LoveLive!'


def _make_instance_label(proof_stance: ProofStance, world_assump: WorldAssumption) -> Union[bool, str]:
    if world_assump == WorldAssumption.CWA:
        if proof_stance == ProofStance.PROOF:
            return True
        elif proof_stance == ProofStance.DISPROOF:
            return False
        elif proof_stance == ProofStance.UNKNOWN:
            return False
        else:
            raise ValueError()
    elif world_assump == WorldAssumption.OWA:
        if proof_stance == ProofStance.PROOF:
            return True
        elif proof_stance == ProofStance.DISPROOF:
            return False
        elif proof_stance == ProofStance.UNKNOWN:
            return 'Unknown'
        else:
            raise ValueError()
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
        self.formula = distractor

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


class NLProofSDataset:

    def __init__(self,
                 pipeline: ProofTreeGenerationPipeline,
                 proof_stances: List[str],
                 world_assump: str,
                 depths: List[int],
                 branch_extension_steps: List[int],
                 unknown_ratio: float = 1 / 3.,
                 use_collapsed_translation_nodes_for_unknown_tree=False,
                 word_bank: Optional[WordBank] = None,
                 num_distractors: Optional[List[int]] = None,
                 num_translation_distractors: Optional[List[int]] = None,
                 log_stats=False,
                 raise_if_translation_not_found=True):
        self.pipeline = pipeline

        self.proof_stances = [ProofStance(proof_stance) for proof_stance in proof_stances]
        self.world_assump = WorldAssumption(world_assump)
        self.unknown_ratio = unknown_ratio

        if len(depths) == 0:
            raise ValueError()
        self.depths = depths
        self.branch_extension_steps = branch_extension_steps
        self.num_distractors = num_distractors or [0]
        self.num_translation_distractors = num_translation_distractors or [0]
        self.log_stats = log_stats,
        self.pipeline.log_stats = log_stats
        self.raise_if_translation_not_found = raise_if_translation_not_found

        self.use_collapsed_translation_nodes_for_unknown_tree = use_collapsed_translation_nodes_for_unknown_tree
        if self.use_collapsed_translation_nodes_for_unknown_tree:
            self.word_swap_distractor = build_translation_distractor('word_swap', word_bank=word_bank)
        else:
            self.word_swap_distractor = None

    @profile
    def generate(self,
                 size: int,
                 conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=True,
                 add_randome_sentence_if_context_is_null=True) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]], List[str], Dict[str, Any]]]:
        """ Generate dataset

        See discussions.md for the options.
        """
        def is_root(node: Node) -> bool:
            return isinstance(node, ProofNode) and node == proof_tree.root_node

        def is_leaf(node: Node) -> bool:
            return isinstance(node, ProofNode) and node in proof_tree.leaf_nodes

        def is_assump(node: Node) -> bool:
            return node.assump_parent is not None

        def is_int(node: Node) -> bool:
            return isinstance(node, ProofNode) and (not is_root(node) and not is_leaf(node))

        def is_distractor(node: Node) -> bool:
            return isinstance(node, _DistractorFakeNode)

        def _get_sent_from_node(node: Node) -> str:
            if isinstance(node, ProofNode):
                return node.formula.translation or node.formula.rep
            else:
                return node.translation

        sample_cum_stats = defaultdict(int)
        all_sample_stats = defaultdict(list)
        for i_sample in range(size):
            depth = random.sample(self.depths, 1)[0]
            # generate a proof tree
            _num_distractors = random.sample(self.num_distractors, 1)[0]
            _num_translation_distractors = random.sample(self.num_translation_distractors, 1)[0]
            _branch_extension_steps = random.sample(self.branch_extension_steps, 1)[0]
            proof_tree, root_negation_formula, formula_distractors, translation_distractors, pipeline_stats = self.pipeline.run(
                depth,
                _branch_extension_steps,
                _num_distractors,
                _num_translation_distractors,
                raise_if_translation_not_found=self.raise_if_translation_not_found,
            )

            if random.random() < self.unknown_ratio:
                proof_stance = ProofStance.UNKNOWN
                hypothesis = _get_sent_from_node(proof_tree.root_node)
                dead_leaf_nodes = random.sample(proof_tree.leaf_nodes,
                                                max(1, int(len(proof_tree.leaf_nodes) * 0.2)))
            else:
                if random.random() < 1 / 2.:
                    proof_stance = ProofStance.PROOF
                    hypothesis = _get_sent_from_node(proof_tree.root_node)
                    dead_leaf_nodes = []
                else:
                    proof_stance = ProofStance.DISPROOF
                    hypothesis = root_negation_formula.translation or root_negation_formula.translation.rep
                    dead_leaf_nodes = []

            missing_leaf_nodes = []
            collapsed_leaf_nodes = []
            for dead_node in dead_leaf_nodes:
                if self.use_collapsed_translation_nodes_for_unknown_tree:
                    if random.random() <= 0.5 and dead_node.formula.translation is not None:
                        collapased_translations = self.word_swap_distractor.generate(
                            [dead_node.formula.translation],
                            1,
                        )

                        if len(collapased_translations) == 0:
                            logger.warning('Could not collapse the translation "%s". Will be treated as missing nodes.', dead_node.formula.translation)
                            missing_leaf_nodes.append(dead_node)
                        else:
                            collapased_translation = collapased_translations[0]
                            logger.info('Make collapsed translation node as:\norig     : "%s"\ncollapsed: "%s"', dead_node.formula.translation, collapased_translation)
                            dead_node.formula.translation = collapased_translation
                            if dead_node.formula.translation_name is not None:
                                dead_node.formula.translation_name = dead_node.formula.translation_name + '.collapsed'

                            collapsed_leaf_nodes.append(dead_node)
                    else:
                        missing_leaf_nodes.append(dead_node)
                else:
                    missing_leaf_nodes.append(dead_node)

            # indentify nodes in proof
            nodes_in_proof: List[Node] = []
            dead_nodes = copy.copy(dead_leaf_nodes)
            missinge_nodes = copy.copy(missing_leaf_nodes)
            collapsed_nodes = copy.copy(collapsed_leaf_nodes)
            for node in proof_tree.depth_first_traverse():
                if not is_root(node) or is_int(node):
                    # add children
                    for child_node in node.children:
                        if child_node in dead_nodes:
                            if child_node in missinge_nodes:
                                continue
                            elif child_node in collapsed_nodes:
                                if child_node not in nodes_in_proof:
                                    nodes_in_proof.append(child_node)
                            else:
                                raise Exception()
                        else:
                            if child_node not in nodes_in_proof:
                                nodes_in_proof.append(child_node)

                    # add the parent
                    if any(child in dead_nodes for child in node.children):
                        # if a child is dead, then the parent will be also dead.
                        dead_nodes.append(node)
                        missinge_nodes.append(node)
                    else:
                        nodes_in_proof.append(node)

            all_nodes: List[Node] = list(nodes_in_proof)\
                + [_FormulaDistractorNode(distractor) for distractor in formula_distractors]\
                + [_TranslationDistractorNode(distractor_translation) for distractor_translation in translation_distractors]
            if len(all_nodes) == 0:
                if add_randome_sentence_if_context_is_null:
                    random_sentence = _generate_random_sentence(self.pipeline.translator)
                    all_nodes = [_FormulaDistractorNode(Formula(random_sentence))]
                    logger.info('Adding a random sentence into context since context have no sentence. The randome sentence is: "%s"', random_sentence)
                else:
                    raise NotImplementedError('We must add something to context since null context will lead to error in NLProofS learning.')

            # build node ids
            i_sent = 1
            i_assump = 1
            node2id = {}
            id2node = {}
            for node in random.sample(all_nodes, len(all_nodes)):
                if is_root(node):
                    id_ = 'hypothesis'
                elif is_leaf(node):
                    if is_assump(node):
                        id_ = f'assump{i_assump}'
                        i_assump += 1
                    else:
                        id_ = f'sent{i_sent}'
                        i_sent += 1
                elif is_int(node):
                    continue
                elif is_distractor(node):
                    id_ = f'sent{i_sent}'
                    i_sent += 1
                else:
                    raise Exception()
                node2id[node] = id_
                id2node[id_] = node

            i_int = 1
            for node in proof_tree.depth_first_traverse():
                if node not in all_nodes:
                    continue

                if is_int(node):
                    id_ = f'int{i_int}'
                    i_int += 1
                    node2id[node] = id_
                    id2node[id_] = node

            context = ' '.join([
                f'{id_}: {_get_sent_from_node(node)}'
                for id_, node in id2node.items()
                if id_.startswith('sent') and node not in missing_leaf_nodes
            ])

            # make proof string
            proof_elems = []
            for node in proof_tree.depth_first_traverse():
                if node not in all_nodes:
                    continue

                if is_root(node):
                    assump_ids = [node2id[assump_child] for assump_child in node.assump_children]
                    child_ids = [node2id[child] for child in node.children]
                    premise_str = ' & '.join([f'[{_id}]' for _id in assump_ids] + child_ids)
                    conclusion_str = 'hypothesis'
                elif is_leaf(node):
                    if is_assump(node):
                        premise_str = 'void'
                        assump_id = node2id[node]
                        conclusion_str = f'{assump_id}: {_get_sent_from_node(node)}'
                    else:
                        continue
                elif is_int(node):
                    node_id = node2id[node]
                    assump_ids = [node2id[assump_child] for assump_child in node.assump_children]
                    child_ids = [node2id[child] for child in node.children]
                    premise_str = ' & '.join([f'[{_id}]' for _id in assump_ids] + child_ids)
                    conclusion_str = f'{node_id}: {_get_sent_from_node(node)}'
                elif is_distractor(node):
                    continue
                else:
                    raise Exception()
                proof_str = ' -> '.join([premise_str, conclusion_str])

                proof_elems.append(proof_str)

            if proof_stance == ProofStance.UNKNOWN and conclude_hypothesis_from_subtree_roots_if_proof_is_unknown:
                subtree_root_nodes: List[Node] = []
                for node in nodes_in_proof:
                    _is_root = True

                    for other_node in nodes_in_proof:
                        if other_node == node:
                            continue

                        if node in other_node.descendants:
                            _is_root = False
                            break

                    if _is_root:
                        subtree_root_nodes.append(node)

                # We do not consider leaf nodes.
                # Since ther are indistinguishable from formula_distractors, the prover can not specify them.
                subtree_root_nodes_wo_leaf = [node for node in subtree_root_nodes if not is_leaf(node)]

                if len(subtree_root_nodes_wo_leaf) == 0:
                    # XXX: we fixed this to avoid making sent1 too frequent.
                    # rare case but possible when all the subtrees are leaf
                    # in that case, we use sent1 as a proxy.
                    # node_ids = ['sent1']

                    sent_ids = [id_ for id_ in id2node.keys() if id_.startswith('sent')]
                    node_ids = random.sample(sent_ids, 1)
                else:
                    node_ids = [node2id[node] for node in subtree_root_nodes_wo_leaf]
                proof_elems.append(' & '.join(node_ids) + ' -> hypothesis')

            proof_str = '; '.join(proof_elems) + ';'
            proof_strs = [proof_str]  # only one proof in our dataset

            # make output json
            label = _make_instance_label(proof_stance, self.world_assump)
            dataset_json = {
                'hypothesis': hypothesis,
                'context': context,
                'proofs': proof_strs,

                'proof_stance': proof_stance.value,
                'answer': label,

                'original_tree_depth': proof_tree.depth,

                # I have no idea how to define depth from the root when proof is incomplete.
                'depth': None if proof_stance == ProofStance.UNKNOWN else proof_tree.depth,

                'num_formula_distractors': len(formula_distractors),
                'num_translation_distractors': len(translation_distractors),
                'num_all_distractors': len(formula_distractors) + len(translation_distractors),
            }

            # Update statistics
            if self.log_stats:
                sample_stats = flatten_dict(pipeline_stats)
                sample_stats[f'answer.{label}'] = 1
                sample_stats[f'proof_stance.{proof_stance.value}'] = 1
                sample_stats['word_count_hypothesis'] = len(hypothesis.split(' '))
                sample_stats['word_count_context'] = len(context.split(' '))
                sample_stats['word_count_proof'] = mean([len(proof_str.split(' ')) for proof_str in proof_strs])
                sample_stats['word_count_all'] = sample_stats['word_count_hypothesis'] + sample_stats['word_count_context'] + sample_stats['word_count_proof']
                sample_stats['tree'] = 1

                for name, count in sample_stats.items():
                    sample_cum_stats[name] += count

                for name, count in sample_stats.items():
                    if name.find('argument') >= 0 or name.find('translation') >= 0:
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

            yield dataset_json,\
                proof_tree,\
                formula_distractors,\
                translation_distractors,\
                gathered_stats
