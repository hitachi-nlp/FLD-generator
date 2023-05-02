from typing import List, Optional, Tuple, Dict, Any, Set
import logging
from collections import defaultdict

from FLD.formula import Formula, NEGATION, eliminate_double_negation
from FLD.proof import ProofTree, ProofNode
from FLD.proof_tree_generators import ProofTreeGenerator
from FLD.formula_distractors import FormulaDistractor
from FLD.translators.base import Translator
from FLD.utils import flatten_dict
from FLD.exception import FormalLogicExceptionBase
from FLD.proof_tree_generators import ProofTreeGenerationFailure
from FLD.formula_distractors import FormulaDistractorGenerationFailure, NegativeTreeDistractor
from FLD.translation_distractors import TranslationDistractor
from FLD.translators import TranslationFailure
from FLD.utils import make_pretty_msg
import kern_profiler

logger = logging.getLogger(__name__)


class ProofTreeGenerationPipelineFailure(FormalLogicExceptionBase):
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
        self.translator.log_stats = log_stats

        self._empty_argument_stat = {arg.id: 0 for arg in self.generator.arguments}
        self._empty_translation_stat = {name: 0 for name in self.translator.translation_names}

    @profile
    def run(self,
            depth: int,
            branch_extension_steps: int,
            num_distractors: int,
            num_translation_distractors: int,
            depth_1_reference_weight: Optional[float] = None,
            force_fix_illegal_unconditioned_constants=False,
            raise_if_translation_not_found=True) -> Tuple[ProofTree, Formula, Optional[List[Formula]], List[str], Dict[str, Any], Dict[str, int]]:
        others = {}

        if not self.generator.disallow_contradiction_as_hypothesis:
            raise ValueError('generator.disallow_contradiction_as_hypothesis must be "Ture" since we need the negated hypothesis for ')

        if depth < 1:
            raise ValueError('depth must be >= 1')

        def _make_pretty_log(title: str, status: str) -> str:
            return make_pretty_msg(title=title, status=status, boundary_level=4)

        while True:
            logger.info(_make_pretty_log('generate proof tree', 'start'))
            try:
                proof_tree = self.generator.generate_tree(
                    depth,
                    branch_extension_steps,
                    depth_1_reference_weight=depth_1_reference_weight,
                    force_fix_illegal_unconditioned_constants=force_fix_illegal_unconditioned_constants,
                )
            except ProofTreeGenerationFailure as e:
                raise ProofTreeGenerationPipelineFailure(str(e))
            logger.info(_make_pretty_log('generate proof tree', 'finish'))

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            logger.info(_make_pretty_log('generate distractors', 'start'))
            is_formula_distractor_failed = False
            if num_distractors > 0:
                if self.distractor is not None:
                    try:
                        formula_distractors, _others = self.distractor.generate(proof_tree, num_distractors)
                        for _other_key, _other_val in _others.items():
                            if _other_key in others:
                                raise ValueError(f'Duplicated other key {_other_key}')
                            others[_other_key] = _other_val

                    except FormulaDistractorGenerationFailure as e:
                        is_formula_distractor_failed = True
                        if self.fallback_from_formula_to_translation_distractor:
                            logger.warning('formula distractor %s failed in generating distractors. will fallback to generate distractors by translation distractors.',
                                           str(self.distractor))
                            formula_distractors = []
                        else:
                            raise ProofTreeGenerationPipelineFailure(str(e))
                else:
                    raise ValueError('could not generate distractors since distractor was not specified in the constructor.')
            else:
                formula_distractors = []
            logger.info(_make_pretty_log('generate distractors', 'finish'))

            root_negation_formula = Formula(f'{NEGATION}({proof_tree.root_node.formula.rep})')
            if self.generator.elim_dneg:
                root_negation_formula = eliminate_double_negation(root_negation_formula)

            if self.translator is not None:
                logger.info(_make_pretty_log('generate translations', 'start'))
                all_formulas = [node.formula for node in proof_tree.nodes] + [root_negation_formula]  + formula_distractors
                leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
                assump_formula_indices = [i for i, node in enumerate(proof_tree.nodes) if node.assump_parent is not None]

                other_formulas = []
                if others.get('negative_tree', None) is not None:
                    negative_tree = others['negative_tree']
                    other_formulas = [node.formula for node in negative_tree.nodes]
                all_formulas = all_formulas + [formula for formula in other_formulas if formula not in all_formulas]

                try:
                    named_translations, translator_stats = self.translator.translate(
                        all_formulas,
                        list(proof_tree.unconditioned_constants),
                        raise_if_translation_not_found=raise_if_translation_not_found,
                    )
                except TranslationFailure as e:
                    raise ProofTreeGenerationPipelineFailure(str(e))

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
                    try:
                        translation_distractors: List[str] = self.translation_distractor.generate(leaf_translations, _num_translation_distractors)
                    except FormulaDistractorGenerationFailure as e:
                        raise ProofTreeGenerationPipelineFailure(str(e))
                else:
                    raise ValueError('could not generate translation distractors since translation distractor was not specified in the constructor.')
            else:
                translation_distractors = []
            logger.info(_make_pretty_log('generate translation distractors', 'finish'))

            if self.log_stats:
                stats = self._get_stats(proof_tree, formula_distractors, translator_stats)
            else:
                stats = {}

            return proof_tree, root_negation_formula, formula_distractors, translation_distractors, others, stats

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
            translation_name = node.formula.translation_name if node.formula.translation_name is not None else '<no_name>'
            if translation_name not in stats['translation_stats']['name_stats']:
                stats['translation_stats']['name_stats'][translation_name] = 0
            stats['translation_stats']['name_stats'][translation_name] += 1

        for key, val in flatten_dict(translator_stats).items():
            stats['translation_stats']['other_stats'][key] = val

        return stats
