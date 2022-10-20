import json
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict
import random
import logging

from FLNL.formula import Formula

from FLNL.interpretation import (
    generate_mappings_from_formula,
    generate_mappings_from_predicates_and_constants,
    interprete_formula,
)
from .base import (
    Translator,
    TranslationNotFoundError,
    calc_formula_specificity,
)

logger = logging.getLogger(__name__)


class SentenceWiseTranslator(Translator):
    """Translator compatible with ./configs/FLNL/sentence_translations/syllogistic_corpus-02.json"""

    def __init__(self,
                 sentence_translations: Dict[str, List[str]],
                 predicate_translations: Optional[List[str]] = None,
                 constant_translations: Optional[List[str]] = None,
                 do_translate_to_nl=True,
                 log_stats=False):
        super().__init__(log_stats=log_stats)

        self._sentence_translations = OrderedDict()
        for formula, translations in sorted(
            sentence_translations.items(),
            key=lambda formula_trans: (calc_formula_specificity(Formula(formula_trans[0]), formula_trans[0]))
        )[::-1]:
            # sort by "complexity" of the formulas
            # We want first match to simple = constrained formulas first.
            # e.g.) We want matched to "Fa & Fb" first, rather than general "Fa & Gb"
            self._sentence_translations[formula] = translations
        self.predicate_translations = predicate_translations
        self.constant_translations = constant_translations
        self.do_translate_to_nl = do_translate_to_nl

    def _translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:
        translations = []

        # sentence translation
        for formula in formulas:

            done_translation = False
            for trans_formula_rep, trans_nls in self._sentence_translations.items():
                if len(trans_nls) == 0:
                    continue

                trans_formula = Formula(trans_formula_rep)
                for mapping in generate_mappings_from_formula([trans_formula], [formula]):
                    trans_formula_pulled = interprete_formula(trans_formula, mapping)
                    if trans_formula_pulled.rep == formula.rep:
                        trans_nl = random.choice(trans_nls)
                        translations.append(interprete_formula(Formula(trans_nl), mapping).rep)
                        done_translation = True

            if not done_translation:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation not found for "{formula.rep}"')
                else:
                    logger.info('translation not found for "%s"', formula.rep)
                    translations.append(None)

        if self.do_translate_to_nl:
            interp_mappings = generate_mappings_from_predicates_and_constants(
                list(set([predicate.rep for formula in formulas for predicate in formula.predicates])),
                list(set([constant.rep for formula in formulas for constant in formula.constants])),
                self.predicate_translations,
                self.constant_translations,
                shuffle=True,
            )
            interp_mapping = next(interp_mappings)
            for i_formula, (formula, translation) in enumerate(zip(formulas, translations)):
                if translation is not None:
                    translations[i_formula] = interprete_formula(Formula(translation), interp_mapping).rep

        return [(None, translation) for translation in translations], {}
