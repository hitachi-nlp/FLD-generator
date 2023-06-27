from typing import List, Iterable, Optional, Set
from abc import abstractmethod, ABC
import re
import random
import logging

from .exception import FormalLogicExceptionBase
from FLD_generator.utils import run_with_timeout_retry, RetryAndTimeoutFailure
from FLD_generator.word_banks.base import WordBank
from FLD_generator.word_banks import POS, ATTR
import kern_profiler


logger = logging.getLogger(__name__)


class TranslationDistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class TranslationDistractor(ABC):

    def generate(self,
                 translations: List[str],
                 size: int,
                 max_retry: Optional[int] = None,
                 timeout_per_trial: Optional[int] = None,
                 best_effort=False) -> List[str]:
        max_retry = max_retry or self.default_max_retry
        timeout_per_trial = timeout_per_trial or self.default_timeout
        try:
            trial_results = run_with_timeout_retry(
                self._generate,
                func_args=[translations, size],
                func_kwargs={'best_effort': best_effort},

                should_retry_func = lambda distractors: len(distractors) < size,
                should_retry_exception=TranslationDistractorGenerationFailure,

                max_retry=max_retry,
                timeout_per_trial=timeout_per_trial,
                best_effort=best_effort,

                logger=logger,
                log_title='_generate()',
            )
            return sorted(trial_results, key = lambda distractors: len(distractors))[-1]
        except RetryAndTimeoutFailure as e:
            raise TranslationDistractorGenerationFailure(str(e))

    @property
    @abstractmethod
    def default_max_retry(self) -> int:
        pass

    @property
    @abstractmethod
    def default_timeout(self) -> int:
        pass

    @abstractmethod
    def _generate(self, translations: List[str], size: int, best_effort=False) -> List[str]:
        pass


class WordSwapDistractor(TranslationDistractor):

    def __init__(self,
                 word_bank: WordBank,
                 word_swap_prob=0.1,
                 swap_ng_words: Optional[Set[str]] = None):
        self._word_bank = word_bank
        self._words = {}

        logger.info('loading words from the wordbank ...')
        for pos in POS:
            self._words[pos] = list(self._load_words_by_pos_attrs(word_bank, pos=pos))
        logger.info('loading words from the wordbank ... done!')

        self.word_swap_prob = word_swap_prob
        self.swap_ng_words = swap_ng_words

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

    @profile
    def _generate(self, translations: List[str], size: int, best_effort=False) -> List[str]:
        intermediate_constants = list(self._word_bank.get_intermediate_constant_words())
        translations = [transl for transl in translations
                        if all(transl.find(intermediate_constant) < 0 for intermediate_constant in intermediate_constants)]

        if len(translations) == 0 or size == 0:
            return []
        
        distractor_translations = []
        is_duplicated_translation_generated = False
        num_loop = int(size / len(translations) + 1)
        for i_loop in range(0, num_loop):
            for translation in random.sample(translations, len(translations)):
                swapped_translation = self._word_swap_translation(translation)

                if swapped_translation is not None:
                    if swapped_translation in distractor_translations:
                        is_duplicated_translation_generated = True
                    else:
                        distractor_translations.append(swapped_translation)

                if len(distractor_translations) >= size:
                    return distractor_translations

        if len(distractor_translations) < size:
            msg = f'WordSwapDistractor could not generate {size} distractors. Will return only {len(distractor_translations)} distractors'
            if is_duplicated_translation_generated:
                msg += '\nThis might be due to that duplicated translation are generated but they are excluded.'
            if best_effort:
                logger.info(msg)
            else:
                raise TranslationDistractorGenerationFailure(msg)
        return distractor_translations

    def _word_swap_translation(self, transl: str, at_least_one=True) -> Optional[str]:

        for trial in range(0, 100):
            words = transl.split(' ')
            swapped_words = []
            for word in words:
                if word in self.swap_ng_words:
                    swapped_words.append(word)
                    continue

                if random.random() <= self.word_swap_prob:
                    POSs = self._word_bank.get_pos(word)
                    if len(POSs) == 0:
                        swapped_words.append(word)
                        continue

                    random_word = None
                    for pos in random.sample(POSs, len(POSs)):
                        if pos in self._words:
                            random_word = random.choice(self._words[pos])
                            break

                    if random_word is not None:
                        swapped_words.append(random_word)
                    else:
                        swapped_words.append(word)
                else:
                    swapped_words.append(word)

            any_word_is_swapped = any(
                swapped_word != word
                for swapped_word, word in zip(swapped_words, words)
            )

            if at_least_one and not any_word_is_swapped:
                continue
            else:
                return ' '.join(swapped_words)

        return None

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 10


def build(type_: str,
          word_bank: Optional[WordBank] = None,
          swap_ng_words: Optional[Set[str]] = None):
    msg = 'we should not use translation distractor because it can not ensure that the collapsed sentence can not derive the original hypothesis. For example, "{A}=typhoon & {B}=rain" collapsed to "{A}=typhoon & {B}=cloud" still derives {A}=typhoon.'
    # raise Exception(msg)
    logger.warning(msg)

    swap_ng_words = swap_ng_words or {'a', 'the', 'is'}

    if type_ == 'word_swap':

        if word_bank is None:
            raise ValueError()

        return WordSwapDistractor(word_bank, swap_ng_words=swap_ng_words)

    else:
        raise ValueError(f'Unknown distractor type {type_}')
