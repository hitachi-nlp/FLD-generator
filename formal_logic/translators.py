import json
from typing import List, Dict, Optional
from abc import abstractmethod, ABC
import random

from formal_logic import Formula
from formal_logic.proof import ProofTree
from formal_logic.replacements import generate_replacement_mappings_from_formula, replace_formula


class Translator(ABC):

    @abstractmethod
    def translate(self, formulas: List[Formula]) -> List[Optional[str]]:
        pass


class SentenceTranslator(Translator):

    def __init__(self, sentence_translations: Dict[str, List[str]]):
        self._sentence_translations = sentence_translations

    def translate(self, formulas: List[Formula]) -> List[Optional[str]]:
        translations = []
        for formula in formulas:

            done_translation = False
            for trans_formula_rep, trans_nls in self._sentence_translations.items():
                if len(trans_nls) == 0:
                    continue

                trans_formula = Formula(trans_formula_rep)
                for mapping in generate_replacement_mappings_from_formula([trans_formula],
                                                                          [formula],
                                                                          allow_negation=False):
                    trans_formula_replaced = replace_formula(trans_formula, mapping)
                    if trans_formula_replaced.rep == formula.rep:
                        trans_nl = random.choice(trans_nls)
                        translations.append(replace_formula(Formula(trans_nl), mapping).rep)
                        done_translation = True

            if not done_translation:
                translations.append(None)

        return translations


def load_sentence_translation_config(path: str) -> Dict[str, Dict[str, List]]:
    return json.load(open(path))


def add_translations_to_tree(tree: ProofTree, translator: Translator) -> None:
    translations = translator.translate([node.formula for node in tree.nodes])
    for node, translation in zip(tree.nodes, translations):
        node.formula.translation = translation
