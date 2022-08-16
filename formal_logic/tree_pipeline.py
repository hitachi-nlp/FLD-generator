from typing import List, Optional, Tuple, Dict, Any
import logging
from collections import defaultdict

from formal_logic.formula import Formula
from formal_logic.proof import ProofTree
from formal_logic.generators import FormalLogicGenerator
from formal_logic.distractors import FormalLogicDistractor
from formal_logic.translators import Translator
from formal_logic.utils import flatten_dict

logger = logging.getLogger(__name__)


class TreePipeline:

    def __init__(self,
                 generator: FormalLogicGenerator,
                 distractor: Optional[FormalLogicDistractor] = None,
                 translator: Optional[Translator] = None):
        self.generator = generator
        self.distractor = distractor
        self.translator = translator

    def run(self,
            depth: int = 5,
            raise_if_translation_not_found=True) -> Tuple[ProofTree, Optional[List[Formula]], Dict[str, int]]:
        while True:
            proof_tree = self.generator.generate_tree(depth=depth)

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            if self.distractor is not None:
                distractors = self.distractor.generate([node.formula for node in proof_tree.nodes])
            else:
                distractors = []

            if self.translator is not None:
                named_translations, translator_stats = self.translator.translate([node.formula for node in proof_tree.nodes] + distractors,
                                                                                 raise_if_translation_not_found=raise_if_translation_not_found)
                for i_node, node in enumerate(proof_tree.nodes):
                    node.formula.translation_name, node.formula.translation = named_translations[i_node]
                for i_distractor, distractor_formula in enumerate(distractors):
                    distractor_formula.translation_name, distractor_formula.translation = named_translations[len(proof_tree.nodes) + i_distractor]

            return proof_tree, distractors, self._get_stats(proof_tree, translator_stats)

    def _get_stats(self,
                   proof_tree: ProofTree,
                   translator_stats: Dict[str, int]) -> Dict[str, int]:
        stats = {
            'arguments': defaultdict(int),
            'translation': {
                'names': defaultdict(int),
                'others': defaultdict(int),
            },
        }
        for node in proof_tree.nodes:
            if node.argument is not None:
                stats['arguments'][node.argument.id] += 1
            translation_name = node.formula.translation_name if node.formula.translation_name is not None else '<no_name>'
            stats['translation']['names'][translation_name] += 1

        for key, val in flatten_dict(translator_stats).items():
            stats['translation']['others'][key] = val

        return stats
