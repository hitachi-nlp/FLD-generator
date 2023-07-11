from typing import List, Optional, Tuple, Dict, Any, Set
import logging
from collections import defaultdict
import random

from FLD_generator.formula import Formula, NEGATION, eliminate_double_negation
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
                 add_subj_obj_swapped_distractor=False,
                 log_stats=False):
        self.generator = generator
        self.distractor = distractor
        self.translation_distractor = translation_distractor
        self.fallback_from_formula_to_translation_distractor = fallback_from_formula_to_translation_distractor
        self.translator = translator
        self.add_subj_obj_swapped_distractor = add_subj_obj_swapped_distractor

        self.log_stats = log_stats
        self._empty_argument_stat = {arg.id: 0 for arg in self.generator.arguments}

        if self.translator is not None:
            self.translator.log_stats = log_stats
            self._empty_translation_stat = {name: 0 for name in self.translator.translation_names}
        else:
            self._empty_translation_stat = {}

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
            raise_if_translation_not_found=True) -> Tuple[ProofTree, Formula, Optional[List[Formula]], List[str], Dict[str, Any], Dict[str, int]]:
        misc = {}

        if not self.generator.disallow_contradiction_as_hypothesis:
            raise ValueError('generator.disallow_contradiction_as_hypothesis must be "Ture" since we need the negated hypothesis for ')

        if depth < 1:
            raise ValueError('depth must be >= 1')

        def _make_pretty_log(title: str, status: str) -> str:
            return make_pretty_msg(title=title, status=status, boundary_level=4)

        while True:
            logger.info(_make_pretty_log('generate proof tree', 'start'))
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
            logger.info(_make_pretty_log('generate proof tree', 'finish'))

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            logger.info(_make_pretty_log('generate distractors', 'start'))
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
            logger.info(_make_pretty_log('generate distractors', 'finish'))

            root_negation_formula = Formula(f'{NEGATION}({proof_tree.root_node.formula.rep})')
            if self.generator.elim_dneg:
                root_negation_formula = eliminate_double_negation(root_negation_formula)

            translator_stats = {}
            if self.translator is not None:
                logger.info(_make_pretty_log('generate translations', 'start'))
                all_formulas = [node.formula for node in proof_tree.nodes] + [root_negation_formula]  + formula_distractors
                leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
                assump_formula_indices = [i for i, node in enumerate(proof_tree.nodes) if node.is_assump]

                other_formulas = []
                all_negative_tree_attrs = [val for name, val in misc.items()
                                           if name.find('negative_tree') >= 0]
                for negative_tree_attrs in all_negative_tree_attrs:
                    other_formulas += [node.formula for node in negative_tree_attrs['tree'].nodes]
                all_formulas = all_formulas + [formula for formula in other_formulas if formula not in all_formulas]

                try:
                    named_translations, translator_stats = self.translator.translate(
                        all_formulas,
                        list(proof_tree.intermediate_constants),
                        raise_if_translation_not_found=raise_if_translation_not_found,
                    )
                except TranslationFailure as e:
                    raise ProofTreeGenerationPipelineFailure(str(e))
                except TranslationImpossible as e:
                    raise ProofTreeGenerationPipelineImpossible(str(e))

                for i_formula, (formula, (translation_name, translation, SO_swap_formula)) in enumerate(zip(all_formulas, named_translations)):
                    formula.translation_name = translation_name
                    if i_formula in assump_formula_indices:
                        translation_prefix = 'let\'s assume that '
                    else:
                        translation_prefix = ''

                    if translation is not None:
                        formula.translation = translation_prefix + translation

                    if self.add_subj_obj_swapped_distractor and formula in leaf_formulas and SO_swap_formula is not None:
                        logger.info('adding subj obj swapped distractor: "%s"', SO_swap_formula.translation)
                        formula_distractors.append(SO_swap_formula)
                logger.info(_make_pretty_log('generate translations', 'finish'))

            logger.info(_make_pretty_log('generate translation distractors', 'start'))
            if num_translation_distractors > 0 or (self.fallback_from_formula_to_translation_distractor and is_formula_distractor_failed):
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
            logger.info(_make_pretty_log('generate translation distractors', 'finish'))

            if self.log_stats:
                stats = self._get_stats(proof_tree, formula_distractors, translator_stats)
            else:
                stats = {}

            return proof_tree, root_negation_formula, formula_distractors, translation_distractors, misc, stats

    def _get_stats(self,
                   proof_tree: ProofTree,
                   formula_distractors: List[Formula],
                   translator_stats: Dict[str, int]) -> Dict[str, int]:
        stats = {
            'tree_stats': {},
            'distractor': len(formula_distractors),
            'argument_stats': self._empty_argument_stat.copy(),
            'translation_stats': {
                'name_stats': self._empty_translation_stat.copy(),
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
