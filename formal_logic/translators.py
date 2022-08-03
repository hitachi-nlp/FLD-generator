import json
from typing import List, Dict, Optional, Set
from abc import abstractmethod, ABC
from collections import OrderedDict
import random
import re

from .formula import Formula
from .proof import ProofTree
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    replace_formula,
)


class Translator(ABC):

    @abstractmethod
    def translate(self, formulas: List[Formula]) -> List[Optional[str]]:
        pass


class SentenceWiseTranslator(Translator):

    def __init__(self,
                 sentence_translations: Dict[str, List[str]],
                 predicate_translations: Optional[List[str]] = None,
                 constant_translations: Optional[List[str]] = None,
                 translate_terms=True):

        def num_terms(formula_rep: str) -> int:
            formula = Formula(formula_rep)
            return len(formula.predicates) + len(formula.constants) + len(formula.variables)

        self._sentence_translations = OrderedDict()
        for formula, translations in sorted(sentence_translations.items(),
                                            key=lambda formula_trans: num_terms(formula_trans[0])):
            # sort by "complexity" of the formulas
            # We want first match to simple = constrained formulas first.
            # e.g.) We want matched to "Fa & Fb" first, rather than general "Fa & Gb"
            self._sentence_translations[formula] = translations
        self.predicate_translations = predicate_translations
        self.constant_translations = constant_translations
        self.translate_terms = translate_terms

    def translate(self, formulas: List[Formula]) -> List[Optional[str]]:
        translations = []

        # sentence translation
        for formula in formulas:

            done_translation = False
            for trans_formula_rep, trans_nls in self._sentence_translations.items():
                if len(trans_nls) == 0:
                    continue

                trans_formula = Formula(trans_formula_rep)
                for mapping in generate_replacement_mappings_from_formula([trans_formula], [formula]):
                    trans_formula_replaced = replace_formula(trans_formula, mapping)
                    if trans_formula_replaced.rep == formula.rep:
                        trans_nl = random.choice(trans_nls)
                        translations.append(replace_formula(Formula(trans_nl), mapping).rep)
                        done_translation = True

            if not done_translation:
                translations.append(None)

        # term translation
        if self.translate_terms:
            term_mappings = generate_replacement_mappings_from_terms(
                list(set([predicate.rep for formula in formulas for predicate in formula.predicates])),
                list(set([constant.rep for formula in formulas for constant in formula.constants])),
                self.predicate_translations,
                self.constant_translations,
                shuffle=True
            )
            term_mapping = next(term_mappings)
            for i_formula, (formula, translation) in enumerate(zip(formulas, translations)):
                if translation is not None:
                    translations[i_formula] = replace_formula(Formula(translation), term_mapping).rep
                    print('[translated]:', translations[i_formula])
                else:
                    print('[no translation]', formula.rep)

        return translations


class IterativeRegexpTranslator(Translator):
    """ sample implementation of regexp matching """

    def __init__(self):
        pass

    def translate(self, formulas: List[Formula]) -> List[Optional[str]]:
        translations = {
            '\({A} v {B}\)x': [
                'someone is {A} and {B}'
            ],
            '{A}x': [
                'someone is {A}',
                'he is {A}',
                'she is {A}',
            ],
            '\(x\): (.*) -> (.*)': [
                'if \g<1>, then \g<2>'
            ],
        }
        translations = OrderedDict([
            (k, v) for k, v in sorted(translations.items(),
                                      key=lambda k_v: len(k_v[0]))
        ][::-1])

        translated_reps = []
        for formula in formulas:
            translated_formula = Formula(formula.rep)

            has_translation = True
            while has_translation:
                has_translation = False
                for i_translation, (src_rep, tgt_reps) in enumerate(translations.items()):
                    tgt_rep = random.choice(tgt_reps)

                    src_formula = Formula(src_rep)
                    tgt_formula = Formula(tgt_rep)

                    for mapping in generate_replacement_mappings_from_formula([src_formula], [formula]):
                        src_formula_replaced = replace_formula(src_formula, mapping)
                        tgt_formula_replaced = replace_formula(tgt_formula, mapping)
                        if re.search(src_formula_replaced.rep, translated_formula.rep) is not None:
                            translated_formula = Formula(re.sub(src_formula_replaced.rep, tgt_formula_replaced.rep, translated_formula.rep))
                            has_translation = True
                            break

            translated_reps.append(translated_formula.rep)

        return translated_reps
