import json
from typing import List, Dict, Optional, Tuple, Union, Iterable
from abc import abstractmethod, ABC
from collections import OrderedDict, defaultdict
import random
import re
import logging
from pprint import pformat, pprint
from nltk.corpus import cmudict
from functools import lru_cache

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
from .interpretation import (
    generate_mappings_from_formula,
    generate_mappings_from_predicates_and_constants,
    interprete_formula,
    formula_can_not_be_identical_to,
)
from .word_banks import POS, VerbForm, AdjForm, NounForm
from .exception import FormalLogicExceptionBase
from .utils import starts_with_vowel_sound
import kern_profiler

logger = logging.getLogger(__name__)


def calc_formula_specificity(formula: Formula) -> float:
    """ Caluculate the specificity of the formula.

    Examples:
        {F}{a} -> {G}{a} is more specific than {F}{a} -> {G}{b},
        since the former is constrained version of the latter as {a}={b}
    """
    return - float(len(formula.predicates) + len(formula.constants))


class TranslationNotFoundError(FormalLogicExceptionBase):
    pass


class Translator(ABC):

    @property
    @abstractmethod
    def translation_names(self) -> List[str]:
        pass

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
                 do_translate_to_nl=True):

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
                    logger.warning('translation not found for "%s"', formula.rep)
                    translations.append(None)

        if self.do_translate_to_nl:
            interp_mappings = generate_mappings_from_predicates_and_constants(
                list(set([predicate.rep for formula in formulas for predicate in formula.predicates])),
                list(set([constant.rep for formula in formulas for constant in formula.constants])),
                self.predicate_translations,
                self.constant_translations,
                block_shuffle=True,
            )
            interp_mapping = next(interp_mappings)
            for i_formula, (formula, translation) in enumerate(zip(formulas, translations)):
                if translation is not None:
                    translations[i_formula] = interprete_formula(Formula(translation), interp_mapping).rep

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

                    for mapping in generate_mappings_from_formula([src_formula], [formula]):
                        src_formula_replaced = interprete_formula(src_formula, mapping)
                        tgt_formula_replaced = interprete_formula(tgt_formula, mapping)
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
                 do_translate_to_nl=True,
                 ):

        two_layered_config = self._build_two_layered_config(config_json)

        _resolved_translations = {}
        for prefix, config in two_layered_config.items():
            _resolved_translations[prefix] = {
                key: [
                    resolved_nl
                    for transl_nl in transl_nls
                    for resolved_nl in self._resolve_translation(transl_nl, two_layered_config)
                ]
                for key, transl_nls in config.items()
            }

        _resolved_translations_sorted = {}
        for prefix, config in _resolved_translations.items():
            _resolved_translations_sorted[prefix] = OrderedDict(
                (transl_key, transl_nls)
                for transl_key, transl_nls in sorted(config.items(), key=lambda key_nls: (calc_formula_specificity(Formula(key_nls[0])), key_nls[0]))
            )

        self._translations: Dict[str, List[str]] = _resolved_translations_sorted['sentence']
        logger.info('---- loaded translations ----')
        for key, nls in self._translations.items():
            logger.info(key)
            for nl in nls:
                logger.info('    ' + nl)

        # self._translations, self._clause_translations = self._load_translations(config_json)

        self._adj_and_verbs, self._entity_nouns, self._event_nouns = self._load_words(word_bank)
        self._wb = word_bank

        self._do_translate_to_nl = do_translate_to_nl

    def _build_two_layered_config(self, config: Dict) -> Dict[str, Dict[str, List[str]]]:
        two_layered_config = self._completely_flatten_config(config)

        one_hierarchy_config: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        for key, val in two_layered_config.items():
            if key.find('::') >= 0:
                prefix = '::'.join(key.split('::')[:-1])
                transl_key = key.split('::')[-1]
            else:
                prefix = 'others'
                transl_key = key
            one_hierarchy_config[prefix][transl_key] = val
        return one_hierarchy_config

    def _completely_flatten_config(self, config: Dict) -> Dict[str, List[str]]:
        flat_config = {}
        for key, val in config.items():
            if isinstance(val, str):
                flat_config[key] = [val]
            elif isinstance(val, list):
                flat_config[key] = val
            elif isinstance(val, dict):
                for child_key, child_val in self._completely_flatten_config(val).items():
                    flat_config[f'{key}::{child_key}'] = child_val
            else:
                raise ValueError()
        return flat_config

    def _resolve_translation(self,
                             nl: str,
                             two_layered_config: Dict[str, Dict[str, List[str]]]) -> List[str]:
        resolved_nls = [nl]
        for template in self._extract_transl_templates(nl):
            template_prefix = '::'.join(template.split('::')[:-1])
            template_key = template.split('::')[-1]
            template_key_formula = Formula(template_key)

            template_nls = None
            template_is_found = False
            for transl_prefix, config in two_layered_config.items():
                if transl_prefix != template_prefix:
                    continue
                for transl_key, transl_nls in config.items():
                    transl_key_formula = Formula(transl_key)
                    if formula_can_not_be_identical_to(transl_key_formula, template_key_formula):
                        continue
                    for mapping in generate_mappings_from_formula([transl_key_formula],
                                                                  [template_key_formula]):
                        key_formula_pulled = interprete_formula(transl_key_formula, mapping)
                        if key_formula_pulled.rep == template_key_formula.rep:
                            template_nls = [interprete_formula(Formula(transl_nl), mapping).rep for transl_nl in transl_nls]
                            template_is_found = True
                    if template_is_found:
                        break
                if template_is_found:
                    break
            if not template_is_found:
                logger.warning(f'Template "{template}" not found, which appeared in "{nl}"')
                return []

            resolved_template_nls = [
                resolved_template_nl
                for template_nl in template_nls
                for resolved_template_nl in self._resolve_translation(template_nl, two_layered_config)
            ]

            resolved_nls = [
                transl_nl.replace(f'<{template}>', resolved_template_nl)
                for transl_nl in resolved_nls
                for resolved_template_nl in resolved_template_nls
            ]
        return resolved_nls

    def _extract_transl_templates(self, nl: str) -> Iterable[str]:
        for match in re.finditer(r'<[^>]*>', nl):
            yield nl[match.span()[0] + 1 : match.span()[1] - 1]

    def _load_words(self,
                    word_bank: WordBank):
        logger.info('loading words from WordBank ...')
        _adj_set = set(self._load_words_by_pos_attrs(word_bank, pos=POS.ADJ))
        _intransitive_verb_set = {
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
            if ATTR.can_be_intransitive_verb in word_bank.get_attrs(word)
        }
        _adj_and_verbs = sorted(_adj_set.union(_intransitive_verb_set))
        _entity_nouns = sorted(
            word for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_entity_noun in word_bank.get_attrs(word)
        )
        _event_nouns = sorted(
            word for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_event_noun in word_bank.get_attrs(word)
        )
        logger.info('loading words from WordBank done!')
        return _adj_and_verbs, _entity_nouns, _event_nouns

    @profile
    def _load_words_by_pos_attrs(self,
                                 word_bank: WordBank,
                                 pos: Optional[POS] = None,
                                 attrs: Optional[List[ATTR]] = None) -> Iterable[str]:
        attrs = attrs or []
        for word in word_bank.get_words():
            if pos is not None and pos not in word_bank.get_pos(word):
                continue
            if any((attr not in word_bank.get_attrs(word)
                    for attr in attrs)):
                continue
            yield word

    @property
    def translation_names(self) -> List[str]:
        return [self._translation_name(sentence_key, nl)
                for sentence_key, nls in self._translations.items()
                for nl in nls]

    def _translation_name(self, sentence_key: str, nl: str) -> str:
        return '____'.join([sentence_key, nl])

    @profile
    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]], Dict[str, int]]:

        def raise_or_warn(msg: str) -> None:
            if raise_if_translation_not_found:
                # import pudb; pudb.set_trace()
                # XXX: remove comment out
                raise TranslationNotFoundError(msg)
            else:
                logger.warning(msg)

        translations = []
        translation_names = []
        count_stats = {'inflation': defaultdict(int)}

        interp_mapping = self._choose_interp_mapping(formulas)

        for formula in formulas:
            # Chose translations which is consistent with the formula.
            sentence_key, sentence_nls, sentence_nls_pulled = self._find_sentence_consistent_translation(formula)
            if sentence_nls is None or len(sentence_nls) == 0:
                if sentence_nls is None:
                    raise_or_warn(f'sentence translation not found for "{formula.rep}"')
                else:
                    assert(len(sentence_nls) == 0)
                    raise_or_warn(f'sentence translation for "{formula.rep}" is found (key="{sentence_key}"), but it has empty list. This can be caused by that translation templates could not be resolved for that translations.')

                sentence_key, sentence_nls, sentence_nls_pulled = self._find_sentence_consistent_translation(formula)
                translations.append(None)
                translation_names.append(None)
                continue

            # Chose translations the pos and inflations of which are consistent with the interpretation mapping.
            interp_mapping_consisntent_nls_pulled = self._find_interp_mapping_consistent_translations(
                sentence_nls_pulled,
                interp_mapping,
            )
            interp_mapping_consisntent_nls = [
                sentence_nl
                for sentence_nl, sentence_nl_pulled in zip(sentence_nls, sentence_nls_pulled)
                if sentence_nl_pulled in interp_mapping_consisntent_nls_pulled
            ]
            if len(interp_mapping_consisntent_nls) == 0:
                msgs = [
                    f'translation not found for "{formula.rep}" the pos and word inflations of which are consistent with the following chosen interpretation mapping.',
                    'The tried translations are:\n{"\n".join(interp_mapping_consisntent_nls_pulled)}',
                    'The interp_mapping is:{pformat(interp_mapping)}',
                ]
                raise_or_warn('\n'.join(msgs))
                translations.append(None)
                translation_names.append(None)
                continue

            # Choose a translation
            _idx = random.choice(range(len(interp_mapping_consisntent_nls_pulled)))
            chosen_nl = interp_mapping_consisntent_nls[_idx]
            chosen_nl_pulled = interp_mapping_consisntent_nls_pulled[_idx]

            # Generate word inflated mapping.
            inflated_mapping, _inflation_stats = self._make_word_inflated_interp_mapping(interp_mapping, chosen_nl_pulled)
            for inflation_type, count in _inflation_stats.items():
                count_stats['inflation'][f'{inflation_type}'] = count

            interp_templated_translation_pulled_wo_info = re.sub('\[[^\]]*\]', '', chosen_nl_pulled)

            # do interpretation using predicates and constants using interp_mapping
            if self._do_translate_to_nl:
                interp_templated_translation_pulled_wo_info_definite_article_induced = self._replace_indefinite_with_definite_articles(interp_templated_translation_pulled_wo_info)
                translation = interprete_formula(Formula(interp_templated_translation_pulled_wo_info_definite_article_induced), inflated_mapping).rep
            else:
                translation = interp_templated_translation_pulled_wo_info

            translations.append(translation)
            translation_names.append(self._translation_name(sentence_key, chosen_nl))

        translations = [
            (self._correct_indefinite_articles(translation) if translation is not None else None)
            for translation in translations
        ]

        return list(zip(translation_names, translations)), count_stats

    def _find_sentence_consistent_translation(self, formula: Formula) -> Union[Tuple[str, List[str], List[str]], Tuple[None, None, None]]:
        transl_key = None
        transl_nls = None
        transl_nls_pulled = None
        transl_is_found = False
        for _transl_key, _transl_nls in self._translations.items():
            if formula_can_not_be_identical_to(Formula(_transl_key), formula):  # early rejection
                continue

            for mapping in generate_mappings_from_formula([Formula(_transl_key)], [formula]):
                transl_key_pulled = interprete_formula(Formula(_transl_key), mapping).rep
                if transl_key_pulled == formula.rep:
                    transl_key = _transl_key
                    transl_nls = _transl_nls
                    transl_nls_pulled = [interprete_formula(Formula(transl_nl), mapping).rep for transl_nl in transl_nls]
                    transl_is_found = True
                    break
            if transl_is_found:
                break
        return transl_key, transl_nls, transl_nls_pulled

    def _find_interp_mapping_consistent_translations(self,
                                                     sentence_transl_nls_pulled: List[str],
                                                     interp_mapping: Dict[str, str]) -> List[str]:
        """ Find translations the pos and word inflations of which are consistent with interp_mapping """
        consistent_nls = []
        for sentence_transl_nl_pulled in sentence_transl_nls_pulled:
            sentence_transl_pulled_formula = Formula(sentence_transl_nl_pulled)

            interp_mapping_is_consisntent = False
            for interprand in sentence_transl_pulled_formula.predicates + sentence_transl_pulled_formula.constants:
                word = interp_mapping[interprand.rep]

                pos, form = self._get_interprand_info_from_template(interprand.rep, sentence_transl_pulled_formula.rep)
                if pos not in self._wb.get_pos(word):
                    interp_mapping_is_consisntent = False
                    break

                inflated_word = self._get_inflated_word(word, pos, form)

                if inflated_word is not None:
                    interp_mapping_is_consisntent = True
                else:
                    interp_mapping_is_consisntent = False
                    break
            if interp_mapping_is_consisntent:
                consistent_nls.append(sentence_transl_nl_pulled)
        return consistent_nls

    def _replace_indefinite_with_definite_articles(self, sentence_with_templates: str) -> str:
        constants = [c.rep for c in Formula(sentence_with_templates).constants]

        with_definite = sentence_with_templates
        for constant in constants:
            if with_definite.count(constant) < 2:
                continue

            first_pos = with_definite.find(constant)

            until_first = with_definite[:first_pos + len(constant)]
            from_second = with_definite[first_pos + len(constant):]

            from_second_with_definite = re.sub(
                f'(.*)a (.*){constant}',
                f'\g<1>the \g<2>{constant}',
                from_second,
            )
            with_definite = until_first + from_second_with_definite
        if sentence_with_templates != with_definite:
            logger.info('articles "a" are modified to "the" as:    "%s"    ->    "%s"',
                        sentence_with_templates,
                        with_definite)
            # print(f'"{sentence_with_templates}"    ->    "{with_definite}"')
        return with_definite

    def _correct_indefinite_articles(self, sentence_wo_templates: str) -> str:
        words = sentence_wo_templates.split(' ')
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

    @profile
    def _choose_interp_mapping(self, formulas: List[Formula]) -> Dict[str, str]:
        zeroary_predicates = list({predicate.rep
                                   for formula in formulas
                                   for predicate in formula.zeroary_predicates})
        unary_predicates = list({predicate.rep
                                 for formula in formulas
                                 for predicate in formula.unary_predicates})
        constants = list({constant.rep for formula in formulas for constant in formula.constants})

        # zero-ary predicate {A}, which appears as ".. {A} i ..", shoud be Noun.
        zeroary_mapping = next(
            generate_mappings_from_predicates_and_constants(
                zeroary_predicates,
                [],
                random.sample(self._event_nouns, len(zeroary_predicates) * 3),
                [],
                block_shuffle=True,
                allow_many_to_one=False,
            )
        )

        # Unary predicate {A}, which appears as "{A}{a}", shoud be adjective or verb.
        unary_mapping = next(
            generate_mappings_from_predicates_and_constants(
                unary_predicates,
                constants,
                random.sample(self._adj_and_verbs, len(unary_predicates) * 3),
                random.sample(self._entity_nouns, len(constants) * 3),
                block_shuffle=True,
                allow_many_to_one=False,
            )
        )

        interp_mapping = zeroary_mapping.copy()
        interp_mapping.update(unary_mapping)

        return interp_mapping

    def _make_word_inflated_interp_mapping(self,
                                           interp_mapping: Dict[str, str],
                                           interprand_templated_translation_pulled: str) -> Tuple[Dict[str, str], Dict[str, int]]:
        inflated_mapping = {}
        stats = defaultdict(int)

        for interprand_formula in Formula(interprand_templated_translation_pulled).predicates\
                + Formula(interprand_templated_translation_pulled).constants:
            interprand_rep = interprand_formula.rep
            if interprand_templated_translation_pulled.find(f'{interprand_rep}[') >= 0:
                word = interp_mapping[interprand_rep]
                pos, form = self._get_interprand_info_from_template(interprand_rep, interprand_templated_translation_pulled)
                stats[f'{pos.value}.{form.value}'] += 1
                inflated_word = self._get_inflated_word(word, pos, form)
                assert(inflated_word is not None)
            else:
                raise Exception(
                    f'Something wrong. Since we have checked in that the translation indeed exists, this program must not pass this block.  The problematic translation is "{interprand_templated_translation_pulled}" and unfound string is "{interprand_rep}["',
                )
            inflated_mapping[interprand_rep] = inflated_word
        return inflated_mapping, stats

    def _get_interprand_info_from_template(self, interprand: str, rep: str) -> Tuple[POS, Union[AdjForm, VerbForm, NounForm]]:
        if not re.match(f'.*{interprand}\[([^\]]*)\].*', rep):
            raise Exception(f'Information for "{interprand}" can not be extracted from "{rep}".')
        info = re.sub(f'.*{interprand}\[([^\]]*)\].*', r'\g<1>', rep)

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
