import json
from typing import List, Dict, Optional, Tuple, Union, Iterable, Any, Set, Container
from collections import OrderedDict, defaultdict
from tqdm import tqdm
import random
import re
import logging
from pprint import pformat, pprint
from functools import lru_cache

from tqdm import tqdm
from FLNL.formula import Formula
from FLNL.word_banks.base import WordBank, ATTR
from FLNL.interpretation import (
    generate_mappings_from_formula,
    generate_mappings_from_predicates_and_constants,
    interpret_formula,
    formula_can_not_be_identical_to,
)
from FLNL.word_banks import POS, VerbForm, AdjForm, NounForm, WordForm
from FLNL.utils import starts_with_vowel_sound, compress, decompress
from .base import Translator, TranslationNotFoundError, calc_formula_specificity
import kern_profiler

logger = logging.getLogger(__name__)


class _PosFormConditionSet(set):

    def __new__(cls, elems: Iterable[Tuple[str, Optional[POS], Optional[WordForm]]]):
        unique_elems = set(elems)
        sorted_elems = sorted(unique_elems)
        return super().__new__(cls, sorted_elems)


class _PosFormConditionTuple(tuple):

    def __new__(cls, elems: Iterable[Tuple[str, Optional[POS], Optional[WordForm]]]):
        return super().__new__(cls, sorted(elems))


def _compress_nls(texts: List[str]) -> bytes:
    return compress('<<SEP>>'.join(texts))


def _decompress_nls(binary: bytes) -> List[str]:
    return decompress(binary).split('<<SEP>>')


