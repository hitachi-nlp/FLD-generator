import json
from typing import List, Dict, Optional, Tuple, Union, Iterable
from abc import abstractmethod, ABC
from collections import OrderedDict, defaultdict
import random
import re
import logging
from pprint import pformat, pprint
from nltk.corpus import cmudict

from .formula import (
    Formula,
    CONSTANTS,
    VARIABLES,
    AND,
    OR,
    IMPLICATION,
    NOT,
)
from .word_banks.base import WordBank, ATTR
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    replace_formula,
    formula_can_not_be_identical_to,
)
from .word_banks import POS, VerbForm, AdjForm, NounForm
from .exception import FormalLogicExceptionBase
from .utils import starts_with_vowel_sound
import kern_profiler

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

    @profile
    def __init__(self,
                 config_json: Dict[str, Dict],
                 word_bank: WordBank,
                 verb_vs_adj_sampling_rate = 3 / 4,  # tune this if pos_type distribution is skewed.
                 translate_terms=True,
                 ):

        def num_terms(formula_rep: str) -> int:
            formula = Formula(formula_rep)
            return len(formula.predicates) + len(formula.constants) + len(formula.variables)

        self._translations = OrderedDict([
            (rep, translations)
            for rep, translations in sorted(config_json['translations'].items(), key=lambda rep_trans: num_terms(rep_trans[0]))
        ][::-1])

        self._clause_translations = {
            f'{clause_type}.{terms_rep}': pos_typed_translations
            for clause_type, clause_translations in config_json['clauses'].items()
            for terms_rep, pos_typed_translations in clause_translations.items()
        }

        logger.info('')
        logger.info('')
        logger.info('============================== Loaded Translations =====================================  ')
        logger.info('')
        logger.info('------------------ sentence translations -----------------------')
        for sentence_key, nls in self._translations.items():
            logger.info('"%s"', sentence_key)
            for nl in nls:
                logger.info('    "%s"', nl)
        logger.info('')
        logger.info('------------------ clause translations -----------------------')
        for clause_key, nls in self._clause_translations.items():
            logger.info('"%s"', clause_key)
            for nl in nls:
                logger.info('    "%s"', nl)
                # logger.info(re.sub('\n', '\n    ', pformat(self._translations)))

        self._wb = word_bank
        logger.info('loading words from WordBank ...')
        _adj_set = set(self._load_words(pos=POS.ADJ))
        _intransitive_verb_set = {
            word
            for word in self._load_words(pos=POS.VERB)
            if ATTR.can_be_intransitive_verb in self._wb.get_attrs(word)
        }
        self._adj_and_verbs = sorted(_adj_set.union(_intransitive_verb_set))
        self._entity_nouns = sorted(
            word for word in self._load_words(pos=POS.NOUN)
            if ATTR.can_be_entity_noun in self._wb.get_attrs(word)
        )
        self._event_nouns = sorted(
            word for word in self._load_words(pos=POS.NOUN)
            if ATTR.can_be_event_noun in self._wb.get_attrs(word)
        )
        logger.info('loading words from WordBank done!')

        self._verb_vs_adj_sampling_rate = verb_vs_adj_sampling_rate

        self._translate_terms = translate_terms

    @profile
    def _load_words(self,
                    pos: Optional[POS] = None,
                    attrs: Optional[List[ATTR]] = None) -> Iterable[str]:
        attrs = attrs or []
        for word in self._wb.get_words():
            if pos is not None and pos not in self._wb.get_pos(word):
                continue
            if any((attr not in self._wb.get_attrs(word)
                    for attr in attrs)):
                continue
            yield word

    @profile
    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:

        translations = []
        translation_names = []
        count_stats = {'inflation': defaultdict(int)}

        term_mapping = self._choose_term_mapping(formulas)
        # if len(set(term_mapping.values())) != len(term_mapping):
        #     raise Exception()

        for formula in formulas:
            # Choose clauset templated translation
            (predicate_symbol_mapping,
             clause_templated_translation_key,
             clause_templated_translation,
             clause_templated_translation_replaced) = self._choose_clause_templated_translation(formula)
            if clause_templated_translation_replaced is None:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation not found for {formula.rep}')
                else:
                    translations.append(None)
                    translation_names.append(None)
                    continue

            # Replace clause template. The result is term templated translation.
            term_templated_translation_replaced = self._replace_clause_templates(
                formula,
                clause_templated_translation_replaced,
                term_mapping,
            )
            if term_templated_translation_replaced is None:
                if raise_if_translation_not_found:
                    raise TranslationNotFoundError(f'translation may not be complete for "{term_templated_translation_replaced}"')
                else:
                    translations.append(None)
                    translation_names.append(None)
                    continue

            # Generate word inflated mapping.
            inflated_mapping, _inflation_stats = self._make_inflated_mapping(term_mapping, term_templated_translation_replaced)
            for inflation_type, count in _inflation_stats.items():
                count_stats['inflation'][f'{inflation_type}'] = count

            term_templated_translation_replaced_wo_info = re.sub('\[[^\]]*\]', '', term_templated_translation_replaced)

            # Do translation
            if self._translate_terms:
                translation = replace_formula(Formula(term_templated_translation_replaced_wo_info), inflated_mapping).rep
            else:
                translation = term_templated_translation_replaced_wo_info

            translations.append(translation)
            translation_names.append(
                self._make_translation_name(
                    clause_templated_translation_key,
                    clause_templated_translation,
                    term_templated_translation_replaced,
                    predicate_symbol_mapping
                )
            )

        translations = [(self._correct_indefinite_article(translation) if translation is not None else None)
                        for translation in translations]

        return list(zip(translation_names, translations)), count_stats

    def _correct_indefinite_article(self, sentence: str) -> str:
        words = sentence.split(' ')
        corrected_words = []
        for i_word, word in enumerate(words):
            if word.lower() in ['a', 'an']:
                if len(words) >= i_word + 2:
                    next_word = words[i_word + 1]
                    if starts_with_vowel_sound(next_word):
                        corrected_words.append('an')
                    else:
                        corrected_words.append('a')
                else:
                    raise ValueError('Sentence ends with article: {sentence}')
            else:
                corrected_words.append(word)
        return ' '.join(corrected_words)

    def _make_translation_name(self,
                               clause_templated_translation_key,
                               clause_templated_translation,
                               term_templated_translation_replaced,
                               predicate_symbol_mapping) -> str:
        # inverse mapping
        term_templated_translation = replace_formula(Formula(term_templated_translation_replaced),
                                                     {v: k for k, v in predicate_symbol_mapping.items()}).rep
        return '____'.join([clause_templated_translation_key,
                            clause_templated_translation,
                            term_templated_translation])

    @profile
    def _choose_term_mapping(self, formulas: List[Formula]) -> Dict[str, str]:
        zeroary_predicates = list({predicate.rep
                                   for formula in formulas
                                   for predicate in formula.zeroary_predicates})
        unary_predicates = list({predicate.rep
                                 for formula in formulas
                                 for predicate in formula.unary_predicates})
        constants = list({constant.rep for formula in formulas for constant in formula.constants})

        # zero-ary predicate {A}, which appears as ".. {A} i ..", shoud be Noun.
        zeroary_mapping = next(
            generate_replacement_mappings_from_terms(
                zeroary_predicates,
                [],
                random.sample(self._event_nouns, len(zeroary_predicates) * 3),
                [],
                block_shuffle=True,
                allow_replacement=False,
            )
        )

        # Unary predicate {A}, which appears as "{A}{a}", shoud be adjective or verb.
        unary_mapping = next(
            generate_replacement_mappings_from_terms(
                unary_predicates,
                constants,
                random.sample(self._adj_and_verbs, len(unary_predicates) * 3),
                random.sample(self._entity_nouns, len(constants) * 3),
                block_shuffle=True,
                allow_replacement=False,
            )
        )

        term_mapping = zeroary_mapping.copy()
        term_mapping.update(unary_mapping)

        return term_mapping

    @profile
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

            if formula_can_not_be_identical_to(Formula(_translation_formula_rep), formula):  # early rejection for speed
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

        if clause_templated_translation_key is None:
            logger.warning('clause templated translation not found for %s', formula.rep)

        return mapping, clause_templated_translation_key, clause_templated_translation, clause_templated_translation_replaced

    @profile
    def _replace_clause_templates(self,
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

                    _term_templated_translation_replaced = None
                    term_reps = [
                        term.rep
                        for term in Formula(clause_template_replaced).predicates + Formula(clause_template_replaced).constants
                    ]

                    possible_term_templated_translations = []
                    possible_term_templated_translations_replaced = []
                    for pos_typed_translation in pos_typed_translations:
                        pos_typed_translation_replaced = replace_formula(Formula(pos_typed_translation), clause_template_mapping).rep
                        pos_typed_term_found = False
                        for term_symbol in term_reps:
                            word = term_mapping[term_symbol]

                            pos, form = self._get_term_info_from_template(term_symbol, pos_typed_translation_replaced)
                            if pos not in self._wb.get_pos(word):
                                pos_typed_term_found = False
                                break

                            inflated_word = self._get_inflated_word(word, pos, form)

                            if inflated_word is not None:
                                pos_typed_term_found = True
                            else:
                                pos_typed_term_found = False
                                break
                        if pos_typed_term_found:
                            possible_term_templated_translations.append(pos_typed_translation)
                            possible_term_templated_translations_replaced.append(pos_typed_translation_replaced)
                    if len(possible_term_templated_translations_replaced) == 0:
                        possible_term_templated_translations = []
                        possible_term_templated_translations_replaced = []

                        raise ValueError(f'We could not find any clause replacement for "{clause_template_replaced}, where pos and word-inflation are consistent with the given term mapping:\n{pformat(term_mapping)}')

                    _idx = random.choice(range(len(possible_term_templated_translations_replaced)))
                    _term_templated_translation_replaced = possible_term_templated_translations_replaced[_idx]

                    possible_term_templated_translations_replaced = []
                    for pos_typed_translation in pos_typed_translations:
                        pos_typed_translation_replaced = replace_formula(Formula(pos_typed_translation), clause_template_mapping).rep
                        pos_typed_term_found = None
                        for term_symbol in term_reps:
                            word = term_mapping[term_symbol]

                            pos_typed_term_found = False
                            for pos in self._wb.get_pos(word):
                                if pos_typed_translation_replaced.find(f'{term_symbol}[{pos.value}') >= 0:
                                    pos_typed_term_found = True
                                    break
                            if not pos_typed_term_found:
                                break
                        if pos_typed_term_found:
                            possible_term_templated_translations_replaced.append(pos_typed_translation_replaced)

                    term_templated_translation_replaced = term_templated_translation_replaced.replace(f'{{{clause_template_replaced}}}', _term_templated_translation_replaced)
                    has_clause_replacement = True
                    break
                if has_clause_replacement:
                    break

        if term_templated_translation_replaced.find('verb_clause') >= 0\
                or term_templated_translation_replaced.find('noun_clause') >= 0:
            logger.warning('Clause template replacement could not be completed for "%s"', term_templated_translation_replaced)
            return None
        else:
            return term_templated_translation_replaced

    def _make_inflated_mapping(self,
                               term_mapping: Dict[str, str],
                               term_templated_translation_replaced: str) -> Tuple[Dict[str, str], Dict[str, int]]:
        inflated_mapping = {}
        stats = defaultdict(int)

        for term_formula in Formula(term_templated_translation_replaced).predicates\
                + Formula(term_templated_translation_replaced).constants:
            term_rep = term_formula.rep
            if term_templated_translation_replaced.find(f'{term_rep}[') >= 0:
                word = term_mapping[term_rep]
                pos, form = self._get_term_info_from_template(term_rep, term_templated_translation_replaced)
                stats[f'{pos.value}.{form.value}'] += 1
                inflated_word = self._get_inflated_word(word, pos, form)
                assert(inflated_word is not None)
            else:
                # inflated_word = term_mapping[term]
                raise Exception(
                    f'Something wrong. Since we have checked in self._replace_clause_templates() that the translation indeed exists, this program must not pass this block.  The problematic translation is "{term_templated_translation_replaced}" and unfound string is "{term_rep}["',
                )
            inflated_mapping[term_rep] = inflated_word
        return inflated_mapping, stats

    def _get_term_info_from_template(self, term: str, rep: str) -> Tuple[POS, Union[AdjForm, VerbForm, NounForm]]:
        if not re.match(f'.*{term}\[([^\]]*)\].*', rep):
            raise Exception(f'Information for "{term}" can not be extracted from "{rep}".')
        info = re.sub(f'.*{term}\[([^\]]*)\].*', r'\g<1>', rep)

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
            force = False
        elif pos == POS.VERB:
            force = True
        elif pos == POS.NOUN:
            force = False
        else:
            raise ValueError()
        return self._wb.change_word_form(word, form, force=force)
