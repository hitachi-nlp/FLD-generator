from abc import abstractmethod
from typing import List, Dict, Optional, Tuple, Iterable, Any, Set, Callable, Union, Generator, Iterator
from collections import OrderedDict, defaultdict
import statistics
import re
import copy
import random
import logging
from pprint import pformat
from functools import lru_cache
import math

from FLD_generator.formula import Formula, PREDICATES, CONSTANTS, remove_outer_brace
from FLD_generator.word_banks.base import WordBank, ATTR
from FLD_generator.interpretation import (
    generate_mappings_from_formula,
    generate_mappings_from_predicates_and_constants,
    interpret_formula,
    formula_can_not_be_identical_to,
)
from FLD_generator.word_banks import POS
from FLD_generator.utils import (
    compress,
    decompress,
    make_pretty_msg,
    chained_sampling_from_weighted_iterators,
    make_combination,
    shuffle,
    RandomCycle,
)
from FLD_generator.knowledge_banks.base import KnowledgeBankBase
from .base import (
    Translator,
    TranslationNotFoundError,
    calc_formula_specificity,
    Phrase,
    PredicatePhrase,
    ConstantPhrase,
)
import line_profiling

logger = logging.getLogger(__name__)

_SENTENCE_TRANSLATION_PREFIX = 'sentence'
_DEBUG = False


