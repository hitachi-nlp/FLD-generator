from typing import List, Optional, Tuple, Dict, Any, Set
import logging
from collections import defaultdict

from FLNL.formula import Formula, NEGATION, eliminate_double_negation
from FLNL.proof import ProofTree, ProofNode
from FLNL.proof_tree_generators import ProofTreeGenerator
from FLNL.formula_distractors import FormulaDistractor
from FLNL.translators.base import Translator
from FLNL.utils import flatten_dict
from FLNL.exception import FormalLogicExceptionBase
from FLNL.proof_tree_generators import ProofTreeGenerationFailure
from FLNL.formula_distractors import FormulaDistractorGenerationFailure
from FLNL.translators import TranslationFailure
import kern_profiler

logger = logging.getLogger(__name__)


class ProofTreeGenerationPipelineFailure(FormalLogicExceptionBase):
    pass


class ProofTreeGenerationPipeline:

    def __init__(self,
                 generator: ProofTreeGenerator,
                 distractor: Optional[FormulaDistractor] = None,
                 translator: Optional[Translator] = None,
                 add_subj_obj_swapped_distractor=False,
                 log_stats=False):
        self.generator = generator
        self.distractor = distractor
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
            raise_if_translation_not_found=True) -> Tuple[ProofTree, Formula, Optional[List[Formula]], Dict[str, int]]:

        if not self.generator.disallow_contradiction_as_hypothesis:
            raise ValueError('generator.disallow_contradiction_as_hypothesis must be "Ture" since we need the negated hypothesis for ')

        if depth < 1:
            raise ValueError('depth must be >= 1')

        while True:
            logger.info('========================== generating proof tree... ============================')
            try:
                proof_tree = self.generator.generate_tree(depth, branch_extension_steps)
            except ProofTreeGenerationFailure as e:
                raise ProofTreeGenerationPipelineFailure(str(e))
            logger.info('========================== generating proof tree done! ============================')

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            logger.info('========================== generating distractor... ============================')
            if self.distractor is not None:
                try:
                    distractor_formulas = self.distractor.generate(proof_tree, num_distractors)
                except FormulaDistractorGenerationFailure as e:
                    raise ProofTreeGenerationPipelineFailure(str(e))
            else:
                distractor_formulas = []
            logger.info('========================== generating distractor done! ============================')

            root_negation_formula = Formula(f'{NEGATION}({proof_tree.root_node.formula.rep})')
            if self.generator.elim_dneg:
                root_negation_formula = eliminate_double_negation(root_negation_formula)

            if self.translator is not None:
                logger.info('========================== translating... ============================')
                all_formulas = [node.formula for node in proof_tree.nodes] + [root_negation_formula]  + distractor_formulas
                leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
                assump_formula_indices = [i for i, node in enumerate(proof_tree.nodes) if node.assump_parent is not None]

                try:
                    named_translations, translator_stats = self.translator.translate(all_formulas,
                                                                                     raise_if_translation_not_found=raise_if_translation_not_found)
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
                        distractor_formulas.append(SO_swap_formula)
                    
                logger.info('========================== translating done! ============================')

            if self.log_stats:
                stats = self._get_stats(proof_tree, distractor_formulas, translator_stats)
            else:
                stats = {}

            return proof_tree, root_negation_formula, distractor_formulas, stats

    def _get_stats(self,
                   proof_tree: ProofTree,
                   distractor_formulas: List[Formula],
                   translator_stats: Dict[str, int]) -> Dict[str, int]:
        stats = {
            'tree_stats': {},
            'distractor': len(distractor_formulas),
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
