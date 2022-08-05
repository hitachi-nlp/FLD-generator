import json
from typing import List, Dict, Optional, Tuple
from abc import abstractmethod, ABC
from collections import OrderedDict, defaultdict
import random
import re
import logging
from pprint import pprint

from .formula import Formula, CONSTANTS
from .word_banks.base import WordBank
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    replace_formula,
)
from .word_banks import POS, VerbForm
from .exception import FormalLogicExceptionBase

logger = logging.getLogger(__name__)


class TranslationNotFoundError(FormalLogicExceptionBase):
    pass


class Translator(ABC):

    @abstractmethod
    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> List[Tuple[Optional[str], Optional[str]]]:
        pass


class SentenceWiseTranslator(Translator):
    """Translator compatible with ./configs/formal_logic/sentence_translations/syllogistic_corpus-02.json"""

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

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> List[Tuple[Optional[str], Optional[str]]]:
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
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation not found for {formula.rep}')
                else:
                    logger.warning('translation not found for %s', formula.rep)
                    translations.append(None)

        # term translation
        if self.translate_terms:
            term_mappings = generate_replacement_mappings_from_terms(
                list(set([predicate.rep for formula in formulas for predicate in formula.predicates])),
                list(set([constant.rep for formula in formulas for constant in formula.constants])),
                self.predicate_translations,
                self.constant_translations,
                block_shuffle=True,
            )
            term_mapping = next(term_mappings)
            for i_formula, (formula, translation) in enumerate(zip(formulas, translations)):
                if translation is not None:
                    translations[i_formula] = replace_formula(Formula(translation), term_mapping).rep
                    print('[translated]:', translations[i_formula])
                else:
                    print('[no translation]', formula.rep)

        return [(None, translation) for translation in translations]


class IterativeRegexpTranslator(Translator):
    """ sample implementation of regexp matching """

    def __init__(self):
        pass

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> List[Tuple[Optional[str], Optional[str]]]:
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

        return [(None, translated_rep) for translated_rep in translated_reps]


class ClauseTypedTranslator(Translator):

    def __init__(self,
                 sentence_translations: Dict[str, Dict],
                 word_bank: WordBank,
                 translate_terms=True,
                 verb_vs_adj_sampling_rate = 3 / 4,  # tune this if pos_type distribution is skewed.
                 ):

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
        self.translate_terms = translate_terms
        self.wb = word_bank

        self._adjs = set(self.wb.get_words(pos=POS.ADJ))
        self._verbs = {word for word in self.wb.get_words(pos=POS.VERB)
                       if self.wb.can_be_intransitive_verb(word)}
        self._nouns = {word for word in self.wb.get_words(pos=POS.NOUN)}

        self.verb_vs_adj_sampling_rate = verb_vs_adj_sampling_rate

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> List[Tuple[Optional[str], Optional[str]]]:
        replaced_typed_translations: List[Dict] = []
        translation_formula_reps = []

        # sentence translation
        for formula in formulas:

            done_translation = False
            for trans_formula_rep, clause_typed_translations in self._sentence_translations.items():
                if len(clause_typed_translations) == 0:
                    continue

                trans_formula = Formula(trans_formula_rep)
                for mapping in generate_replacement_mappings_from_formula([trans_formula], [formula]):
                    trans_formula_replaced = replace_formula(trans_formula, mapping)
                    if trans_formula_replaced.rep == formula.rep:
                        replaced_translations = {}
                        for clause_type, pos_typed_translations in clause_typed_translations.items():
                            replaced_translations[clause_type] = {}
                            for predicate_pos_type, nls in pos_typed_translations.items():
                                replaced_translations[clause_type][predicate_pos_type] = []
                                for nl in nls:
                                    translated_nl = replace_formula(Formula(nl), mapping)
                                    replaced_translations[clause_type][predicate_pos_type].append(translated_nl)
                        replaced_typed_translations.append(replaced_translations)
                        translation_formula_reps.append(trans_formula_rep)
                        done_translation = True
                        break
                if done_translation:
                    break

            if not done_translation:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation not found for {formula.rep}')
                else:
                    logger.warning('translation not found for %s', formula.rep)
                    replaced_typed_translations.append(None)
                    translation_formula_reps.append(None)

        # term translation
        translations = []
        translation_names = []

        if self.translate_terms:
            term_mappings = generate_replacement_mappings_from_terms(
                list({predicate.rep for formula in formulas for predicate in formula.predicates}),
                list({constant.rep for formula in formulas for constant in formula.constants}),
                self._sample_predicate_translations(),
                self._sample_constant_translations(),
                block_shuffle=True,
            )
            term_mapping = next(term_mappings)
            for i_formula, (formula, _replaced_typed_translations) in enumerate(zip(formulas, replaced_typed_translations)):
                if _replaced_typed_translations is None:
                    translations.append(None)
                    translation_names.append(None)
                else:
                    predicate_symbols = [pred.rep for pred in formula.predicates]
                    if any([word in self._adjs
                            for symbol, word in term_mapping.items()
                            if symbol in predicate_symbols]):
                        possible_predicate_pos_types = ['adj_predicate']
                    else:
                        possible_predicate_pos_types = ['verb_predicate', 'adj_predicate']

                    clause_type = random.choice(['verb_clause', 'noun_clause'])
                    predicate_pos_type = random.choice(possible_predicate_pos_types)
                    nls = _replaced_typed_translations[clause_type][predicate_pos_type]

                    i_translation = random.choice(range(len(nls)))
                    nl = nls[i_translation].rep

                    inflated_mapping = {}
                    for symbol, word in term_mapping.items():
                        if symbol not in [f.rep for f in formula.predicates + formula.constants]:
                            continue

                        if symbol in CONSTANTS:
                            inflated_mapping[symbol] = word
                        else:
                            if predicate_pos_type == 'adj_predicate':
                                if POS.ADJ in self.wb.get_pos(word):
                                    inflated_word = word
                                elif POS.VERB in self.wb.get_pos(word):
                                    inflated_word = self.wb.change_verb_form(word, VerbForm.VBG, force=True)
                                else:
                                    raise Exception()
                            elif predicate_pos_type == 'verb_predicate':
                                if POS.ADJ in self.wb.get_pos(word):
                                    raise Exception()
                                elif POS.VERB in self.wb.get_pos(word):
                                    if nl.find(f'does not {symbol}') >= 0:
                                        inflated_word = self.wb.change_verb_form(word, VerbForm.VB, force=True)
                                    else:
                                        inflated_word = self.wb.change_verb_form(word, VerbForm.VBZ, force=True)
                                else:
                                    raise Exception()

                            else:
                                raise Exception()

                            if inflated_word is None:
                                raise Exception()
                            inflated_mapping[symbol] = inflated_word

                    translation_names.append('.'.join([translation_formula_reps[i_formula], f'clause-{clause_type}', f'predicate-{predicate_pos_type}', str(i_translation)]))
                    translations.append(replace_formula(Formula(nl), inflated_mapping).rep)

        return [(name, translation) for name, translation in zip(translation_names, translations)]

    def _sample_predicate_translations(self, num=100) -> List[str]:
        # We sample more from verbs since the condition for "possible_pos_types" (see lines around 230)
        # is harder for verbs.
        verbs = random.sample(self._verbs, int(num * self.verb_vs_adj_sampling_rate))
        adjs = random.sample(self._adjs, int(num * (1 - self.verb_vs_adj_sampling_rate)))
        return list(set(verbs + adjs))

    def _sample_constant_translations(self, num=100) -> List[str]:
        return random.sample(self._nouns, num)