class _PosFormConditionSet(set):

    def __new__(cls, elems: Iterable[Tuple[str, Optional[POS], Optional[str]]]):
        keys = [elem[0] for elem in elems]
        key_set = set(keys)
        if len(key_set) < len(keys):
            raise Exception(f'Duplicated condition for found in {elems}')
        unique_elems = set(elems)
        return super().__new__(cls, unique_elems)


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
                 # words_per_type=5000,
                 volume_to_weight: str = 'log10',
                 default_weight_factor_type='W_VOL__1.0',
                 do_translate_to_nl=True,
                 adj_verb_noun_ratio: Optional[List] = None,
                 knowledge_bank: Optional[KnowledgeBankBase] = None,
                 log_stats=False):
        super().__init__(log_stats=log_stats)

        self._default_weight_factor_type = default_weight_factor_type
        self._two_layered_config = self._build_two_layered_config(config_json)

        self._load_words_by_pos_attrs_cache: Dict[Any, set] = {}
        self._load_words_by_pos_attrs_cache_interm: Dict[Any, set] = defaultdict(set)

        self._translations: Dict[str, List[Tuple[str, str]]] = self._two_layered_config[_SENTENCE_TRANSLATION_PREFIX]
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

        # self.words_per_type = words_per_type

        self._word_bank = word_bank

        self.use_fixed_translation = use_fixed_translation
        self.reused_object_nouns_max_factor = reused_object_nouns_max_factor
        self._zeroary_predicates, self._unary_predicates, self._constants = self._load_phrases(
            self._word_bank, adj_verb_noun_ratio=adj_verb_noun_ratio)
        if limit_vocab_size_per_type is not None:
            self._zeroary_predicates = self._sample(self._zeroary_predicates, limit_vocab_size_per_type)
            self._unary_predicates = self._sample(self._unary_predicates, limit_vocab_size_per_type)
            self._constants = self._sample(self._constants, limit_vocab_size_per_type)
        self._constant_set = set(self._constants)

        if volume_to_weight == 'linear':
            self._volume_to_weight_func = lambda volume: volume
        elif volume_to_weight == 'sqrt':
            self._volume_to_weight_func = lambda volume: (math.sqrt(volume) if volume > 0 else 0)
        elif volume_to_weight == 'logE':
            self._volume_to_weight_func = lambda volume: (1 + math.log(volume) if volume > 0 else 0)
        elif volume_to_weight == 'log10':
            self._volume_to_weight_func = lambda volume: (1 + math.log10(volume) if volume > 0 else 0)
        elif volume_to_weight == 'inv_linear':
            self._volume_to_weight_func = lambda volume: (1.0 / volume if volume > 0 else 0)
        elif volume_to_weight.startswith('pow-'):
            ind = float(volume_to_weight.split('-')[1])
            self._volume_to_weight_func = lambda volume: (math.pow(volume, ind) if volume > 0 else 0)
        else:
            raise ValueError()

        self._do_translate_to_nl = do_translate_to_nl

        self._knowledge_bank = knowledge_bank

    def _build_two_layered_config(self, config: Dict) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
        flat_config = self._completely_flatten_config(config)

        two_layered_config: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        for key, val in flat_config.items():
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
            two_layered_config[prefix][transl_key] = val
        return two_layered_config

    def _completely_flatten_config(self, config: Dict) -> Dict[str, List[Tuple[float, str]]]:
        flat_config = {}
        for key, val in config.items():
            if isinstance(val, list):
                children = []
                for child in val:
                    if isinstance(child, list):
                        if not len(child) == 2:
                            raise ValueError('invalid template {str(child)}')
                        children.append(tuple(child))
                    else:
                        if not isinstance(child, str):
                            raise ValueError('invalid template {str(child)}')
                        children.append((self._default_weight_factor_type, child))
                flat_config[key] = children

            elif isinstance(val, dict):
                for child_key, child_val in self._completely_flatten_config(val).items():
                    flat_config[f'{key}::{child_key}'] = child_val

            else:
                raise ValueError()

        return flat_config

    @profile
    def _load_phrases(self,
                      word_bank: WordBank,
                      adj_verb_noun_ratio: Optional[List[float]] = None,
                      # prioritize_form_abundant_words=False,
                      ) -> Tuple[Iterable[PredicatePhrase], Iterable[PredicatePhrase], List[ConstantPhrase]]:

        logger.info('loading nouns ...')
        intermediate_constant_nouns = set(word_bank.get_intermediate_constant_words())
        nouns = [word
                 for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
                 if word not in intermediate_constant_nouns]
        event_nouns = [word
                       for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
                       if ATTR.can_be_event_noun in word_bank.get_attrs(word)]

        logger.info('loading entity nouns ...')
        entity_nouns = [word
                        for word in self._load_words_by_pos_attrs(word_bank, pos=POS.NOUN)
                        if ATTR.can_be_entity_noun in word_bank.get_attrs(word)]

        logger.info('loading adjs ...')
        adjs = [word
                for word in self._load_words_by_pos_attrs(word_bank, pos=POS.ADJ)]

        logger.info('loading intransitive_verbs ...')
        intransitive_verbs = [word
                              for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
                              if ATTR.can_be_intransitive_verb in word_bank.get_attrs(word)]

        logger.info('loading transitive_verbs ...')
        transitive_verbs = [word
                            for word in self._load_words_by_pos_attrs(word_bank, pos=POS.VERB)
                            if ATTR.can_be_transitive_verb in word_bank.get_attrs(word)]

        logger.info('making transitive verb and object combinations ...')

        @profile
        def build_transitive_verb_PASs() -> Iterable[Tuple[str, str]]:
            _transitive_verbs = shuffle(transitive_verbs)
            _nouns = shuffle(nouns)
            for i in range(min(len(_transitive_verbs), len(_nouns))):
                verb = _transitive_verbs[i]
                obj = _nouns[i]
                # yield pair_pred_with_obj_mdf(verb, obj, None)
                # yield PredicatePhrase(predicate=verb, object=obj)
                yield verb, obj

        if adj_verb_noun_ratio is not None and len(adj_verb_noun_ratio) != 3:
            raise ValueError()
        adj_verb_noun_ratio = adj_verb_noun_ratio or [1, 2, 1]
        adj_verb_noun_weight = [3 * ratio / sum(adj_verb_noun_ratio) for ratio in adj_verb_noun_ratio]

        zeorary_word_weights = (adj_verb_noun_weight[0], adj_verb_noun_weight[1] * 1 / 3, adj_verb_noun_weight[0] * 2 / 3, adj_verb_noun_weight[2])
        zeroary_predicates = chained_sampling_from_weighted_iterators(
            (RandomCycle(adjs), RandomCycle(intransitive_verbs), RandomCycle(build_transitive_verb_PASs, shuffle=False), RandomCycle(event_nouns)),
            zeorary_word_weights,
        )

        unary_word_weights = (adj_verb_noun_weight[0], adj_verb_noun_weight[1] * 1 / 3, adj_verb_noun_weight[0] * 2 / 3, adj_verb_noun_weight[2])
        unary_predicates = chained_sampling_from_weighted_iterators(
            (RandomCycle(adjs), RandomCycle(intransitive_verbs), RandomCycle(build_transitive_verb_PASs, shuffle=False), RandomCycle(nouns)),
            unary_word_weights,
        )

        constants = entity_nouns

        return (
            (PredicatePhrase(predicate=pred[0], object=pred[1]) if isinstance(pred, tuple) else PredicatePhrase(predicate=pred) for pred in  zeroary_predicates),
            (PredicatePhrase(predicate=pred[0], object=pred[1]) if isinstance(pred, tuple) else PredicatePhrase(predicate=pred) for pred in  unary_predicates),
            [ConstantPhrase(constant) for constant in constants],
        )

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
            if pos is not None and pos not in word_bank.get_pos(word, not_found_warning=False):
                continue
            if any(attr not in word_bank.get_attrs(word)
                   for attr in attrs):
                continue
            intermediate_cache.add(word)
            yield word

        self._load_words_by_pos_attrs_cache[cache_key] = intermediate_cache

    @property
    def acceptable_formulas(self) -> List[str]:
        return list(self._translations.keys())

    # def is_acceptable(self, formulas: List[Formula]) -> List[str]:
    #     return all(formula.rep in self.acceptable_formulas
    #                for formula in formulas)

    @property
    def translation_names(self) -> List[str]:
        return [self._translation_name(sentence_key, weighted_nl[1])
                for sentence_key, nls in self._translations.items()
                for weighted_nl in nls]

    def _translation_name(self, sentence_key: str, nl: str) -> str:
        return '____'.join([sentence_key, nl])

    @profile
    def _translate(self,
                   formulas: List[Formula],
                   intermediate_constant_formulas: List[Formula],
                   knowledge_injection_idxs: Optional[List[int]] = None,
                   raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str], Optional[Formula], bool]], Dict[str, int]]:
        knowledge_injection_idxs = knowledge_injection_idxs or []
        self._reset_predicate_phrase_assets()

        def raise_or_warn(msg: str) -> None:
            if raise_if_translation_not_found:
                raise TranslationNotFoundError(msg)
            else:
                logger.warning(msg)

        translations: List[Optional[str]] = []
        SO_swap_formulas: List[Optional[Formula]] = []
        translation_names: List[Optional[str]] = []
        count_stats: Dict[str, int] = {'inflation_stats': defaultdict(int)}

        if len(knowledge_injection_idxs) > 0:
            if self._knowledge_bank is None:
                raise ValueError()
            should_knowledge_formulas = [formulas[idx] for idx in knowledge_injection_idxs]
            if not self._knowledge_bank.is_acceptable(should_knowledge_formulas):
                raise ValueError('The following formulas can not be translated with knowledge: %s', str(should_knowledge_formulas))
            (
                knowledge_injection_mapping,
                knowledge_pos_mapping,
                _is_knowledge_injected,
            ) = self._choose_interpret_mapping(should_knowledge_formulas,
                                               [],
                                               from_knowledge=True)
            knowledge_formulas = [formula
                                    for i, (formula, is_injected) in enumerate(zip(should_knowledge_formulas, _is_knowledge_injected))
                                    if is_injected]
            is_knowledge_injected = [True if formula in knowledge_formulas else False
                                       for formula in formulas]

        else:
            knowledge_injection_mapping = {}
            knowledge_pos_mapping = {}
            is_knowledge_injected = [False] * len(formulas)

        interpret_mapping = self._choose_interpret_mapping(formulas,
                                                           intermediate_constant_formulas,
                                                           constraints=knowledge_injection_mapping)
        force_pos_mapping = knowledge_pos_mapping

        for formula, _is_knowledge_injected in zip(formulas, is_knowledge_injected):
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
                    force_pos_mapping=force_pos_mapping,
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
                inflated_mapping, _inflation_stats = self._make_phrase_inflated_interpret_mapping(
                    interpret_mapping,
                    chosen_nl_pushed,
                )

                if self.log_stats:
                    for inflation_type, count in _inflation_stats.items():
                        count_stats['inflation_stats'][f'{inflation_type}'] = count

                interpret_templated_translation_pushed = re.sub('\[[^\]]*\]', '', chosen_nl_pushed)

                # do interpretation using predicates and constants using interpret_mapping
                if self._do_translate_to_nl:
                    interpret_templated_translation_pushed_with_the_or_it = self._postprocess_template(interpret_templated_translation_pushed)
                    translation = interpret_formula(Formula(interpret_templated_translation_pushed_with_the_or_it),
                                                    self._make_phrase_str_mapping(inflated_mapping)).rep
                else:
                    translation = interpret_templated_translation_pushed

                SO_swap_formula: Optional[Formula] = None
                if len(formula.unary_PASs) == 1 and len(formula.predicates) == 1 and len(formula.constants) == 1:  # something like {A}{a}
                    constant = formula.constants[0].rep
                    predicate = formula.predicates[0].rep

                    constant_transl = interpret_mapping[constant]
                    predicate_transl = interpret_mapping[predicate]

                    if predicate_transl.object is not None:
                        SO_swap_interpret_mapping = copy.deepcopy(inflated_mapping)
                        SO_swap_interpret_mapping[constant] = ConstantPhrase(constant=predicate_transl.object)
                        SO_swap_interpret_mapping[predicate] = PredicatePhrase(predicate=predicate_transl.predicate,
                                                                               object=constant_transl,
                                                                               right_modifier=predicate_transl.right_modifier,
                                                                               left_modifier=predicate_transl.left_modifier)

                        SO_swap_inflated_mapping, _ = self._make_phrase_inflated_interpret_mapping(
                            SO_swap_interpret_mapping,
                            chosen_nl_pushed,
                        )
                        interpret_templated_translation_pushed_with_the_or_it = self._postprocess_template(interpret_templated_translation_pushed)
                        SO_swap_translation = interpret_formula(Formula(interpret_templated_translation_pushed_with_the_or_it),
                                                                self._make_phrase_str_mapping(SO_swap_inflated_mapping)).rep

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

                # translation = self._make_predicate_phrase_str(translation)
                translations.append(translation)

                # if SO_swap_formula is not None:
                #     SO_swap_formula.translation = self._make_predicate_phrase_str(SO_swap_formula.translation)
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
            (self._postprocess_translation(translation,
                                           is_knowledge_injected=_is_knowledge_injected) if translation is not None else None)
            for translation, _is_knowledge_injected in zip(translations, is_knowledge_injected)
        ]

        for SO_swap_formula in SO_swap_formulas:
            if SO_swap_formula is not None and SO_swap_formula.translation is not None:
                SO_swap_formula.translation = (
                    self._postprocess_translation(SO_swap_formula.translation, is_knowledge_injected=False) if SO_swap_formula.translation is not None
                    else None)

        return list(zip(translation_names, translations, SO_swap_formulas, is_knowledge_injected)), count_stats

    def is_knowledge_translatable(self, formulas: List[Formula]) -> bool:
        return self._knowledge_bank.is_acceptable(formulas)

    # @profile
    def _find_translation_key(self, formula: Formula) -> Iterable[Tuple[str, Dict[str, str]]]:
        for _remove_outer_brace in [False, True]:
            if _remove_outer_brace:
                _formula = remove_outer_brace(formula)
            else:
                _formula = formula
            for _transl_key, _ in self._translations.items():
                if formula_can_not_be_identical_to(Formula(_transl_key), _formula):  # early rejection
                    continue

                for push_mapping in generate_mappings_from_formula([Formula(_transl_key)], [_formula]):
                    _transl_key_pushed = interpret_formula(Formula(_transl_key), push_mapping).rep
                    if _transl_key_pushed == _formula.rep:
                        yield _transl_key, push_mapping

    # @profile
    def _sample_interpret_mapping_consistent_nl(self,
                                                sentence_key: str,
                                                interpret_mapping: Dict[str, Phrase],
                                                push_mapping: Dict[str, str],
                                                force_pos_mapping: Optional[Dict[str, str]] = None,
                                                block_shuffle=True,
                                                volume_to_weight = lambda weight: weight,
                                                log_indent=0) -> Optional[str]:
        """ Find translations the pos and nflations of which are consistent with interpret_mapping """
        if _DEBUG:
            print()
            print(' ' * log_indent + '**** _sample_interpret_mapping_consistent_nl() ****')
            print(' ' * log_indent + '    sentence_key:', sentence_key)

        iterators = []
        weight_types: List[str] = []
        volumes: List[int] = []
        for weight_type, transl_nl in self._translations[sentence_key]:
            iterator_with_volume = self._make_resolved_translation_sampler(  # SLOW
                transl_nl,
                # set(['::'.join([_SENTENCE_TRANSLATION_PREFIX, sentence_key])]),
                set([transl_nl]),
                constraint_interpret_mapping=interpret_mapping,
                constraint_force_pos_mapping=force_pos_mapping,
                constraint_push_mapping=push_mapping,
                block_shuffle=block_shuffle,
                volume_to_weight=volume_to_weight,
                log_indent = log_indent + 4,
            )

            iterators.append(iterator_with_volume[0])
            weight_types.append(weight_type)
            volumes.append(iterator_with_volume[1])

        if block_shuffle:

            volume_weights = [volume_to_weight(volume) for volume in volumes]
            weights = [self._get_weight_factor_func(weight_type)(volume_weights, i_iterator)
                       for i_iterator, weight_type in enumerate(weight_types)]

            # @profile
            def generate():
                for resolved_nl, condition in chained_sampling_from_weighted_iterators(
                    iterators,
                    weights,
                ):
                    yield resolved_nl, condition

        else:
            # @profile
            def generate():
                for iterator in iterators:
                    for resolved_nl, condition in iterator:
                        yield resolved_nl, condition

        for resolved_nl, condition in generate():   # SLOW

            condition_is_consistent = self._interpret_mapping_is_consistent_with_condition(
                condition,
                interpret_mapping,
                push_mapping,
                force_pos_mapping=force_pos_mapping,
            )
            assert condition_is_consistent  # the consistency should have been checked recursively.
            return resolved_nl

        return None

    @lru_cache(maxsize=100000)
    def _get_weight_factor_func(self, type_: str) -> Callable[[List[float], int], float]:
        """

        examples of type_
            "W_VOL__1.0"
            "W_VOL_AVG__0.1"
        """
        volume_weight_agg, factor = type_.split('__')

        _factor = float(factor)

        if volume_weight_agg == 'W_VOL':

            def agg_volume_weights(volume_weights: List[float], i: int) -> float:
                return volume_weights[i]

        elif volume_weight_agg == 'W_VOL_AVG':

            def agg_volume_weights(volume_weights: List[float], i: int) -> float:
                if len(volume_weights) == 1:
                    return volume_weights[i]
                else:
                    other_avg = statistics.mean(volume_weights[j] for j in range(len(volume_weights))
                                                if j != i)
                    return other_avg

        else:
            raise ValueError(f'Unknown volume weight aggregation type "{volume_weight_agg}"')

        def get_weight(volume_weights: List[float], i: int) -> float:
            return agg_volume_weights(volume_weights, i) * _factor

        return get_weight

    # @profile
    def _make_resolved_translation_sampler(self,
                                           nl: str,
                                           # ancestor_keys: Set[str],
                                           ancestor_nls: Set[str],
                                           constraint_interpret_mapping: Optional[Dict[str, Phrase]] = None,
                                           constraint_force_pos_mapping: Optional[Dict[str, str]] = None,
                                           constraint_push_mapping: Optional[Dict[str, str]] = None,
                                           block_shuffle=True,
                                           volume_to_weight = lambda volume: volume,
                                           check_condition=True,
                                           log_indent=0) -> Tuple[Iterable[NLAndCondition], int]:
        # SLOW due to the many calls
        if _DEBUG:
            print()
            print(' ' * log_indent + '== _make_resolved_translation_sampler() ==')
            print(' ' * log_indent + '    nl:', nl)
            # print(' ' * log_indent + '    ancestor_keys:', ancestor_keys)
            print(' ' * log_indent + '    ancestor_nls:', ancestor_nls)
        if nl.startswith('__'):
            return iter([]), 0

        condition = self._get_pos_form_consistency_condition(nl)  # SLOW
        if constraint_push_mapping is not None\
                and check_condition\
                and not self._interpret_mapping_is_consistent_with_condition(condition,
                                                                             constraint_interpret_mapping,
                                                                             constraint_push_mapping,
                                                                             force_pos_mapping=constraint_force_pos_mapping):
            return iter([]), 0

        templates = list(self._extract_templates(nl))
        if len(templates) == 0:
            volume = 1

            def generate():
                yield nl, condition

        else:

            class ResolveTemplateGenerator:

                # # @profile
                def __init__(self, parent_translator: TemplatedTranslator, template: str):
                    self._template = template
                    self._parent_translator = parent_translator
                    self.volume = self._resolve()[1]

                # # @profile
                def __call__(self) -> Iterable[NLAndCondition]:
                    return self._resolve()[0]

                # # @profile
                def _resolve(self) -> Tuple[Iterable[NLAndCondition], int]:
                    return self._parent_translator._make_resolved_template_sampler(
                        self._template,
                        # ancestor_keys,
                        ancestor_nls,
                        constraint_interpret_mapping=constraint_interpret_mapping,
                        constraint_force_pos_mapping=constraint_force_pos_mapping,
                        constraint_push_mapping=constraint_push_mapping,
                        shuffle=block_shuffle,
                        volume_to_weight=volume_to_weight,
                        check_condition=check_condition,
                        log_indent = log_indent + 4
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

    # @profile
    def _make_resolved_template_sampler(self,
                                        template: str,
                                        # ancestor_keys: Set[str],
                                        ancestor_nls: Set[str],
                                        constraint_interpret_mapping: Optional[Dict[str, Phrase]] = None,
                                        constraint_force_pos_mapping: Optional[Dict[str, str]] = None,
                                        constraint_push_mapping: Optional[Dict[str, str]] = None,
                                        shuffle=True,
                                        volume_to_weight = lambda volume: volume,
                                        check_condition=True,
                                        log_indent=0) -> Tuple[Iterable[NLAndCondition], int]:
        if _DEBUG:
            print()
            print(' ' * log_indent + '-- _make_resolved_template_sampler() --')
            print(' ' * log_indent + '    template:', template)
            # print(' ' * log_indent + '    ancestor_keys:', ancestor_keys)
            print(' ' * log_indent + '    ancestor_nls:', ancestor_nls)
        template_key, template_nls = self._find_template_nls(template,
                                                             # tuple(sorted(ancestor_keys)),
                                                             # tuple(sorted(ancestor_nls.union(set([template])))),
                                                             log_indent = log_indent + 4)
        if template_key is None:
            raise Exception(f'template for {template} not found.')

        iterators = []
        weight_types: List[str] = []
        volumes: List[int] = []
        for weight, template_nl in template_nls:
            if template_nl in ancestor_nls:
                continue

            iterator_with_volume = self._make_resolved_translation_sampler(template_nl,
                                                                           # ancestor_keys.union(set([template_key])),
                                                                           ancestor_nls.union(set([template_nl])),
                                                                           constraint_interpret_mapping=constraint_interpret_mapping,
                                                                           constraint_force_pos_mapping=constraint_force_pos_mapping,
                                                                           constraint_push_mapping=constraint_push_mapping,
                                                                           block_shuffle=shuffle,
                                                                           volume_to_weight=volume_to_weight,
                                                                           check_condition=check_condition,
                                                                           log_indent = log_indent + 4)
            iterators.append(iterator_with_volume[0])
            weight_types.append(weight)
            volumes.append(iterator_with_volume[1])

        if shuffle:

            volume_weights = [volume_to_weight(volume) for volume in volumes]
            weights = [self._get_weight_factor_func(weight_type)(volume_weights, i_iterator)
                       for i_iterator, weight_type in enumerate(weight_types)]

            # @profile
            def generate():
                for resolved_template_nl, condition in chained_sampling_from_weighted_iterators(
                    iterators,
                    weights,
                ):
                    yield resolved_template_nl, condition

        else:

            # @profile
            def generate():
                for iterator in iterators:
                    for resolved_template_nl, condition in iterator:
                        yield resolved_template_nl, condition

        return generate(), sum(volumes)

    # @profile
    def _interpret_mapping_is_consistent_with_condition(self,
                                                        condition: _PosFormConditionSet,
                                                        interpret_mapping: Dict[str, Phrase],
                                                        push_mapping: Dict[str, str],
                                                        force_pos_mapping: Optional[Dict[str, str]] = None) -> bool:
        condition_is_consistent = True
        for interprand_rep, pos, form in condition:
            interprand_rep_pushed = push_mapping[interprand_rep]
            phrase = interpret_mapping[interprand_rep_pushed]
            forced_pos = force_pos_mapping.get(interprand_rep_pushed, None)

            allowed_pos = [forced_pos] if forced_pos is not None else self._get_pos(phrase)

            if pos not in allowed_pos:
                condition_is_consistent = False
                break

            inflated_phrases = self._get_inflated_phrases(phrase, pos, form)
            if len(inflated_phrases) == 0:
                condition_is_consistent = False
                break

        return condition_is_consistent

    @lru_cache(maxsize=1000000)
    def _find_template_nls(self,
                           template: str,
                           # ancestor_keys: Tuple[str],
                           # ancestor_nls: Tuple[str],
                           log_indent=0) -> Tuple[Optional[str], Optional[List[Tuple[str, str]]]]:
        if _DEBUG:
            print()
            print(' ' * log_indent + '-- _find_template_nls() --')
            print(' ' * log_indent + '    template:', template)
            # print(' ' * log_indent + '    ancestor_keys:', ancestor_keys)
            # print(' ' * log_indent + '    ancestor_nls:', ancestor_nls)
        # ancestor_keys_set = set(ancestor_keys)
        # ancestor_nls_set = set(ancestor_nls)

        template_prefix = '::'.join(template.split('::')[:-1])
        template_key = template.split('::')[-1]
        template_key_formula = Formula(template_key)

        found_template_nls = None
        found_template_key = None

        config = self._two_layered_config[template_prefix]
        for transl_key, transl_nls in config.items():
            key_formula = Formula(transl_key)
            if formula_can_not_be_identical_to(key_formula, template_key_formula):
                continue

            for mapping in generate_mappings_from_formula([key_formula],
                                                          [template_key_formula]):
                key_formula_pulled = interpret_formula(key_formula, mapping)
                if key_formula_pulled.rep == template_key_formula.rep:
                    found_template_key = transl_key
                    found_template_nls = []
                    for weighted_nl in transl_nls:
                        weight_type, nl = weighted_nl
                        found_template_nls.append((weight_type, interpret_formula(Formula(nl), mapping).rep))
                    break

            if found_template_nls is not None:
                break

        return (
            '::'.join([template_prefix, found_template_key]) if found_template_key is not None else None,
            found_template_nls,
        )

    def _make_phrase_str_mapping(self, mapping: Dict[str, Phrase]) -> Dict[str, str]:
        return {
            key: self._make_phrase_str(val)
            for key, val in mapping.items()
        }

    def _make_phrase_str(self, phrase: Phrase) -> str:
        if isinstance(phrase, ConstantPhrase):
            return self._make_constant_phrase_str(phrase)
        elif isinstance(phrase, PredicatePhrase):
            return self._make_predicate_phrase_str(phrase)
        else:
            raise ValueError(f'{str(phrase)}')

    @abstractmethod
    def _make_constant_phrase_str(self, const: ConstantPhrase) -> str:
        pass

    @abstractmethod
    def _make_predicate_phrase_str(self, pred: PredicatePhrase) -> str:
        pass

    def _merge_condition(self, this: _PosFormConditionSet, that: _PosFormConditionSet) -> _PosFormConditionSet:
        return this.union(that)

    def _extract_templates(self, nl: str) -> Iterable[str]:
        for match in re.finditer(f'{self._TEMPLATE_BRACES[0]}((?!{self._TEMPLATE_BRACES[1]}).)*{self._TEMPLATE_BRACES[1]}', nl):
            template = nl[match.span()[0] + len(self._TEMPLATE_BRACES[0]) : match.span()[1] - len(self._TEMPLATE_BRACES[1])]
            yield template

    # @profile
    def _get_pos_form_consistency_condition(self, nl: str) -> _PosFormConditionSet:
        formula = Formula(nl)
        interprands = formula.predicates + formula.constants

        conditions: List[Tuple[str, POS, str]] = []
        for interprand in interprands:
            pos_form = self._get_interprand_condition_from_template(interprand.rep, formula.rep)
            if pos_form is None:
                continue
            pos, form = pos_form
            conditions.append((interprand.rep, pos, form))

        return _PosFormConditionSet(conditions)

    # @profile
    def _choose_interpret_mapping(self,
                                  formulas: List[Formula],
                                  intermediate_constant_formulas: List[Formula],
                                  constraints: Optional[Dict[str, Phrase]] = None,
                                  from_knowledge=False,
                                  ) -> Union[Dict[str, str], Tuple[Dict[str, Phrase], Dict[str, str], List[bool]]]:

        if from_knowledge and self._knowledge_bank.is_acceptable(formulas):
            _mapping, is_injected = self._knowledge_bank.sample_mapping(formulas)
            mapping = {key: val[0] for key, val in _mapping}
            pos_mapping = {key: val[1] for key, val in _mapping if val[1] is not None}
            return mapping, pos_mapping, is_injected

        else:
            constraints = constraints or {}

            zeroary_predicates = list({predicate.rep
                                       for formula in formulas
                                       for predicate in formula.zeroary_predicates})
            unary_predicates = list({predicate.rep
                                     for formula in formulas
                                     for predicate in formula.unary_predicates})
            constants = list({constant.rep for formula in formulas for constant in formula.constants})
            intermediate_constants = sorted({constant.rep for constant in intermediate_constant_formulas})

            # we sample more phrases so that we have more chance of POS/FORM condition matching.
            adj_verb_nouns = self._sample(self._unary_predicates, len(unary_predicates) * 3)
            if self.reused_object_nouns_max_factor > 0.0:
                obj_nouns = list({phrase.object for phrase in adj_verb_nouns
                                  if isinstance(phrase, PredicatePhrase)})
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

            # intermediate_constant_nouns = sorted(self._word_bank.get_intermediate_constant_words())[:len(intermediate_constants)]
            intermediate_constant_nouns = self._sample(self._word_bank.get_intermediate_constant_words(), len(intermediate_constants))

            zeroary_constraints = {k: v for k, v in constraints.items() if k in zeroary_predicates}
            # zero-ary predicate {A}, which appears as ".. {A} i ..", shoud be Noun.
            zeroary_mapping = next(
                generate_mappings_from_predicates_and_constants(
                    zeroary_predicates,
                    [],
                    event_nouns,
                    [],
                    shuffle=True,
                    allow_many_to_one=False,
                    constraints=zeroary_constraints,
                )
            )

            # Unary predicate {A}, which appears as "{A}{a}", shoud be adjective or verb.
            unary_constraints = {
                **dict(zip(intermediate_constants, intermediate_constant_nouns)),
                **{k: v for k, v in constraints.items() if k in unary_predicates + constants}
            }
            unary_mapping = next(
                generate_mappings_from_predicates_and_constants(
                    unary_predicates,
                    constants,
                    adj_verb_nouns,
                    entity_nouns,
                    shuffle=True,
                    allow_many_to_one=False,
                    constraints=unary_constraints,
                )
            )

            interpret_mapping = zeroary_mapping.copy()
            interpret_mapping.update(unary_mapping)

            return interpret_mapping

    # @profile
    def _sample(self,
                elems: Union[List[Any], Iterable[Any]],
                size: int,
                allow_duplicates=False) -> List[Any]:
        if isinstance(elems, list):
            if len(elems) < size:
                logger.warning('Can\'t sample %d elements. Will sample only %d elements.',
                               size,
                               len(elems))
                samples = random.sample(elems, len(elems))
            else:
                samples = random.sample(elems, size)
            if not allow_duplicates and len(samples) != len(set(samples)):
                raise ValueError('The given "elems" seems to have duplicates')
        else:
            samples: Set[Any] = set([])
            for elem in elems:
                samples.add(elem)
                if len(samples) >= size:
                    break
            if len(samples) < size:
                raise Exception('Could not sample %d elements from the iterator', size)
            samples = list(samples)
        return samples

    # @profile
    def _take(self, elems: Union[Iterable[Any], List[Any]], size: int, allow_duplicates=False) -> List[Any]:
        if isinstance(elems, list):
            if len(elems) < size:
                logger.warning('Can\'t take %d elements. Will take only %d elements.',
                               size,
                               len(elems))
            samples = elems[:size]
            if not allow_duplicates and len(samples) != len(set(samples)):
                raise ValueError('The given "elems" seems to have duplicates')
        else:
            samples: Set[Any] = set([])
            for elem in elems:
                samples.add(elem)
                if len(samples) >= size:
                    break
            if len(samples) < size:
                raise Exception('Could not sample %d elements from the iterator', size)
            samples = list(samples)
        return samples

    # @profile
    def _make_phrase_inflated_interpret_mapping(self,
                                                interpret_mapping: Dict[str, Phrase],
                                                interprand_templated_translation_pushed: str) -> Tuple[Dict[str, Phrase], Dict[str, int]]:
        inflated_mapping = {}
        stats = defaultdict(int)

        for interprand_formula in Formula(interprand_templated_translation_pushed).predicates\
                + Formula(interprand_templated_translation_pushed).constants:
            interprand_rep = interprand_formula.rep
            if interprand_templated_translation_pushed.find(f'{interprand_rep}[') >= 0:
                phrase = interpret_mapping[interprand_rep]
                pos_form = self._get_interprand_condition_from_template(interprand_rep, interprand_templated_translation_pushed)
                if pos_form is None:
                    raise ValueError(f'Could not extract pos and form information about "{interprand_rep}" from "{interprand_templated_translation_pushed}"')
                pos, form = pos_form
                if self.log_stats:
                    stats[f'{pos.value}.{form}'] += 1
                inflated_phrases = self._get_inflated_phrases(phrase, pos, form)

                assert len(inflated_phrases) > 0
                inflated_phrase = random.choice(inflated_phrases)
            else:
                raise Exception(
                    f'Something wrong. Since we have checked in that the translation indeed exists, this program must not pass this block.  The problematic translation is "{interprand_templated_translation_pushed}" and unfound string is "{interprand_rep}["',
                )
            inflated_mapping[interprand_rep] = inflated_phrase
        return inflated_mapping, stats

    # @profile
    def _get_interprand_condition_from_template(self, interprand: str, rep: str) -> Optional[Tuple[POS, Optional[str]]]:
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
            pos_str, form = info.split('.')
        else:
            pos_str, form = info, 'normal'

        return POS[pos_str], form

    @lru_cache(maxsize=1000000)
    def _get_inflated_phrases(self, phrase: Phrase, pos: POS, form: str) -> Union[Tuple[str, ...], Tuple[Phrase, ...]]:
        if pos == POS.ADJ:
            force = True
        elif pos == POS.VERB:
            force = False
        elif pos == POS.NOUN:
            force = False
        else:
            raise ValueError()

        if isinstance(phrase, PredicatePhrase):
            _word, obj, right_modifier, left_modifier = phrase.predicate, phrase.object, phrase.right_modifier, phrase.left_modifier
        elif isinstance(phrase, ConstantPhrase):
            _word = phrase.constant
        else:
            raise ValueError()

        inflated_words = self._word_bank.change_word_form(_word, pos, form, force=False)
        if len(inflated_words) == 0 and force:
            inflated_words = self._word_bank.change_word_form(_word, pos, form, force=True)

        if isinstance(phrase, PredicatePhrase):
            return tuple(PredicatePhrase(predicate=_inflated_word, object=obj, right_modifier=right_modifier, left_modifier=left_modifier)
                         for _inflated_word in inflated_words)

        elif isinstance(phrase, ConstantPhrase):
            return tuple(ConstantPhrase(constant=_inflated_word)
                         for _inflated_word in inflated_words)

        else:
            raise ValueError()

    @lru_cache(maxsize=1000000)
    def _get_pos(self, phrase: Phrase) -> List[POS]:
        if isinstance(phrase, PredicatePhrase):
            _word = phrase.predicate
        elif isinstance(phrase, ConstantPhrase):
            _word = phrase.constant
        else:
            raise ValueError()
        return self._word_bank.get_pos(_word)

    @abstractmethod
    def _postprocess_template(self, template: str) -> str:
        pass

    @abstractmethod
    def _reset_predicate_phrase_assets(self) -> None:
        pass

    @abstractmethod
    def _postprocess_translation(self, translation: str, is_knowledge_injected=False) -> str:
        pass
