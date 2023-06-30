import json
from typing import List, Dict, Optional, Tuple, Union, Iterable, Any, Set, Container, Callable
from collections import OrderedDict, defaultdict
import traceback
import re
from tqdm import tqdm
import copy
import random
import re
import logging
from pprint import pformat, pprint
from functools import lru_cache
import math

from tqdm import tqdm
from FLD_generator.utils import nested_merge
from FLD_generator.formula import Formula, PREDICATES, CONSTANTS, negate, ContradictionNegationError, IMPLICATION
from FLD_generator.word_banks.base import WordBank, ATTR
from FLD_generator.interpretation import (
    generate_mappings_from_formula,
    generate_mappings_from_predicates_and_constants,
    interpret_formula,
    formula_can_not_be_identical_to,
)
from FLD_generator.utils import make_combination, chained_sampling_from_weighted_iterators
from FLD_generator.word_banks import POS, VerbForm, AdjForm, NounForm, WordForm
from FLD_generator.utils import starts_with_vowel_sound, compress, decompress, make_pretty_msg
from .base import Translator, TranslationNotFoundError, calc_formula_specificity
import kern_profiler

logger = logging.getLogger(__name__)

_SENTENCE_TRANSLATION_PREFIX = 'sentence'


class _PosFormConditionSet(set):

    def __new__(cls, elems: Iterable[Tuple[str, Optional[POS], Optional[WordForm]]]):
        keys = [elem[0] for elem in elems]
        key_set = set(keys)
        if len(key_set) < len(keys):
            raise Exception(f'Duplicated condition for found in {elems}')
        unique_elems = set(elems)
        return super().__new__(cls, unique_elems)


class _PosFormConditionTuple(tuple):

    def __new__(cls, elems: Iterable[Tuple[str, Optional[POS], Optional[WordForm]]]):
        return super().__new__(cls, sorted(elems, key=lambda key_pos_form: key_pos_form[0]))


NLAndCondition = Iterable[Tuple[str, _PosFormConditionSet]]


def _compress_nls(texts: List[str]) -> bytes:
    return compress('<<SEP>>'.join(texts))


def _decompress_nls(binary: bytes) -> List[str]:
    return decompress(binary).split('<<SEP>>')


