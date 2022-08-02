from typing import List, Optional, Tuple
import logging

from formal_logic.formula import Formula
from formal_logic.proof import ProofTree
from formal_logic.generators import FormalLogicGenerator
from formal_logic.distractors import FormalLogicDistractor
from formal_logic.translators import Translator

logger = logging.getLogger(__name__)


class TreePipeline:

    def __init__(self,
                 generator: FormalLogicGenerator,
                 distractor: Optional[FormalLogicDistractor] = None,
                 translator: Optional[Translator] = None):
        self.generator = generator
        self.distractor = distractor
        self.translator = translator

    def run(self, depth: int = 5, num_distractors: int = 5) -> Tuple[ProofTree, Optional[List[Formula]]]:
        while True:
            proof_tree = self.generator.generate_tree(depth=depth)

            if proof_tree is None:
                logger.info('tree not generated. Will retry.')
                continue

            if self.distractor is not None:
                distractors = self.distractor.generate([node.formula for node in proof_tree.nodes], num_distractors)
            else:
                distractors = []

            if self.translator is not None:
                translations = self.translator.translate([node.formula for node in proof_tree.nodes] + distractors)
                for i_node, node in enumerate(proof_tree.nodes):
                    node.formula.translation = translations[i_node]
                for i_distractor, distractor_formula in enumerate(distractors):
                    distractor_formula.translation = translations[len(proof_tree.nodes) + i_distractor]

            return proof_tree, distractors
