from typing import List, Optional, Tuple, Dict, Any, Set
import logging
from collections import defaultdict

from formal_logic.formula import Formula
from formal_logic.proof import ProofTree, ProofNode
from formal_logic.proof_tree_generators import ProofTreeGenerator
from formal_logic.distractors import FormalLogicDistractor
from formal_logic.translators import Translator
from formal_logic.utils import flatten_dict
import kern_profiler

logger = logging.getLogger(__name__)


class ProofTreeGenerationPipeline:

    def __init__(self,
                 generator: ProofTreeGenerator,
                 distractor: Optional[FormalLogicDistractor] = None,
                 translator: Optional[Translator] = None):
        self.generator = generator
        self.distractor = distractor
        self.translator = translator

        self._empty_argument_stat = {arg.id: 0 for arg in self.generator.arguments}
        self._empty_translation_stat = {name: 0 for name in self.translator.translation_names}

    @profile
    def run(self,
            depth: int,
            max_leaf_extensions: int,
            raise_if_translation_not_found=True) -> Tuple[ProofTree, Optional[List[Formula]], Dict[str, int]]:
        while True:
            logger.info('========================== generating proof tree... ============================')
            proof_tree = self.generator.generate_tree(depth, max_leaf_extensions)
            logger.info('========================== generating proof tree done! ============================')

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            logger.info('========================== generating distractor... ============================')
            if self.distractor is not None:
                distractor_formulas = self.distractor.generate(proof_tree)
            else:
                distractor_formulas = []
            logger.info('========================== generating distractor done! ============================')

            if self.translator is not None:
                logger.info('========================== translating... ============================')
                named_translations, translator_stats = self.translator.translate([node.formula for node in proof_tree.nodes] + distractor_formulas,
                                                                                 raise_if_translation_not_found=raise_if_translation_not_found)
                for i_node, node in enumerate(proof_tree.nodes):
                    node.formula.translation_name, node.formula.translation = named_translations[i_node]
                for i_distractor, distractor_formula in enumerate(distractor_formulas):
                    distractor_formula.translation_name, distractor_formula.translation = named_translations[len(proof_tree.nodes) + i_distractor]
                logger.info('========================== translating done! ============================')

            return proof_tree, distractor_formulas, self._get_stats(proof_tree, translator_stats)

    def _get_stats(self,
                   proof_tree: ProofTree,
                   translator_stats: Dict[str, int]) -> Dict[str, int]:
        stats = {
            'arguments': self._empty_argument_stat.copy(),
            'translation': {
                'names': self._empty_translation_stat.copy(),
                'others': defaultdict(int),
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
        tree_stats = {
            'nodes': len(proof_tree.nodes),
            'nodes_leaf': len(proof_tree.leaf_nodes),
            'nodes_non_leaf': len(proof_tree.nodes) - len(proof_tree.leaf_nodes),

            'formulas': num_formulas,
            'formulas_leaf': num_leaf_formulas,
            'formulas_non_leaf': num_formulas - num_leaf_formulas,

            'depth': proof_tree.depth,
        }
        stats['tree'] = tree_stats

        # argument & translation stats
        for node in proof_tree.nodes:
            if node.argument is not None:
                stats['arguments'][node.argument.id] += 1

            translation_name = node.formula.translation_name if node.formula.translation_name is not None else '<no_name>'
            if translation_name not in stats['translation']['names']:
                stats['translation']['names'][translation_name] = 0
            stats['translation']['names'][translation_name] += 1

        for key, val in flatten_dict(translator_stats).items():
            stats['translation']['others'][key] = val

        return stats
