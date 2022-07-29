import random
import json
from typing import Dict, List, Optional

from formal_logic import Formula
from formal_logic.proof import ProofTree
from formal_logic.replacements import generate_replacement_mappings_from_formula, replace_formula


def translate_sentence(formula,
                       sentence_translations: Dict[str, List[str]]) -> Optional[str]:
    for trans_formula_rep, trans_nls in sentence_translations.items():
        if len(trans_nls) == 0:
            continue

        trans_formula = Formula(trans_formula_rep)
        for mapping in generate_replacement_mappings_from_formula([trans_formula],
                                                                  [formula],
                                                                  allow_negation=False):
            trans_formula_replaced = replace_formula(trans_formula, mapping)
            if trans_formula_replaced.rep == formula.rep:
                trans_nl = random.choice(trans_nls)
                return replace_formula(Formula(trans_nl), mapping).rep
    return None


def add_sentence_translations_to_tree(tree: ProofTree,
                                      sentence_translations: Dict[str, List[str]]) -> None:
    for node in tree.nodes:
        node.formula.translation = translate_sentence(node.formula, sentence_translations)


def load_sentence_translation_config(path: str) -> Dict[str, Dict[str, List]]:
    return json.load(open(path))