class TemplatedTranslator(Translator):

    _TEMPLATE_BRACES = ['<<', '>>']

    def __init__(self,
                 config_json: Dict[str, Dict],
                 word_bank: WordBank,
                 use_fixed_translation: bool,
                 reused_object_nouns_max_factor=0.0,
                 limit_vocab_size_per_type: Optional[int] = None,
                 words_per_type=5000,
                 volume_to_weight: str = 'linear',
                 do_translate_to_nl=True,
                 log_stats=False):
        super().__init__(log_stats=log_stats)

        self._two_layered_config = self._build_two_layered_config(config_json)

        self._load_words_by_pos_attrs_cache: Dict[Any, set] = {}
        self._load_words_by_pos_attrs_cache_interm: Dict[Any, set] = defaultdict(set)

        self._translations: Dict[str, List[str]] = self._two_layered_config[_SENTENCE_TRANSLATION_PREFIX]
        # sort by specificity
        self._translations = OrderedDict((
            (key, val)
            for key, val in sorted(self._translations.items(),
                                   key=lambda key_val: calc_formula_specificity(Formula(key_val[0])))[::-1]
        ))
        logger.debug(make_pretty_msg(title='loaded translations', boundary_level=0))
        for key, nls in self._translations.items():
            logger.debug('translation key = "%s"', key)
            for nl in nls:
                logger.debug('    "%s"', nl)

        self.words_per_type = words_per_type

        self._word_bank = word_bank

        self.use_fixed_translation = use_fixed_translation
        self.reused_object_nouns_max_factor = reused_object_nouns_max_factor
        self._zeroary_predicates, self._unary_predicates, self._constants = self._load_words(self._word_bank)
        if limit_vocab_size_per_type is not None:
            self._zeroary_predicates = self._sample(self._zeroary_predicates, limit_vocab_size_per_type)
            self._unary_predicates = self._sample(self._unary_predicates, limit_vocab_size_per_type)
            self._constants = self._sample(self._constants, limit_vocab_size_per_type)
        self._zeroary_predicate_set = set(self._zeroary_predicates)
        self._unary_predicate_set = set(self._unary_predicates)
        self._constant_set = set(self._constants)

        if volume_to_weight == 'linear':
            self._volume_to_weight_func = lambda volume: volume
        elif volume_to_weight == 'sqrt':
            self._volume_to_weight_func = lambda volume: (math.sqrt(volume) if volume > 0 else 0)
        elif volume_to_weight == 'log10':
            self._volume_to_weight_func = lambda volume: (math.log10(volume) if volume > 0 else 0)
        elif volume_to_weight == 'inv_linear':
            self._volume_to_weight_func = lambda volume: (1.0 / volume if volume > 0 else 0)
        elif volume_to_weight.startswith('pow-'):
            ind = float(volume_to_weight.split('-')[1])
            self._volume_to_weight_func = lambda volume: (math.pow(volume, ind) if volume > 0 else 0)
        else:
            raise ValueError()

        self._do_translate_to_nl = do_translate_to_nl

    def _build_two_layered_config(self, config: Dict) -> Dict[str, Dict[str, List[str]]]:
        two_layered_config = self._completely_flatten_config(config)

        one_hierarchy_config: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        for key, val in two_layered_config.items():
            if key.startswith('__'):
                logger.info('skip key "%s"', key)
                continue
            elif key.find('::') >= 0:
                prefix = '::'.join(key.split('::')[:-1])
                transl_key = key.split('::')[-1]
            else:
                prefix = 'others'
                transl_key = key
            if transl_key.startswith('__'):
                logger.info('skip key "%s"', key)
                continue
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

    @profile
    def _load_words(self, word_bank: WordBank) -> Tuple[List[str], List[str], List[str]]:

        logger.info('loading nouns ...')
        intermediate_constant_nouns = set(word_bank.get_intermediate_constant_words())
        nouns = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if word not in intermediate_constant_nouns
        )

        event_nouns = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_event_noun in word_bank.get_attrs(word)
        )

        logger.info('loading entity nouns ...')
        entity_nouns = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
            if ATTR.can_be_entity_noun in word_bank.get_attrs(word)
        )

        logger.info('loading adjs ...')
        adjs = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.ADJ)
        )

        logger.info('loading intransitive_verbs ...')
        intransitive_verbs = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
            if ATTR.can_be_intransitive_verb in word_bank.get_attrs(word)
        )

        logger.info('loading transitive_verbs ...')
        transitive_verbs = sorted(
            word
            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
            if ATTR.can_be_transitive_verb in word_bank.get_attrs(word)
        )

        logger.info('making transitive verb and object combinations ...')
        transitive_verb_PASs = []
        for verb in self._sample(transitive_verbs, 1000):  # limit 1000 for speed
            for obj in self._sample(nouns, 1000):
                transitive_verb_PASs.append(self._pair_word_with_obj(verb, obj))

        zeroary_predicates = self._sample(adjs, self.words_per_type)\
            + self._sample(intransitive_verbs, int(self.words_per_type * 2 / 3))\
            + self._sample(transitive_verb_PASs, int(self.words_per_type * 4 / 3))\
            + self._sample(event_nouns, int(self.words_per_type))
        zeroary_predicates = sorted({word for word in zeroary_predicates})

        unary_predicates = self._sample(adjs, self.words_per_type)\
            + self._sample(intransitive_verbs, int(self.words_per_type * 2 / 3))\
            + self._sample(transitive_verb_PASs, int(self.words_per_type * 4 / 3))\
            + self._sample(nouns, int(self.words_per_type))
        unary_predicates = sorted({word for word in unary_predicates})

        constants = self._sample(entity_nouns, self.words_per_type)

        return zeroary_predicates, unary_predicates, constants

    @profile
    def _load_words_by_pos_attrs(self,
                                 word_bank: WordBank,
                                 pos: Optional[POS] = None,
                                 attrs: Optional[List[ATTR]] = None) -> Iterable[str]:
        cache_key = (id(word_bank), pos, tuple(attrs) if attrs is not None else None)
        if cache_key in self._load_words_by_pos_attrs_cache:
            yield from self._load_words_by_pos_attrs_cache[cache_key]
            return

        intermediate_cache = self._load_words_by_pos_attrs_cache_interm[cache_key]
        attrs = attrs or []
        for word in word_bank.get_words():
            if word in intermediate_cache:
                continue
            if pos is not None and pos not in word_bank.get_pos(word):  # SLOW
                continue
            if any((attr not in word_bank.get_attrs(word)
                    for attr in attrs)):
                continue
            intermediate_cache.add(word)
            yield word

        self._load_words_by_pos_attrs_cache[cache_key] = intermediate_cache

    @property
    def acceptable_formulas(self) -> List[str]:
        return list(self._translations.keys())

    @property
    def translation_names(self) -> List[str]:
        return [self._translation_name(sentence_key, nl)
                for sentence_key, nls in self._translations.items()
                for nl in nls]

    def _translation_name(self, sentence_key: str, nl: str) -> str:
        return '____'.join([sentence_key, nl])

    @profile
    def _translate(self,
                   formulas: List[Formula],
                   intermediate_constant_formulas: List[Formula],
                   raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str], Optional[Formula]]], Dict[str, int]]:

        def raise_or_warn(msg: str) -> None:
            if raise_if_translation_not_found:
                raise TranslationNotFoundError(msg)
            else:
                logger.warning(msg)

        translations: List[Optional[str]] = []
        SO_swap_formulas: List[Optional[Formula]] = []
        translation_names: List[Optional[str]] = []
        count_stats: Dict[str, int] = {'inflation_stats': defaultdict(int)}

        interpret_mapping = self._choose_interpret_mapping(formulas, intermediate_constant_formulas)

        for formula in formulas:
            # find translation key
            found_keys = 0
            is_found = False
            for translation_key, push_mapping in self._find_translation_key(formula):
                found_keys += 1

                # Choose a translation
                chosen_nl = self._sample_interpret_mapping_consistent_nl(
                    translation_key,
                    interpret_mapping,
                    push_mapping,
                    block_shuffle=not self.use_fixed_translation,
                    volume_to_weight=self._volume_to_weight_func,
                )
                if chosen_nl is None:
                    msgs = [
                        f'translation not found for "{formula.rep}" in key="{translation_key}"',
                        'The possible causes includes:',
                        f'(i) the key="{translation_key}" in config indeed have no translation',
                        '(ii) we have found translations, but the sampled interpretation mapping could not match the pos and word inflation required by the translations. The interpret_mapping is the following:',
                        '\n    ' + '\n    '.join(pformat(interpret_mapping).split('\n')),
                    ]
                    logger.info('\n'.join(msgs))
                    continue

                chosen_nl_pushed = interpret_formula(Formula(chosen_nl), push_mapping).rep

                # Generate word inflated mapping.
                inflated_mapping, _inflation_stats = self._make_word_inflated_interpret_mapping(
                    interpret_mapping,
                    chosen_nl_pushed,
                )

                if self.log_stats:
                    for inflation_type, count in _inflation_stats.items():
                        count_stats['inflation_stats'][f'{inflation_type}'] = count

                interpret_templated_translation_pushed_wo_info = re.sub('\[[^\]]*\]', '', chosen_nl_pushed)

                # do interpretation using predicates and constants using interpret_mapping
                if self._do_translate_to_nl:
                    interpret_templated_translation_pushed_wo_info_with_the_or_it = self._replace_following_constants_with_the_or_it(interpret_templated_translation_pushed_wo_info)
                    translation = interpret_formula(Formula(interpret_templated_translation_pushed_wo_info_with_the_or_it), inflated_mapping).rep
                else:
                    translation = interpret_templated_translation_pushed_wo_info

                SO_swap_formula: Optional[Formula] = None
                if len(formula.unary_PASs) == 1 and len(formula.predicates) == 1 and len(formula.constants) == 1:  # something like {A}{a}
                    constant = formula.constants[0].rep
                    predicate = formula.predicates[0].rep

                    constant_transl = interpret_mapping[constant]
                    predicate_transl = interpret_mapping[predicate]

                    predicate_transl_verb, predicate_transl_obj = self._parse_word_with_obj(predicate_transl)

                    if predicate_transl_obj is not None:
                        SO_swap_interpret_mapping = copy.deepcopy(inflated_mapping)
                        SO_swap_interpret_mapping[constant] = predicate_transl_obj
                        SO_swap_interpret_mapping[predicate] = self._pair_word_with_obj(predicate_transl_verb, constant_transl)

                        SO_swap_inflated_mapping, _ = self._make_word_inflated_interpret_mapping(
                            SO_swap_interpret_mapping,
                            chosen_nl_pushed,
                        )
                        interpret_templated_translation_pushed_wo_info_with_the_or_it = self._replace_following_constants_with_the_or_it(interpret_templated_translation_pushed_wo_info)
                        SO_swap_translation = interpret_formula(Formula(interpret_templated_translation_pushed_wo_info_with_the_or_it), SO_swap_inflated_mapping).rep

                        used_predicates = {pred.rep
                                           for formula in formulas + SO_swap_formulas
                                           if formula is not None
                                           for pred in formula.predicates}
                        used_constants = {constant.rep
                                          for formula in formulas + SO_swap_formulas
                                          if formula is not None
                                          for constant in formula.constants}
                        unused_predicate = sorted(set(PREDICATES) - set(used_predicates))[0]
                        unused_constant = sorted(set(CONSTANTS) - set(used_constants))[0]

                        if self._do_translate_to_nl:
                            SO_swap_formula = interpret_formula(formula, {predicate: unused_predicate, constant: unused_constant})
                            SO_swap_formula.translation = SO_swap_translation
                            logger.debug('make subj obj swapped translation: %s', SO_swap_translation)

                translation = translation.replace('__O__', ' ')
                translations.append(translation)

                if SO_swap_formula is not None:
                    SO_swap_formula.translation = SO_swap_formula.translation.replace('__O__', ' ')
                SO_swap_formulas.append(SO_swap_formula)

                translation_names.append(self._translation_name(translation_key, chosen_nl))
                is_found = True
                break

            if not is_found:
                if found_keys == 0:
                    raise_or_warn(f'translation not found for "{formula.rep}", since the translation_key was not found.')
                else:
                    raise_or_warn(f'translation not found for "{formula.rep}" due to the reasons stated the above: (i) or (ii).')
                translations.append(None)
                translation_names.append(None)

        # fix grammers and other stufs
        translations = [
            (self._fix_translation(translation) if translation is not None else None)
            for translation in translations
        ]

        for SO_swap_formula in SO_swap_formulas:
            if SO_swap_formula is not None and SO_swap_formula.translation is not None:
                SO_swap_formula.translation = self._fix_translation(SO_swap_formula.translation) if SO_swap_formula.translation is not None else None

        return list(zip(translation_names, translations, SO_swap_formulas)), count_stats

    def _fix_translation(self, translation: str) -> str:
        # TODO: should transfer to sub-classes since this method depends on, e.g., lanugage (en, ja)
        translation = self._correct_indefinite_particles(translation)
        translation = self._fix_pred_singularity(translation)

        return translation

    @profile
    def _correct_indefinite_particles(self, sentence_wo_templates: str) -> str:
        """ choose an appropriate indefinite particls, i.e., "a" or "an", depending on the word pronounciation """
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
        corrected_sentence = ' '.join(corrected_words)
        return corrected_sentence

    def _fix_pred_singularity(self, translation: str) -> str:
        # TODO: A and B {is, runs} => currently, we do not have ({A}{a} and {B}{a}) so that we do not this fix.
        translation_fixed = translation

        def fix_all_thing_is(translation: str, src_pred: str, dst_pred: str) -> str:
            if re.match(f'.*all .*things? {src_pred}.*', translation):
                translation_fixed = re.sub(f'(.*)all (.*)things? {src_pred}(.*)', '\g<1>all \g<2>things ' + dst_pred + '\g<3>', translation)
                return translation_fixed
            else:
                return translation

        translation_fixed = fix_all_thing_is(translation_fixed, 'is an', 'are')
        translation_fixed = fix_all_thing_is(translation_fixed, 'is a', 'are')
        translation_fixed = fix_all_thing_is(translation_fixed, 'is', 'are')

        translation_fixed = fix_all_thing_is(translation_fixed, 'was an', 'were')
        translation_fixed = fix_all_thing_is(translation_fixed, 'was a', 'were')
        translation_fixed = fix_all_thing_is(translation_fixed, 'was', 'wer')

        translation_fixed = fix_all_thing_is(translation_fixed, 'does', 'do')

        # all kind thing squashes apple -> all kind thing squash apple
        if re.match('(.*)all (.*)things? ([^ ]*)(.*)', translation_fixed):
            word_after_things = re.sub('(.*)all (.*)things? ([^ ]*)(.*)', '\g<3>', translation_fixed)
            if POS.VERB in self._word_bank.get_pos(word_after_things):
                verb_normal = self._word_bank.change_word_form(word_after_things, VerbForm.NORMAL)
                translation_fixed = re.sub('(.*)all (.*)things? ([^ ]*)(.*)', '\g<1>all \g<2>things ' + verb_normal + '\g<4>', translation_fixed)

        # target   : A and B causes C -> A and B cause C
        # negagive : A runs and it is also kind
        # def fix_A_and_B_is(translation: str, src_pred: str, dst_pred: str) -> str:
        #     if re.match(f'.*[^ ]* and [^ ]* {src_pred}.*', translation):
        #         translation_fixed = re.sub('.*([^ ]*) and ([^ ]*) {src_pred}(.*)', '\g<1>all \g<2>things ' + dst_pred + '\g<3>', translation)
        #         return translation_fixed
        #     else:
        #         return translation

        if translation_fixed != translation:
            logger.info('translation is fixed as:\norig : "%s"\nfixed: "%s"', translation, translation_fixed)

        return translation_fixed


    @profile
    def _find_translation_key(self, formula: Formula) -> Iterable[Tuple[str, Dict[str, str]]]:
        for _transl_key, _ in self._translations.items():
            if formula_can_not_be_identical_to(Formula(_transl_key), formula):  # early rejection
                continue

            for push_mapping in generate_mappings_from_formula([Formula(_transl_key)], [formula]):
                _transl_key_pushed = interpret_formula(Formula(_transl_key), push_mapping).rep
                if _transl_key_pushed == formula.rep:
                    yield _transl_key, push_mapping

    @profile
    def _sample_interpret_mapping_consistent_nl(self,
                                             sentence_key: str,
                                             interpret_mapping: Dict[str, str],
                                             push_mapping: Dict[str, str],
                                             block_shuffle=True,
                                             volume_to_weight = lambda weight: weight) -> Optional[str]:
        """ Find translations the pos and nflations of which are consistent with interpret_mapping """

        # # -------------------------------- XXX do not remove those code for debugging ------------------------------
        # query = None
        # # query = '^\({[A-Z]}{[a-z]} & {[A-Z]}{[a-z]}\) ->.*'
        # if query is not None and re.match(query, sentence_key):
        #     print('\n\n\n')
        #     print(f'================ translator resolve debugging for key = "{sentence_key}" =====================')

        #     print('\n\n\n')
        #     print('--------------------- interp mapping ---------------------')

        #     pull_mapping = {val: key for key, val in push_mapping.items()}
        #     pprint({
        #         pull_mapping[key]: val for key, val in interpret_mapping.items()
        #         if key in pull_mapping
        #     })

        #     iterator_with_volumes = [
        #         self._make_resolved_translation_sampler(transl_nl,
        #                                                 set(['::'.join([_SENTENCE_TRANSLATION_PREFIX, sentence_key])]),
        #                                                 constraint_interpret_mapping=interpret_mapping,
        #                                                 constraint_push_mapping=push_mapping,
        #                                                 block_shuffle=block_shuffle,
        #                                                 volume_to_weight=volume_to_weight,
        #                                                 check_condition=False)
        #         for transl_nl in self._translations[sentence_key]
        #     ]
        #     iterators = [iterator_with_volume[0] for iterator_with_volume in iterator_with_volumes]
        #     volumes = [iterator_with_volume[1] for iterator_with_volume in iterator_with_volumes]

        #     print('\n\n\n')
        #     print('--------------------- resolved translations ---------------------')
        #     is_target = False
        #     for resolved_nl, condition in chained_sampling_from_weighted_iterators(
        #         iterators,
        #         [volume_to_weight(volume) for volume in volumes]
        #     ):
        #         condition_is_consistent = self._interpret_mapping_is_consistent_with_condition(
        #             condition,
        #             interpret_mapping,
        #             push_mapping,
        #         )
        #         if condition_is_consistent:
        #             print('OK:  ', resolved_nl)
        #             if resolved_nl.find('a {A}[ADJ] {a}[NOUN] {B}[ADJ]') >= 0:
        #                 is_target = True
        #             if resolved_nl.startswith('a {A}[ADJ] and {B}[ADJ]'):
        #                 print('!! found')
        #                 raise
        #         else:
        #             print('NG:  ', resolved_nl)
        #         # if resolved_nl.find('a {A}[ADJ] and {B}[ADJ]') >= 0:
        #         #     break
        #     if is_target:
        #         raise

        iterator_with_volumes = [
            self._make_resolved_translation_sampler(transl_nl,
                                                    set(['::'.join([_SENTENCE_TRANSLATION_PREFIX, sentence_key])]),
                                                    constraint_interpret_mapping=interpret_mapping,
                                                    constraint_push_mapping=push_mapping,
                                                    block_shuffle=block_shuffle,
                                                    volume_to_weight=volume_to_weight)
            for transl_nl in self._translations[sentence_key]
        ]
        iterators = [iterator_with_volume[0] for iterator_with_volume in iterator_with_volumes]
        volumes = [iterator_with_volume[1] for iterator_with_volume in iterator_with_volumes]

        if block_shuffle:
            def generate():
                for resolved_nl, condition in chained_sampling_from_weighted_iterators(
                    iterators,
                    [volume_to_weight(volume) for volume in volumes]
                ):
                    yield resolved_nl, condition

        else:
            def generate():
                for iterator in iterators:
                    for resolved_nl, condition in iterator:
                        yield resolved_nl, condition

        for resolved_nl, condition in generate():

            condition_is_consistent = self._interpret_mapping_is_consistent_with_condition(
                condition,
                interpret_mapping,
                push_mapping,
            )
            assert condition_is_consistent  # the consistency should have been checked recursively.
            return resolved_nl

        return None

    @profile
    def _interpret_mapping_is_consistent_with_condition(self,
                                                     condition: _PosFormConditionSet,
                                                     interpret_mapping: Dict[str, str],
                                                     push_mapping: Dict[str, str]) -> bool:
        condition_is_consistent = True
        for interprand_rep, pos, form in condition:
            interprand_rep_pushed = push_mapping[interprand_rep]
            word = interpret_mapping[interprand_rep_pushed]

            if pos not in self._get_pos(word):
                condition_is_consistent = False
                break

            inflated_word = self._get_inflated_word(word, pos, form)
            if inflated_word is None:
                condition_is_consistent = False
                break

        return condition_is_consistent

    @profile
    def _make_resolved_translation_sampler(self,
                                           nl: str,
                                           ancestor_keys: Set[str],
                                           constraint_interpret_mapping: Optional[Dict[str, str]] = None,
                                           constraint_push_mapping: Optional[Dict[str, str]] = None,
                                           block_shuffle=True,
                                           volume_to_weight = lambda volume: volume,
                                           check_condition=True) -> Tuple[Iterable[NLAndCondition], int]:
        if nl.startswith('__'):
            return iter([]), 0

        condition = self._get_pos_form_consistency_condition(nl)
        if constraint_push_mapping is not None\
                and check_condition\
                and not self._interpret_mapping_is_consistent_with_condition(condition,
                                                                          constraint_interpret_mapping,
                                                                          constraint_push_mapping):
            return iter([]), 0

        templates = list(self._extract_templates(nl))
        if len(templates) == 0:
            volume = 1

            def generate():
                yield nl, condition
        else:
            class ResolveTemplateGenerator:

                def __init__(self, parent_translator: TemplatedTranslator, template: str):
                    self._template = template
                    self._parent_translator = parent_translator
                    self.volume = self._resolve()[1]

                def __call__(self) -> Iterable[NLAndCondition]:
                    return self._resolve()[0]

                def _resolve(self) -> Tuple[Iterable[NLAndCondition], int]:
                    return self._parent_translator._make_resolved_template_sampler(
                        self._template,
                        ancestor_keys,
                        constraint_interpret_mapping=constraint_interpret_mapping,
                        constraint_push_mapping=constraint_push_mapping,
                        shuffle=block_shuffle,
                        volume_to_weight=volume_to_weight,
                        check_condition=check_condition,
                    )

            template_resolve_generators = [ResolveTemplateGenerator(self, template) for template in templates]

            volumes = [generator.volume for generator in template_resolve_generators]
            volume = 1
            for _volume in volumes:
                volume *= _volume

            def generate():
                for combination in make_combination(template_resolve_generators):
                    template_updated_condition = condition.copy()
                    template_resolved_nl = nl

                    for template, (resolved_template, template_condition) in zip(templates, combination):
                        template_resolved_nl = template_resolved_nl.replace(
                            f'{self._TEMPLATE_BRACES[0]}{template}{self._TEMPLATE_BRACES[1]}',
                            resolved_template,
                            1,
                        )
                        template_updated_condition = self._merge_condition(template_updated_condition, template_condition)

                    yield template_resolved_nl, template_updated_condition

        return generate(), volume

    @profile
    def _make_resolved_template_sampler(self,
                                        template: str,
                                        ancestor_keys: Set[str],
                                        constraint_interpret_mapping: Optional[Dict[str, str]] = None,
                                        constraint_push_mapping: Optional[Dict[str, str]] = None,
                                        shuffle=True,
                                        volume_to_weight = lambda volume: volume,
                                        check_condition=True) -> Tuple[Iterable[NLAndCondition], int]:
        template_key, template_nls = self._find_template_nls(template, tuple(sorted(ancestor_keys)))
        if template_key is None:
            raise Exception(f'template for {template} not found.')
        iterator_with_volumes = [self._make_resolved_translation_sampler(template_nl,
                                                                         ancestor_keys.union(set([template_key])),
                                                                         constraint_interpret_mapping=constraint_interpret_mapping,
                                                                         constraint_push_mapping=constraint_push_mapping,
                                                                         block_shuffle=shuffle,
                                                                         volume_to_weight=volume_to_weight,
                                                                         check_condition=check_condition)
                                 for template_nl in template_nls]
        iterators = [iterator_with_volume[0] for iterator_with_volume in iterator_with_volumes]
        volumes = [iterator_with_volume[1] for iterator_with_volume in iterator_with_volumes]
        volume_sum = sum(volumes)

        if shuffle:
            def generate():
                for resolved_template_nl, condition in chained_sampling_from_weighted_iterators(
                    iterators,
                    [volume_to_weight(volume) for volume in volumes]
                ):
                    yield resolved_template_nl, condition

        else:
            def generate():
                for iterator in iterators:
                    for resolved_template_nl, condition in iterator:
                        yield resolved_template_nl, condition

        return generate(), volume_sum

    @lru_cache(maxsize=1000000)
    def _find_template_nls(self, template: str, ancestor_keys: Tuple[str]) -> Tuple[Optional[str], Optional[List[str]]]:
        ancestor_keys_set = set(ancestor_keys)

        template_prefix = '::'.join(template.split('::')[:-1])
        template_key = template.split('::')[-1]
        template_key_formula = Formula(template_key)

        found_template_nls = None
        found_template_key = None

        config = self._two_layered_config[template_prefix]
        for transl_key, transl_nls in config.items():
            if transl_key in ancestor_keys_set:  # prevent circular reference
                continue

            key_formula = Formula(transl_key)
            if formula_can_not_be_identical_to(key_formula, template_key_formula):
                continue

            for mapping in generate_mappings_from_formula([key_formula],
                                                          [template_key_formula]):
                key_formula_pulled = interpret_formula(key_formula, mapping)
                if key_formula_pulled.rep == template_key_formula.rep:
                    found_template_key = transl_key
                    found_template_nls = [interpret_formula(Formula(transl_nl), mapping).rep
                                          for transl_nl in transl_nls]
                    break

            if found_template_nls is not None:
                break

        return (
            '::'.join([template_prefix, found_template_key]) if found_template_key is not None else None,
            found_template_nls,
        )

    def _merge_condition(self, this: _PosFormConditionSet, that: _PosFormConditionSet) -> _PosFormConditionSet:
        return this.union(that)

    def _extract_templates(self, nl: str) -> Iterable[str]:
        for match in re.finditer(f'{self._TEMPLATE_BRACES[0]}((?!{self._TEMPLATE_BRACES[1]}).)*{self._TEMPLATE_BRACES[1]}', nl):
            template = nl[match.span()[0] + len(self._TEMPLATE_BRACES[0]) : match.span()[1] - len(self._TEMPLATE_BRACES[1])]
            yield template

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
    def _choose_interpret_mapping(self, formulas: List[Formula], intermediate_constant_formulas: List[Formula]) -> Dict[str, str]:
        zeroary_predicates = list({predicate.rep
                                   for formula in formulas
                                   for predicate in formula.zeroary_predicates})
        unary_predicates = list({predicate.rep
                                 for formula in formulas
                                 for predicate in formula.unary_predicates})
        constants = list({constant.rep for formula in formulas for constant in formula.constants})
        intermediate_constants = sorted({constant.rep for constant in intermediate_constant_formulas})

        adj_verb_nouns = self._sample(self._unary_predicates, len(unary_predicates) * 3)  # we sample more words so that we have more chance of POS/FORM condition matching.
        if self.reused_object_nouns_max_factor > 0.0:
            obj_nouns = list({
                self._parse_word_with_obj(word)[1]
                for word in adj_verb_nouns
                if self._parse_word_with_obj(word)[1] is not None
            })
        else:
            obj_nouns = []

        event_noun_size = int(len(zeroary_predicates) * 2.0)
        event_nouns = self._sample(self._zeroary_predicates, max(event_noun_size, 0))

        entity_noun_size = int(math.ceil(len(constants) * 1.0))   # since all the constants have pos=NOUN, x 1.0 is enough
        while True:
            entity_nouns = [noun for noun in obj_nouns if noun in self._constant_set][: int(entity_noun_size * self.reused_object_nouns_max_factor)]
            if len(entity_nouns) > 0:
                logger.info('the following object nouns may be reused as as entity nouns: %s', str(entity_nouns))

            sampled_constants = self._sample(self._constants, max((entity_noun_size - len(entity_nouns)) * 5, 0))
            for constant in sampled_constants:
                if len(entity_nouns) >= entity_noun_size:
                    break
                if constant not in entity_nouns:
                    entity_nouns.append(constant)

            if len(entity_nouns) >= entity_noun_size:
                break

        intermediate_constant_nouns = sorted(self._word_bank.get_intermediate_constant_words())[:len(intermediate_constants)]

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
        try:
            unary_mapping = next(
                generate_mappings_from_predicates_and_constants(
                    unary_predicates,
                    constants,
                    adj_verb_nouns,
                    entity_nouns,
                    shuffle=True,
                    allow_many_to_one=False,
                    constraints={
                        intermediate_constant: intermediate_constant_noun
                        for intermediate_constant, intermediate_constant_noun in zip(intermediate_constants, intermediate_constant_nouns)
                    }
                )
            )
        except:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(unary_predicates)
            print(constants)
            print(adj_verb_nouns)
            print(entity_nouns)
            print(traceback.format_exc())
            raise

        interpret_mapping = zeroary_mapping.copy()
        interpret_mapping.update(unary_mapping)

        return interpret_mapping

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
    def _make_word_inflated_interpret_mapping(self,
                                           interpret_mapping: Dict[str, str],
                                           interprand_templated_translation_pushed: str) -> Tuple[Dict[str, str], Dict[str, int]]:
        inflated_mapping = {}
        stats = defaultdict(int)

        for interprand_formula in Formula(interprand_templated_translation_pushed).predicates\
                + Formula(interprand_templated_translation_pushed).constants:
            interprand_rep = interprand_formula.rep
            if interprand_templated_translation_pushed.find(f'{interprand_rep}[') >= 0:
                word = interpret_mapping[interprand_rep]
                pos_form = self._get_interprand_condition_from_template(interprand_rep, interprand_templated_translation_pushed)
                if pos_form is None:
                    raise ValueError(f'Could not extract pos and form information about "{interprand_rep}" from "{interprand_templated_translation_pushed}"')
                pos, form = pos_form
                if self.log_stats:
                    stats[f'{pos.value}.{form.value}'] += 1
                inflated_word = self._get_inflated_word(word, pos, form)
                assert(inflated_word is not None)
            else:
                raise Exception(
                    f'Something wrong. Since we have checked in that the translation indeed exists, this program must not pass this block.  The problematic translation is "{interprand_templated_translation_pushed}" and unfound string is "{interprand_rep}["',
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

    @lru_cache(maxsize=1000000)
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
        _word_inflated = self._word_bank.change_word_form(_word, form, force=force)
        if _word_inflated is None:
            return None
        else:
            return self._pair_word_with_obj(_word_inflated, obj)

    @lru_cache(maxsize=1000000)
    def _get_pos(self, word: str) -> List[POS]:
        word, obj = self._parse_word_with_obj(word)
        if obj is not None:
            POSs = self._word_bank.get_pos(word)
            assert POS.VERB in POSs
            return [POS.VERB]
        else:
            return self._word_bank.get_pos(word)

    @lru_cache(maxsize=1000000)
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

    @lru_cache(maxsize=1000000)
    def _pair_word_with_obj(self, word: str, obj: Optional[str]) -> str:
        if obj is None:
            return word
        else:
            return '__O__'.join([word, obj])


def build(config_paths: List[str],
          word_bank: WordBank,
          use_fixed_translation=False,
          reused_object_nouns_max_factor=0.0,
          limit_vocab_size_per_type: Optional[int] = None,
          volume_to_weight: str = 'linear',
          do_translate_to_nl=True):

    merged_config_json = {}
    for config_path in config_paths:
        merged_config_json = nested_merge(merged_config_json,
                                          json.load(open(config_path)))

    translator = TemplatedTranslator(
        merged_config_json,
        word_bank,
        use_fixed_translation=use_fixed_translation,
        reused_object_nouns_max_factor=reused_object_nouns_max_factor,
        limit_vocab_size_per_type=limit_vocab_size_per_type,
        volume_to_weight=volume_to_weight,
        do_translate_to_nl=do_translate_to_nl,
    )
    return translator
