from typing import List, Iterable, Optional
from abc import abstractmethod, ABC
import re
import random
import logging

from .exception import FormalLogicExceptionBase
from FLD.utils import run_with_timeout_retry, RetryAndTimeoutFailure
from FLD.word_banks.base import WordBank
from FLD.word_banks import POS, ATTR
import kern_profiler


logger = logging.getLogger(__name__)


class TranslationDistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class TranslationDistractor(ABC):

    def generate(self,
                 translations: List[str],
                 size: int,
                 max_retry: Optional[int] = None,
                 timeout: Optional[int] = None) -> List[str]:
        max_retry = max_retry or self.default_max_retry
        timeout = timeout or self.default_timeout
        try:
            return run_with_timeout_retry(
                self._generate,
                func_args=[translations, size],
                func_kwargs={},
                retry_exception_class=TranslationDistractorGenerationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='_generate()',
            )
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
    def _generate(self, translations: List[str], size: int) -> List[str]:
        pass


class WordSwapDistractor(TranslationDistractor):

    def __init__(self, word_bank: WordBank, word_swap_prob=0.1):
        self._word_bank = word_bank
        self._words = {}

        logger.info('loading words from the wordbank ...')
        for pos in POS:
            self._words[pos] = list(self._load_words_by_pos_attrs(word_bank, pos=pos))
        logger.info('loading words from the wordbank ... done!')

        self.word_swap_prob = word_swap_prob

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
    def _generate(self, translations: List[str], size: int) -> List[str]:
        unconditioned_constants = list(self._word_bank.get_unconditioned_constant_words())
        translations = [transl for transl in translations
                        if all(transl.find(unconditioned_constant) < 0 for unconditioned_constant in unconditioned_constants)]

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
            logger.warning('WordSwapDistractor could not generate %s distractors. Will return only %d distractors', size, len(distractor_translations))
            if is_duplicated_translation_generated:
                logger.warning('This might be due to that duplicated translation are generated but they are excluded.')
        return distractor_translations

    def _word_swap_translation(self, transl: str, at_least_one=True) -> Optional[str]:
        ng_words = ['a', 'the', 'is']

        for trial in range(0, 100):
            words = transl.split(' ')
            swapped_words = []
            for word in words:
                if word in ng_words:
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


def build(type_: str, word_bank: Optional[WordBank] = None):
    if type_ == 'word_swap':
        if word_bank is None:
            raise ValueError()
        return WordSwapDistractor(word_bank)
    else:
        raise ValueError(f'Unknown distractor type {type_}')
