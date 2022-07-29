import random
from typing import Dict, List, Optional

from formal_logic import Formula
from formal_logic.proof import ProofTree
from formal_logic.replacements import generate_replacement_mappings_from_formula, replace_formula


def translate_sentence(formula,
                       sentence_translations: Dict[Formula, List[str]]) -> Optional[str]:
    for trans_formula, trans_nls in sentence_translations.items():
        for mapping in generate_replacement_mappings_from_formula([trans_formula],
                                                                  [formula],
                                                                  allow_negation=False):
            trans_formula_replaced = replace_formula(trans_formula, mapping)
            if trans_formula_replaced.rep == formula.rep:
                trans_nl = random.choice(trans_nls)
                return replace_formula(Formula(trans_nl), mapping).rep
    return None


def add_sentence_translations_to_tree(tree: ProofTree,
                                      sentence_translations: Dict[Formula, List[str]]) -> None:
    for node in tree.nodes:
        node.formula.translation = translate_sentence(node.formula, sentence_translations)