class ClauseTypedTranslator(Translator):

    _TEMPLATE_BRACES = ['<<', '>>']

    def __init__(self,
                 config_json: Dict[str, Dict],
                 word_bank: WordBank,
                 reuse_object_nouns=False,
                 limit_vocab_size_per_type: Optional[int] = None,
                 do_translate_to_nl=True,
                 log_stats=False):
        super().__init__(log_stats=log_stats)

        logger.info('-- building translator.. --')
        self._two_layered_config = self._build_two_layered_config(config_json)

        self._resolve_cache: Dict[str, List[Tuple[str, _PosFormConditionSet]]] = {}
        _resolved_translations: Dict[str, Dict[str, Dict[_PosFormConditionTuple, List[str]]]] = {}
        self._nl_to_condition: Dict[str, _PosFormConditionSet] = {}
        total_trans_nls = 0
        for prefix, config in self._two_layered_config.items():
            _resolved_translations[prefix] = {}
            pbar = tqdm(config.items())
            for key, transl_nls in pbar:
                pbar.set_description(f'resolved translations = {str(total_trans_nls).zfill(10)}')
                _resolved_translations[prefix][key] = defaultdict(list)
                for transl_nl in transl_nls:
                    for resolved_nl, condition in self._resolve_translation(transl_nl):
                        _resolved_translations[prefix][key][_PosFormConditionTuple(condition)].append(
                            resolved_nl
                        )
                        self._nl_to_condition[resolved_nl] = condition
                        total_trans_nls += 1

        self._translations: Dict[str, Dict[_PosFormConditionTuple, List[str]]] = _resolved_translations['sentence']
        # sort by specificity
        self._translations = OrderedDict((
            (key, val)
            for key, val in sorted(self._translations.items(),
                                   key=lambda key_val: calc_formula_specificity(Formula(key_val[0])))[::-1]
        ))
        logger.debug('---- loaded translations ----')
        for key, nls in self._translations.items():
            logger.debug('translation key = "%s"', key)
            for nl in nls:
                logger.debug('    "%s"', nl)

        self._reuse_object_nouns = reuse_object_nouns
        self._zeroary_predicates, self._unary_predicates, self._constants = self._load_words(word_bank)
        if limit_vocab_size_per_type is not None:
            self._zeroary_predicates = self._sample(self._zeroary_predicates, limit_vocab_size_per_type)
            self._unary_predicates = self._sample(self._unary_predicates, limit_vocab_size_per_type)
            self._constants = self._sample(self._constants, limit_vocab_size_per_type)
        self._zeroary_predicate_set = set(self._zeroary_predicates)
        self._unary_predicate_set = set(self._unary_predicates)
        self._constant_set = set(self._constants)
        self._wb = word_bank

        self._do_translate_to_nl = do_translate_to_nl

        logger.info('-- building translator done! --')

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

    def _resolve_translation(self, nl: str) -> List[Tuple[str, _PosFormConditionSet]]:
        if nl.startswith('__'):
            return []

        if nl in self._resolve_cache:
            return self._resolve_cache[nl]

        resolved_nls = [(nl, self._get_pos_form_consistency_condition(nl))]
        for template in self._extract_transl_templates(nl):
            template_prefix = '::'.join(template.split('::')[:-1])
            template_key = template.split('::')[-1]
            template_key_formula = Formula(template_key)

            template_nls = None
            template_is_found = False
            for transl_prefix, config in self._two_layered_config.items():
                if transl_prefix != template_prefix:
                    continue

                for transl_key, transl_nls in config.items():
                    transl_key_formula = Formula(transl_key)
                    if formula_can_not_be_identical_to(transl_key_formula, template_key_formula):
                        continue

                    for mapping in generate_mappings_from_formula([transl_key_formula],
                                                                  [template_key_formula]):
                        key_formula_pulled = interpret_formula(transl_key_formula, mapping)
                        if key_formula_pulled.rep == template_key_formula.rep:
                            template_nls = [interpret_formula(Formula(transl_nl), mapping).rep
                                            for transl_nl in transl_nls]
                            template_is_found = True

                    if template_is_found:
                        break

                if template_is_found:
                    break

            if not template_is_found:
                logger.warning(f'Template "{template}" not found, which appeared in "{nl}"')
                self._resolve_cache[nl] = []
                return []

            resolved_template_nls = [
                (resolved_template_nl, condition)
                for template_nl in template_nls
                for resolved_template_nl, condition in self._resolve_translation(template_nl)
            ]

            resolved_nls = [
                (
                    transl_nl.replace(
                        f'{self._TEMPLATE_BRACES[0]}{template}{self._TEMPLATE_BRACES[1]}',
                        resolved_template_nl,
                        1,
                    ),
                    self._merge_condition(parent_condition, child_condition)
                )
                for transl_nl, parent_condition in resolved_nls
                for resolved_template_nl, child_condition in resolved_template_nls
            ]

        self._resolve_cache[nl] = resolved_nls
        return resolved_nls

    def _merge_condition(self, this: _PosFormConditionSet, that: _PosFormConditionSet) -> _PosFormConditionSet:
        return this.union(that)

    def _extract_transl_templates(self, nl: str) -> Iterable[str]:
        for match in re.finditer(f'{self._TEMPLATE_BRACES[0]}((?!{self._TEMPLATE_BRACES[1]}).)*{self._TEMPLATE_BRACES[1]}', nl):
            template = nl[match.span()[0] + len(self._TEMPLATE_BRACES[0]) : match.span()[1] - len(self._TEMPLATE_BRACES[1])]
            yield template

    def _load_words(self,
                    word_bank: WordBank) -> Tuple[List[str], List[str], List[str]]:
        logger.info('loading words from WordBank ...')

        nouns = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
        })
        event_nouns = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_event_noun in word_bank.get_attrs(word)
        })
        entity_nouns = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_entity_noun in word_bank.get_attrs(word)
        })
        adjs = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.ADJ)
        })
        intransitive_verbs = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
            if ATTR.can_be_intransitive_verb in word_bank.get_attrs(word)
        })
        transitive_verbs = sorted({
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
            if ATTR.can_be_transitive_verb in word_bank.get_attrs(word)
        })

        transitive_verb_PASs = []
        for verb in self._sample(transitive_verbs, 1000):  # limit 1000 for speed
            for pred in self._sample(nouns, 1000):
                transitive_verb_PASs.append(self._pair_word_with_obj(verb, pred))

        words_per_type = 5000

        zeroary_predicates = self._sample(adjs, words_per_type)\
            + self._sample(intransitive_verbs, words_per_type)\
            + self._sample(transitive_verb_PASs, words_per_type)\
            + self._sample(event_nouns, words_per_type)
        zeroary_predicates = sorted({word for word in zeroary_predicates})

        unary_predicates = self._sample(adjs, words_per_type)\
            + self._sample(intransitive_verbs, words_per_type)\
            + self._sample(transitive_verb_PASs, words_per_type)\
            + self._sample(nouns, words_per_type)
        unary_predicates = sorted({word for word in unary_predicates})

        constants = self._sample(entity_nouns, words_per_type)

        logger.info('loading words from WordBank done!')

        return zeroary_predicates, unary_predicates, constants

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
    def acceptable_formulas(self) -> List[str]:
        return list(self._translations.keys())

    @property
    def translation_names(self) -> List[str]:
        return [self._translation_name(sentence_key, nl)
                for sentence_key, condition_config in self._translations.items()
                for condition, nls in condition_config.items()
                for nl in nls]

    def _translation_name(self, sentence_key: str, nl: str) -> str:
        return '____'.join([sentence_key, nl])

    @profile
    def _translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]], Dict[str, int]]:

        def raise_or_warn(msg: str) -> None:
            if raise_if_translation_not_found:
                raise TranslationNotFoundError(msg)
            else:
                logger.warning(msg)

        translations: List[Optional[str]] = []
        translation_names: List[Optional[str]] = []
        count_stats: Dict[str, int] = {'inflation_stats': defaultdict(int)}

        interp_mapping = self._choose_interp_mapping(formulas)

        for formula in formulas:
            # find translation key
            translation_key, push_mapping = self._find_translation_key(formula)
            if translation_key is None:
                raise_or_warn(f'translation not found for "{formula.rep}", since the translation_key was not found.')
                translations.append(None)
                translation_names.append(None)
                continue

            # find translation nls the POS and form of which is consistent with interp_mapping
            matched_condition = self._find_interp_mapping_consistent_condition(translation_key,
                                                                               push_mapping,
                                                                               interp_mapping)
            if matched_condition is None:
                msgs = [
                    f'translation not found for "{formula.rep}" the pos and word inflations of which are consistent with the following chosen interpretation mapping.',
                    'The interp_mapping is the following:',
                    '\n    ' + '\n    '.join(pformat(interp_mapping).split('\n')),
                ]

                raise_or_warn('\n'.join(msgs))
                translations.append(None)
                translation_names.append(None)
                continue
            interp_mapping_consisntent_nls = self._translations[translation_key][matched_condition]

            # Choose a translation
            _idx = random.choice(range(len(interp_mapping_consisntent_nls)))
            chosen_nl = interp_mapping_consisntent_nls[_idx]
            chosen_nl_pushed = interpret_formula(Formula(chosen_nl), push_mapping).rep

            # Generate word inflated mapping.
            inflated_mapping, _inflation_stats = self._make_word_inflated_interp_mapping(interp_mapping,
                                                                                         chosen_nl_pushed)
            if self.log_stats:
                for inflation_type, count in _inflation_stats.items():
                    count_stats['inflation_stats'][f'{inflation_type}'] = count

            interp_templated_translation_pushed_wo_info = re.sub('\[[^\]]*\]', '', chosen_nl_pushed)

            # do interpretation using predicates and constants using interp_mapping
            if self._do_translate_to_nl:
                interp_templated_translation_pushed_wo_info_with_the_or_it = self._replace_following_constants_with_the_or_it(interp_templated_translation_pushed_wo_info)
                translation = interpret_formula(Formula(interp_templated_translation_pushed_wo_info_with_the_or_it), inflated_mapping).rep
            else:
                translation = interp_templated_translation_pushed_wo_info

            translation = translation.replace('__O__', ' ')

            translations.append(translation)
            translation_names.append(self._translation_name(translation_key, chosen_nl))

        translations = [
            (self._correct_indefinite_particles(translation) if translation is not None else None)
            for translation in translations
        ]

        return list(zip(translation_names, translations)), count_stats

    @profile
    def _find_translation_key(self, formula: Formula) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        for _transl_key, _ in self._translations.items():
            if formula_can_not_be_identical_to(Formula(_transl_key), formula):  # early rejection
                continue

            for push_mapping in generate_mappings_from_formula([Formula(_transl_key)], [formula]):
                _transl_key_pushed = interpret_formula(Formula(_transl_key), push_mapping).rep
                if _transl_key_pushed == formula.rep:
                    return _transl_key, push_mapping
        return None, None

    @profile
    def _find_interp_mapping_consistent_condition(self,
                                                  sentence_key: str,
                                                  push_mapping: Dict[str, str],
                                                  interp_mapping: Dict[str, str]) -> Optional[_PosFormConditionTuple]:
        """ Find translations the pos and word inflations of which are consistent with interp_mapping """

        for condition, _ in self._translations[sentence_key].items():
            condition_is_consistent = True

            for interprand_rep, pos, form in condition:
                interprand_rep_pushed = push_mapping[interprand_rep]
                word = interp_mapping[interprand_rep_pushed]

                if pos not in self._get_pos(word):
                    condition_is_consistent = False
                    break

                inflated_word = self._get_inflated_word(word, pos, form)
                if inflated_word is None:
                    condition_is_consistent = False

            if condition_is_consistent:
                return condition

        return None

    @profile
    def _get_pos_form_consistency_condition(self, nl: str) -> _PosFormConditionSet:
        formula = Formula(nl)
        interprands = formula.predicates + formula.constants

        conditions: List[Tuple[str, POS, WordForm]] = []
        for interprand in interprands:
            pos_form = self._get_interprand_condition_from_template(interprand.rep, formula.rep)
            if pos_form is None:
                continue
            pos, form = pos_form
            conditions.append((interprand.rep, pos, form))

        return _PosFormConditionSet(conditions)

    @profile
    def _replace_following_constants_with_the_or_it(self, sentence_with_templates: str) -> str:
        constants = [c.rep for c in Formula(sentence_with_templates).constants]

        with_definite = sentence_with_templates
        for constant in constants:
            if with_definite.count(constant) < 2:
                continue

            first_pos = with_definite.find(constant)

            until_first = with_definite[:first_pos + len(constant)]
            from_second = with_definite[first_pos + len(constant):]

            if re.match(f'.*a {constant} is.*', from_second):
                replace_with_it = random.random() >= 0.5
            else:
                replace_with_it = False

            if replace_with_it:
                from_second_with_definite = re.sub(
                    f'a {constant} is',
                    'it is',
                    from_second,
                )
            else:
                from_second_with_definite = re.sub(
                    f'(.*)a (.*){constant}',
                    f'\g<1>the \g<2>{constant}',
                    from_second,
                )
            with_definite = until_first + from_second_with_definite
        if sentence_with_templates != with_definite:
            logger.info('particles "a (...) %s" are modified as:    "%s"    ->    "%s"',
                        constant,
                        sentence_with_templates,
                        with_definite)
        return with_definite

    @profile
    def _correct_indefinite_particles(self, sentence_wo_templates: str) -> str:
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
                    logger.warning('Sentence might end with particle: "%s"', sentence_wo_templates)
                    corrected_words.append(word)
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

        adj_verb_nouns = self._sample(self._unary_predicates, len(unary_predicates) * 3)
        if self._reuse_object_nouns:
            obj_nouns = [self._parse_word_with_obj(word)[1] for word in adj_verb_nouns
                         if self._parse_word_with_obj(word)[1] is not None]
        else:
            obj_nouns = []

        event_noun_size = len(zeroary_predicates) * 2
        event_nouns = [noun for noun in obj_nouns if noun in self._zeroary_predicate_set][: int(event_noun_size / 2)]
        if len(event_nouns) > 0:
            logger.info('the following object nouns may be reused as as event nouns: %s', str(event_nouns))
        event_nouns += self._sample(self._zeroary_predicates, max(event_noun_size - len(event_nouns), 0))
        event_nouns = list(set(event_nouns))

        entity_noun_size = len(constants) * 2
        entity_nouns = [noun for noun in obj_nouns if noun in self._constant_set][: int(entity_noun_size / 2)]
        if len(entity_nouns) > 0:
            logger.info('the following object nouns may be reused as as entity nouns: %s', str(entity_nouns))
        entity_nouns += self._sample(self._constants, max(entity_noun_size - len(entity_nouns), 0))
        entity_nouns = list(set(entity_nouns))

        # zero-ary predicate {A}, which appears as ".. {A} i ..", shoud be Noun.
        zeroary_mapping = next(
            generate_mappings_from_predicates_and_constants(
                zeroary_predicates,
                [],
                event_nouns,
                [],
                shuffle=True,
                allow_many_to_one=False,
            )
        )

        # Unary predicate {A}, which appears as "{A}{a}", shoud be adjective or verb.
        unary_mapping = next(
            generate_mappings_from_predicates_and_constants(
                unary_predicates,
                constants,
                adj_verb_nouns,
                entity_nouns,
                shuffle=True,
                allow_many_to_one=False,
            )
        )

        interp_mapping = zeroary_mapping.copy()
        interp_mapping.update(unary_mapping)

        return interp_mapping

    @profile
    def _sample(self, elems: List[Any], size: int) -> List[Any]:
        if len(elems) < size:
            logger.warning('Can\'t sample %d elements. Will sample only %d elements.',
                           size,
                           len(elems))
            return random.sample(elems, len(elems))
        else:
            return random.sample(elems, size)

    @profile
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
                pos_form = self._get_interprand_condition_from_template(interprand_rep, interprand_templated_translation_pulled)
                if pos_form is None:
                    raise ValueError(f'Could not extract pos and form information about "{interprand_rep}" from "{interprand_templated_translation_pulled}"')
                pos, form = pos_form
                if self.log_stats:
                    stats[f'{pos.value}.{form.value}'] += 1
                inflated_word = self._get_inflated_word(word, pos, form)
                assert(inflated_word is not None)
            else:
                raise Exception(
                    f'Something wrong. Since we have checked in that the translation indeed exists, this program must not pass this block.  The problematic translation is "{interprand_templated_translation_pulled}" and unfound string is "{interprand_rep}["',
                )
            inflated_mapping[interprand_rep] = inflated_word
        return inflated_mapping, stats

    @profile
    def _get_interprand_condition_from_template(self, interprand: str, rep: str) -> Optional[Tuple[POS, WordForm]]:
        interprand_begin = rep.find(interprand)
        if interprand_begin < 0:
            # raise Exception(f'Information for "{interprand}" can not be extracted from "{rep}".')
            return None
        interprand_end = interprand_begin + len(interprand)

        info_begin = interprand_end
        if rep[info_begin] != '[':
            # raise Exception(f'Information for "{interprand}" can not be extracted from "{rep}".')
            return None
        info_end_offset = rep[info_begin:].find(']')
        info_end = info_begin + info_end_offset + 1

        info = rep[info_begin + 1: info_end - 1]

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

    @profile
    def _get_inflated_word(self, word: str, pos: POS, form: WordForm) -> Optional[str]:
        if pos not in self._get_pos(word):
            raise ValueError(f'the word={word} does not have pos={str(pos)}')

        if pos == POS.ADJ:
            force = True
        elif pos == POS.VERB:
            force = True
        elif pos == POS.NOUN:
            force = False
        else:
            raise ValueError()

        _word, obj = self._parse_word_with_obj(word)
        _word_inflated = self._wb.change_word_form(_word, form, force=force)
        if _word_inflated is None:
            return None
        else:
            return self._pair_word_with_obj(_word_inflated, obj)

    @profile
    def _get_pos(self, word: str) -> List[POS]:
        word, _ = self._parse_word_with_obj(word)
        return self._wb.get_pos(word)

    @profile
    def _parse_word_with_obj(self, word: str) -> Tuple[str, Optional[str]]:
        if word.find('__O__') > 0:
            if word.count('__O__') != 1:
                maybe_verb = word.split('__O__')[0]
                logger.warning('Could not parse word %s since multiple "_O_" found. return verb %s only.', word, maybe_verb)
                return maybe_verb, None
            else:
                verb, obj = word.split('__O__')
                return verb, obj
        else:
            return word, None

    @profile
    def _pair_word_with_obj(self, word: str, obj: Optional[str]) -> str:
        if obj is None:
            return word
        else:
            return '__O__'.join([word, obj])
