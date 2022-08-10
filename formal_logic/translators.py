import json
from typing import List, Dict, Optional, Tuple, Union
from abc import abstractmethod, ABC
from collections import OrderedDict, defaultdict
import random
import re
import logging

from .formula import Formula, CONSTANTS
from .word_banks.base import WordBank
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    replace_formula,
)
from .word_banks import POS, VerbForm, AdjForm, NounForm
from .exception import FormalLogicExceptionBase

logger = logging.getLogger(__name__)


class TranslationNotFoundError(FormalLogicExceptionBase):
    pass


class Translator(ABC):

    @abstractmethod
    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:
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

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:
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

        return [(None, translation) for translation in translations], {}


class IterativeRegexpTranslator(Translator):
    """ sample implementation of regexp matching """

    def __init__(self):
        pass

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:

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

        return [(None, translated_rep) for translated_rep in translated_reps], {}


class ClauseTypedTranslator(Translator):

    def __init__(self,
                 config_json: Dict[str, Dict],
                 word_bank: WordBank,
                 verb_vs_adj_sampling_rate = 3 / 4,  # tune this if pos_type distribution is skewed.
                 translate_terms=True,
                 ):

        self._clause_translations = {
            f'{clause_type}.{terms_rep}': pos_typed_translations
            for clause_type, clause_translations in config_json['clauses'].items()
            for terms_rep, pos_typed_translations in clause_translations.items()
        }

        def num_terms(formula_rep: str) -> int:
            formula = Formula(formula_rep)
            return len(formula.predicates) + len(formula.constants) + len(formula.variables)

        self._translations = OrderedDict([
            (rep, translations)
            for rep, translations in sorted(config_json['translations'].items(), key=lambda rep_trans: num_terms(rep_trans[0]))
        ][::-1])

        self._wb = word_bank
        self._adjs = set(self._wb.get_words(pos=POS.ADJ))
        self._verbs = {word for word in self._wb.get_words(pos=POS.VERB)
                       if self._wb.can_be_intransitive_verb(word)}
        self._nouns = {word for word in self._wb.get_words(pos=POS.NOUN)}
        self._verb_vs_adj_sampling_rate = verb_vs_adj_sampling_rate

        self._translate_terms = translate_terms

    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:

        translations = []
        translation_names = []
        count_stats = {'inflation': defaultdict(int)}

        term_mapping = self._choose_term_mapping(formulas)

        for formula in formulas:
            (predicate_symbol_mapping,
             clause_templated_translation_key,
             clause_templated_translation,
             clause_templated_translation_replaced) = self._choose_clause_templated_translation(formula)

            if clause_templated_translation_replaced is None:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation not found for {formula.rep}')
                else:
                    logger.warning('translation not found for %s', formula.rep)
                    translations.append(None)
                    translation_names.append(None)
                    continue

            term_templated_translation_replaced = self._choose_term_templated_translation(
                formula,
                clause_templated_translation_replaced,
                term_mapping,
            )

            # inverse mapping
            term_templated_translation = replace_formula(Formula(term_templated_translation_replaced),
                                                         {v: k for k, v in predicate_symbol_mapping.items()}).rep

            if term_templated_translation_replaced.find('clause') >= 0:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation may not be complete for "{term_templated_translation_replaced}"')
                else:
                    import pudb; pudb.set_trace()
                    logger.warning('translation may not be complete for "%s"', term_templated_translation_replaced)

            # inflation
            inflated_mapping, _inflation_stats = self._make_inflated_mapping(term_mapping, term_templated_translation_replaced)
            for inflation_type, count in _inflation_stats.items():
                count_stats['inflation'][f'{inflation_type}'] = count

            term_templated_translation_replaced_wo_info = re.sub('\[[^\]]*\]', '', term_templated_translation_replaced)

            if self._translate_terms:
                translation = replace_formula(Formula(term_templated_translation_replaced_wo_info), inflated_mapping).rep
            else:
                translation = term_templated_translation_replaced_wo_info

            translations.append(translation)
            translation_names.append(
                '____'.join([clause_templated_translation_key,
                             clause_templated_translation,
                             term_templated_translation])
            )

        return list(zip(translation_names, translations)), count_stats

    def _choose_term_mapping(self, formulas: List[Formula]) -> Dict[str, str]:
        predicates = list({predicate.rep for formula in formulas for predicate in formula.predicates})
        zeroary_predicates = [p_rep for p_rep in predicates
                              if all([f'{p_rep}x' not in formula.rep and f'{p_rep}{{' not in formula.rep
                                      for formula in formulas])]
        unary_predicates = [p_rep for p_rep in predicates
                            if p_rep not in zeroary_predicates]
        constraints = list({constant.rep for formula in formulas for constant in formula.constants})

        zeroary_mapping = next(
            generate_replacement_mappings_from_terms(
                zeroary_predicates,
                constraints,
                random.sample(self._adjs, len(zeroary_predicates)) + random.sample(self._verbs, len(zeroary_predicates)),
                random.sample(self._nouns, len(constraints)),
                block_shuffle=True,
            )
        )
        unary_mapping = next(
            generate_replacement_mappings_from_terms(
                unary_predicates,
                [],
                random.sample(self._adjs, len(unary_predicates)) + random.sample(self._verbs, len(unary_predicates)),
                [],
                block_shuffle=True,
            )
        )
        term_mapping = zeroary_mapping.copy()
        term_mapping.update(unary_mapping)

        return term_mapping

    def _choose_clause_templated_translation(self, formula: Formula) -> Tuple[Optional[Dict[str, str]],
                                                                              Optional[str],
                                                                              Optional[str],
                                                                              Optional[str]]:
        mapping = None
        clause_templated_translation_key = None
        clause_templated_translation = None
        clause_templated_translation_replaced = None
        for _translation_formula_rep, clause_templated_translations in self._translations.items():
            if len(clause_templated_translations) == 0:
                continue

            _translation_formula = Formula(_translation_formula_rep)
            for _mapping in generate_replacement_mappings_from_formula([_translation_formula], [formula]):
                trans_formula_replaced = replace_formula(_translation_formula, _mapping)
                if trans_formula_replaced.rep == formula.rep:
                    mapping = _mapping
                    clause_templated_translation = random.choice(clause_templated_translations)
                    clause_templated_translation_replaced = replace_formula(
                        Formula(clause_templated_translation),
                        _mapping
                    ).rep
                    clause_templated_translation_key = _translation_formula.rep
                    break
        return mapping, clause_templated_translation_key, clause_templated_translation, clause_templated_translation_replaced

    def _choose_term_templated_translation(self,
                                           formula: Formula,
                                           clause_templated_translation_replaced: str,
                                           term_mapping: Dict[str, str]) -> Optional[str]:
        
        term_templated_translation_replaced = clause_templated_translation_replaced

        has_clause_replacement = True
        while has_clause_replacement:
            has_clause_replacement = False
            for clause_template, pos_typed_translations in self._clause_translations.items():
                for clause_template_mapping in generate_replacement_mappings_from_formula([Formula(clause_template)],
                                                                                          [formula]):
                    clause_template_replaced = replace_formula(Formula(clause_template), clause_template_mapping).rep

                    if term_templated_translation_replaced.find(f'{{{clause_template_replaced}}}') < 0:
                        continue

                    _term_templated_translation_key = None
                    _term_templated_translation_replaced = None
                    predicate_symbols = [p.rep for p in Formula(clause_template_replaced).predicates]

                    possible_term_templated_translations = []
                    possible_term_templated_translations_replaced = []
                    for pos_typed_translation in pos_typed_translations:
                        pos_typed_translation_replaced = replace_formula(Formula(pos_typed_translation), clause_template_mapping).rep
                        pos_typed_predicate_found = False
                        for predicate_symbol in predicate_symbols:
                            word = term_mapping[predicate_symbol]

                            pos, form = self._get_predicate_info(predicate_symbol, pos_typed_translation_replaced)
                            if pos not in self._wb.get_pos(word):
                                pos_typed_predicate_found = False
                                break

                            inflated_word = self._get_inflated_word(word, pos, form)

                            if inflated_word is not None:
                                pos_typed_predicate_found = True
                            else:
                                pos_typed_predicate_found = False
                                break
                        if pos_typed_predicate_found:
                            possible_term_templated_translations.append(pos_typed_translation)
                            possible_term_templated_translations_replaced.append(pos_typed_translation_replaced)
                    if len(possible_term_templated_translations_replaced) == 0:
                        raise ValueError(f'pos typed translation not found for "{clause_template_replaced}"')
                    _idx = random.choice(range(len(possible_term_templated_translations_replaced)))
                    _term_templated_translation_key = possible_term_templated_translations[_idx]
                    _term_templated_translation_replaced = possible_term_templated_translations_replaced[_idx]

                    possible_term_templated_translations_replaced = []
                    for pos_typed_translation in pos_typed_translations:
                        pos_typed_translation_replaced = replace_formula(Formula(pos_typed_translation), clause_template_mapping).rep
                        pos_typed_predicate_found = None
                        for predicate_symbol in predicate_symbols:
                            word = term_mapping[predicate_symbol]

                            pos_typed_predicate_found = False
                            for pos in self._wb.get_pos(word):
                                if pos_typed_translation_replaced.find(f'{predicate_symbol}[{pos.value}') >= 0:
                                    pos_typed_predicate_found = True
                                    break
                            if not pos_typed_predicate_found:
                                break
                        if pos_typed_predicate_found:
                            possible_term_templated_translations_replaced.append(pos_typed_translation_replaced)

                    term_templated_translation_replaced = term_templated_translation_replaced.replace(f'{{{clause_template_replaced}}}', _term_templated_translation_replaced)
                    has_clause_replacement = True
                    break
                if has_clause_replacement:
                    break
        return term_templated_translation_replaced

    def _make_inflated_mapping(self,
                               term_mapping: Dict[str, str],
                               term_templated_translation_replaced: str) -> Tuple[Dict[str, str], Dict[str, int]]:
        inflated_mapping = {}
        stats = defaultdict(int)

        for constraint_formula in Formula(term_templated_translation_replaced).constants:
            inflated_mapping[constraint_formula.rep] = term_mapping[constraint_formula.rep]

        for predicate_symbol_formula in Formula(term_templated_translation_replaced).predicates:
            predicate_symbol = predicate_symbol_formula.rep
            if term_templated_translation_replaced.find(f'{predicate_symbol}[') >= 0:

                word = term_mapping[predicate_symbol]
                pos, form = self._get_predicate_info(predicate_symbol, term_templated_translation_replaced)
                stats[f'{pos.value}.{form.value}'] += 1
                inflated_word = self._get_inflated_word(word, pos, form)
                assert(inflated_word is not None)

            else:
                # inflated_word = term_mapping[predicate_symbol]
                raise Exception()
            inflated_mapping[predicate_symbol] = inflated_word
        return inflated_mapping, stats

    def _get_predicate_info(self, predicate: str, rep: str) -> Tuple[POS, Union[AdjForm, VerbForm, NounForm]]:
        info = re.sub(f'.*{predicate}\[([^\]]*)\].*', r'\g<1>', rep)

        if len(info.split('.')) >= 2:
            pos_str, form_str = info.split('.')
        else:
            pos_str, form_str = info, None

        pos = POS[pos_str]

        if pos == POS.ADJ:
            form = AdjForm.NORMAL if form_str is None else AdjForm(form_str)
        elif pos == POS.VERB:
            form = VerbForm.NORMAL if form_str is None else VerbForm(form_str)
        elif pos == POS.NOUN:
            form = NounForm.NORMAL if form_str is None else NounForm(form_str)
        else:
            raise ValueError()

        return pos, form

    def _get_inflated_word(self, word: str, pos: POS, form: Union[AdjForm, VerbForm, NounForm]) -> Optional[str]:
        if pos not in self._wb.get_pos(word):
            raise ValueError(f'the word={word} does not have pos={str(pos)}')

        if pos == POS.ADJ:
            inflation_func = self._wb.change_adj_form
            force = False
        elif pos == POS.VERB:
            inflation_func = self._wb.change_verb_form
            force = True
        elif pos == POS.NOUN:
            inflation_func = self._wb.change_noun_form
            force = False
        else:
            raise ValueError()
        return inflation_func(word, form, force=force)
