from typing import List, Optional, Tuple, Dict, Any, Set
import logging
from collections import defaultdict
import random
import copy

from FLD_generator.formula import Formula, NEGATION, eliminate_double_negation, negate
from FLD_generator.proof import ProofTree, ProofNode
from FLD_generator.proof_tree_generators import ProofTreeGenerator
from FLD_generator.formula_distractors import FormulaDistractor
from FLD_generator.translators.base import Translator
from FLD_generator.utils import flatten_dict
from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.proof_tree_generators import ProofTreeGenerationFailure, ProofTreeGenerationImpossible
from FLD_generator.formula_distractors import FormulaDistractorGenerationFailure, FormulaDistractorGenerationImpossible, NegativeTreeDistractor
from FLD_generator.translation_distractors import TranslationDistractor, TranslationDistractorGenerationFailure, TranslationDistractorGenerationImpossible
from FLD_generator.translators import TranslationFailure, TranslationImpossible
from FLD_generator.utils import make_pretty_msg
import line_profiling

logger = logging.getLogger(__name__)


class ProofTreeGenerationPipelineFailure(FormalLogicExceptionBase):
    pass


class ProofTreeGenerationPipelineImpossible(FormalLogicExceptionBase):
    pass


class ProofTreeGenerationPipeline:

    def __init__(self,
                 generator: ProofTreeGenerator,
                 distractor: Optional[FormulaDistractor] = None,
                 translation_distractor: Optional[TranslationDistractor] = None,
                 fallback_from_formula_to_translation_distractor=False,
                 translator: Optional[Translator] = None,
                 assumption_prefix='Let\'s assume that ',
                 add_subj_obj_swapped_distractor=False,
                 # knowledge_translator: Optional[Translator] = None,
                 knowledge_range: Optional[Tuple[float, float]] = None,
                 collapsed_knowledge_range: Optional[Tuple[float, float]] = None,
                 log_stats=False):
        self.generator = generator
        self.distractor = distractor
        self.translation_distractor = translation_distractor
        self.fallback_from_formula_to_translation_distractor = fallback_from_formula_to_translation_distractor
        self.translator = translator
        self.add_subj_obj_swapped_distractor = add_subj_obj_swapped_distractor
        self.assumption_prefix = assumption_prefix

        self.log_stats = log_stats
        self._empty_argument_stat = {arg.id: 0 for arg in self.generator.arguments}

        if self.translator is not None:
            self.translator.log_stats = log_stats
            self._empty_translation_stat = {name: 0 for name in self.translator.translation_names}
        else:
            self._empty_translation_stat = {}

        self._knowledge_range = (
            None if knowledge_range is not None and tuple(knowledge_range) == (0.0, 0.0)
            else knowledge_range)
        self._collapsed_knowledge_range = (
            None if collapsed_knowledge_range is not None and tuple(collapsed_knowledge_range) == (0.0, 0.0)
            else collapsed_knowledge_range)
        # self._knowledge_translator = knowledge_translator

        self._reusable_proof_trees: Dict[Tuple[Any], List[ProofTree]] = defaultdict(list)

    @profile
    def _reusable_generate(self,
                           depth: int,
                           branch_extension_steps: int,
                           allow_inconsistency=False,
                           allow_smaller_proofs=False,
                           depth_1_reference_weight: Optional[float] = None,
                           force_fix_illegal_intermediate_constants=False) -> ProofTree:

        def _get_cache_key(_depth: int) -> Tuple:
            return (_depth, allow_inconsistency, allow_smaller_proofs, depth_1_reference_weight, force_fix_illegal_intermediate_constants)

        reusable_proof_trees = self._reusable_proof_trees[_get_cache_key(depth)]
        if len(reusable_proof_trees) > 0:
            idx = random.randint(0, len(reusable_proof_trees) - 1)
            reusable_proof_tree = reusable_proof_trees[idx]
            reusable_proof_trees.pop(idx)
            return reusable_proof_tree

        trial_proof_trees = self.generator.generate_tree(
            depth,
            branch_extension_steps,
            depth_1_reference_weight=depth_1_reference_weight,
            allow_inconsistency=allow_inconsistency,
            allow_smaller_proofs=allow_smaller_proofs,
            best_effort=True,
            force_fix_illegal_intermediate_constants=force_fix_illegal_intermediate_constants,
            get_all_trial_results=True,
        )
        for tree in trial_proof_trees:
            tree.validate()

        trial_proof_trees = sorted(trial_proof_trees, key= lambda proof_tree: proof_tree.depth)
        to_be_cached_trees, to_be_return_tree = trial_proof_trees[:-1], trial_proof_trees[-1]

        for to_be_cached_tree in to_be_cached_trees:
            self._reusable_proof_trees[_get_cache_key(to_be_cached_tree.depth)].append(to_be_cached_tree)
            if len(self._reusable_proof_trees[_get_cache_key(to_be_cached_tree.depth)]) > 100000:  # max cache size
                self._reusable_proof_trees[_get_cache_key(to_be_cached_tree.depth)] = []

        return to_be_return_tree

    @profile
    def run(self,
            depth: int,
            branch_extension_steps: int,
            num_distractors: int,
            num_translation_distractors: int,
            allow_inconsistency=False,
            allow_smaller_proofs=False,
            depth_1_reference_weight: Optional[float] = None,
            force_fix_illegal_intermediate_constants=False,
            translation_variants_per_logic=1,
            raise_if_translation_not_found=True) -> List[Tuple[ProofTree, Formula, Optional[List[Formula]], List[str], Dict[str, Any], Dict[str, int]]]:

        if not self.generator.disallow_contradiction_as_hypothesis:
            raise ValueError('generator.disallow_contradiction_as_hypothesis must be "Ture" since we need the negated hypothesis for ')

        if depth < 1:
            raise ValueError('depth must be >= 1')

        while True:
            logic =\
                self._build_logic(
                    depth,
                    branch_extension_steps,
                    num_distractors,
                    allow_inconsistency=allow_inconsistency,
                    allow_smaller_proofs=allow_smaller_proofs,
                    depth_1_reference_weight=depth_1_reference_weight,
                    force_fix_illegal_intermediate_constants=force_fix_illegal_intermediate_constants
                )
            if logic is None:
                logger.info('tree not generated. Will retry.')
                continue
            proof_tree, root_negation_formula, formula_distractors, is_formula_distractor_failed, misc = logic

            variants = []
            for i_variant in range(translation_variants_per_logic):
                logger.info('================== creating variant=%d from the logic =================', i_variant)
                proof_tree_var = proof_tree.copy()
                root_negation_formula_var = copy.deepcopy(root_negation_formula)
                formula_distractors_var = copy.deepcopy(formula_distractors)
                is_formula_distractor_failed_var = copy.copy(is_formula_distractor_failed)
                misc_var = copy.deepcopy(misc)

                translator_stats_var = self._add_translations(
                    proof_tree_var,
                    root_negation_formula_var,
                    formula_distractors_var,
                    misc_var,
                    raise_if_translation_not_found=raise_if_translation_not_found,
                )

                translation_distractors_var = self._build_translation_distractors(
                    proof_tree_var,
                    num_translation_distractors,
                    is_formula_distractor_failed_var,
                    num_distractors,
                )

                if self.log_stats:
                    stats_var = self._get_stats(proof_tree_var, formula_distractors_var, translator_stats_var)
                else:
                    stats_var = {}

                variants.append((
                    proof_tree_var,
                    root_negation_formula_var,
                    formula_distractors_var,
                    translation_distractors_var,
                    misc_var,
                    stats_var,
                ))

            return variants

    @profile
    def _build_logic(self,
                     depth: int,
                     branch_extension_steps: int,
                     num_distractors: int,
                     allow_inconsistency=False,
                     allow_smaller_proofs=False,
                     depth_1_reference_weight: Optional[float] = None,
                     force_fix_illegal_intermediate_constants=False)\
            -> Optional[Tuple[ProofTree, Formula, List[Formula], bool, Dict[str, Any]]]:
        misc = {}

        logger.info(self._make_pretty_log('generate proof tree', 'start'))
        try:
            proof_tree = self._reusable_generate(
                depth,
                branch_extension_steps,
                depth_1_reference_weight=depth_1_reference_weight,
                allow_inconsistency=allow_inconsistency,
                allow_smaller_proofs=allow_smaller_proofs,
                force_fix_illegal_intermediate_constants=force_fix_illegal_intermediate_constants,
            )
        except ProofTreeGenerationFailure as e:
            raise ProofTreeGenerationPipelineFailure(str(e))
        except ProofTreeGenerationImpossible as e:
            raise ProofTreeGenerationPipelineImpossible(str(e))
        logger.info(self._make_pretty_log('generate proof tree', 'finish'))

        if proof_tree is None:
            return None

        # root_negation_formula = Formula(f'{NEGATION}({proof_tree.root_node.formula.rep})')
        root_negation_formula = negate(proof_tree.root_node.formula)
        if self.generator.elim_dneg:
            root_negation_formula = eliminate_double_negation(root_negation_formula)

        logger.info(self._make_pretty_log('generate distractors', 'start'))
        is_formula_distractor_failed = False
        if num_distractors > 0:
            if self.distractor is not None:
                try:
                    formula_distractors, _misc = self.distractor.generate(proof_tree,
                                                                          num_distractors,
                                                                          allow_inconsistency=allow_inconsistency,
                                                                          allow_smaller_proofs=allow_smaller_proofs,
                                                                          best_effort=True)
                    for _misc_key, _misc_val in _misc.items():
                        if _misc_key in misc:
                            raise ValueError(f'Duplicated misc key {_misc_key}')
                        misc[_misc_key] = _misc_val

                except (FormulaDistractorGenerationFailure, FormulaDistractorGenerationImpossible) as e:
                    is_formula_distractor_failed = True
                    logger.warning('formula distractor %s failed in generating distractors due to the following error. :\n%s',
                                   str(self.distractor), str(e))
                    formula_distractors = []
            else:
                raise ValueError('could not generate distractors since distractor was not specified in the constructor.')
        else:
            formula_distractors = []
        logger.info(self._make_pretty_log('generate distractors', 'finish'))

        return proof_tree, root_negation_formula, formula_distractors, is_formula_distractor_failed, misc

    @profile
    def _add_translations(self,
                          proof_tree: ProofTree,
                          root_negation_formula: Formula,
                          formula_distractors: List[Formula],
                          misc: Dict[str, Any],
                          raise_if_translation_not_found=True) -> Dict[str, Any]:
        translator_stats = {}
        if self.translator is not None:
            logger.info(self._make_pretty_log('generate translations', 'start'))
            tree_nodes, tree_formulas = proof_tree.nodes, [node.formula for node in proof_tree.nodes]
            leaf_nodes, leaf_formulas = proof_tree.leaf_nodes, [node.formula for node in proof_tree.leaf_nodes]
            assump_formula_indices = [i for i, node in enumerate(tree_nodes) if node.is_assump]

            all_formulas = tree_formulas + [root_negation_formula]  + formula_distractors
            other_formulas = []
            all_negative_tree_attrs = [val for name, val in misc.items()
                                       if name.find('negative_tree') >= 0]
            for negative_tree_attrs in all_negative_tree_attrs:
                other_formulas += [node.formula for node in negative_tree_attrs['tree'].nodes]
            all_formulas = all_formulas + [formula for formula in other_formulas if formula not in all_formulas]

            knowledge_idxs: List[int] = []
            collapsed_knowledge_idxs: List[int] = []
            if self._knowledge_range is not None:
                knowledge_candidate_formulas = [formula for formula in leaf_formulas
                                                if self.translator.is_knowledge_translatable(formula)]

                def sample_num(num_max: int, ratio_lower: int, ratio_upper: int) -> float:
                    ratio = ratio_lower + random.random() * (ratio_upper - ratio_lower)
                    return int((num_max + 0.99) * ratio)  # add 0.99 to sample the maximum equally to others

                num_all_knowledge = sample_num(len(knowledge_candidate_formulas), *self._knowledge_range)
                if num_all_knowledge > 0:
                    all_knowledge_formulas = random.sample(knowledge_candidate_formulas, num_all_knowledge)

                    if self._collapsed_knowledge_range is not None:
                        num_collapsed_knowledge = sample_num(num_all_knowledge, *self._collapsed_knowledge_range)
                    else:
                        num_collapsed_knowledge = 0

                    if num_collapsed_knowledge > 0:
                        collapsed_knowledge_formulas = random.sample(all_knowledge_formulas, num_collapsed_knowledge)
                        knowledge_formulas = [formula for formula in all_knowledge_formulas
                                              if formula not in collapsed_knowledge_formulas]
                    else:
                        collapsed_knowledge_formulas = []
                        knowledge_formulas = all_knowledge_formulas

                    for idx, formula in enumerate(tree_formulas):
                        if formula in knowledge_formulas:
                            knowledge_idxs.append(idx)
                        elif formula in collapsed_knowledge_formulas:
                            collapsed_knowledge_idxs.append(idx)

            try:
                named_translations, translator_stats = self.translator.translate(
                    all_formulas,
                    list(proof_tree.intermediate_constants),
                    knowledge_idxs=knowledge_idxs,
                    collapsed_knowledge_idxs=collapsed_knowledge_idxs,
                    raise_if_translation_not_found=raise_if_translation_not_found,
                )
            except TranslationFailure as e:
                raise ProofTreeGenerationPipelineFailure(str(e))
            except TranslationImpossible as e:
                raise ProofTreeGenerationPipelineImpossible(str(e))

            for i_formula, (formula, (translation_name, translation, SO_swap_formula, knowledge_type)) in enumerate(zip(all_formulas, named_translations)):

                formula.translation_name = translation_name
                if i_formula in assump_formula_indices:
                    translation_prefix = self.assumption_prefix
                else:
                    translation_prefix = ''

                if translation is not None:
                    if translation_prefix:
                        formula.translation = translation_prefix + translation[0] + translation[1:]
                    else:
                        try:
                            formula.translation = translation[0].upper() + translation[1:]
                        except IndexError as e:
                            logger.critical('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                            logger.critical('translation: %s', translation)
                            if translation == "":
                                logger.warning('translation is "", which is not expected. Should be debugged.'
                                               'Currently we leave it and is just using other successful samples.')
                            else:
                                raise 

                    if knowledge_type is not None:
                        knowledge_injected_node = [node for node in proof_tree.nodes if node.formula == formula][0]
                        knowledge_injected_node.knowledge_type = knowledge_type
                        logger.info('%s is injected to a node: %s', knowledge_type, str(knowledge_injected_node))

                if self.add_subj_obj_swapped_distractor and formula in leaf_formulas and SO_swap_formula is not None:
                    logger.info('adding subj obj swapped distractor: "%s"', SO_swap_formula.translation)

                    formula_distractors.append(SO_swap_formula)

            logger.info(self._make_pretty_log('generate translations', 'finish'))

        return translator_stats

    @profile
    def _build_translation_distractors(self,
                                       proof_tree: ProofTree,
                                       num_translation_distractors: int,
                                       is_formula_distractor_failed: bool,
                                       num_distractors: int,) -> List[Formula]:
        logger.info(self._make_pretty_log('generate translation distractors', 'start'))
        if num_translation_distractors > 0\
                or (self.fallback_from_formula_to_translation_distractor and is_formula_distractor_failed):
            if (self.fallback_from_formula_to_translation_distractor and is_formula_distractor_failed):
                _num_translation_distractors = num_translation_distractors + num_distractors
                logger.info('try to generate %d + %d distractors by translation distractor. The latter is due to that the formula distractor failed.',
                            num_translation_distractors, num_distractors)

            else:
                _num_translation_distractors = num_translation_distractors

            if self.translation_distractor is not None:
                leaf_translations = [leaf_node.formula.translation for leaf_node in proof_tree.leaf_nodes
                                     if leaf_node.formula.translation is not None]
                if len(leaf_translations) == 0:
                    logger.info('can not generate translation distractors because no leaf translations found')
                    translation_distractors = []
                else:
                    try:
                        translation_distractors: List[str] = self.translation_distractor.generate(leaf_translations, _num_translation_distractors, best_effort=True)
                    except TranslationDistractorGenerationFailure as e:
                        raise ProofTreeGenerationPipelineFailure(str(e))
                    except TranslationDistractorGenerationImpossible as e:
                        raise ProofTreeGenerationPipelineImpossible(str(e))
            else:
                raise ValueError('could not generate translation distractors since translation distractor was not specified in the constructor.')
        else:
            translation_distractors = []
        logger.info(self._make_pretty_log('generate translation distractors', 'finish'))
        return translation_distractors

    def _get_stats(self,
                   proof_tree: ProofTree,
                   formula_distractors: List[Formula],
                   translator_stats: Dict[str, int]) -> Dict[str, int]:
        stats = {
            'tree_stats': {},
            'distractor': len(formula_distractors),
            'argument_stats': self._empty_argument_stat.copy(),
            'translation_stats': {
                # 'name_stats': self._empty_translation_stat.copy(),
                'name_stats': {},
                'other_stats': defaultdict(int),
            },
        }

        # tree stats
        def get_node_formulas(node: Optional[ProofNode]) -> Set[Formula]:
            formulas = set([])

            if node is None:
                pass
            else:
                formulas.add(node.formula)
                if node.argument is None:
                    pass
                else:
                    formulas = formulas.union(set(node.argument.all_formulas))
            return formulas

        num_formulas = len({
            formula
            for node in proof_tree.nodes
            for formula in list(get_node_formulas(node))
        })
        num_leaf_formulas = len({
            formula
            for node in proof_tree.leaf_nodes
            for formula in list(get_node_formulas(node))
        })
        stats['tree'] = {
            'node': len(proof_tree.nodes),
            'node_leaf': len(proof_tree.leaf_nodes),
            'node_non_leaf': len(proof_tree.nodes) - len(proof_tree.leaf_nodes),

            'formula': num_formulas,
            'formula_leaf': num_leaf_formulas,
            'formula_non_leaf': num_formulas - num_leaf_formulas,

            'depth': proof_tree.depth,
        }

        # arguments
        for node in proof_tree.nodes:
            if node.argument is not None:
                stats['argument_stats'][node.argument.id] += 1

        # translation
        for node in proof_tree.nodes:
            if node.formula.translation_name is not None:
                translation_name = node.formula.translation_name
                if translation_name not in stats['translation_stats']['name_stats']:
                    stats['translation_stats']['name_stats'][translation_name] = 0
                stats['translation_stats']['name_stats'][translation_name] += 1

        for key, val in flatten_dict(translator_stats).items():
            stats['translation_stats']['other_stats'][key] = val

        return stats

    def _make_pretty_log(self, title: str, status: str) -> str:
        return make_pretty_msg(title=title, status=status, boundary_level=4)
