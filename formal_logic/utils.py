import logging
from collections import defaultdict
from typing import Dict, Any, Tuple, List, Iterable
import random

from nltk.corpus import cmudict


class DelayedLogger:

    _level_strs = {
        logging.DEBUG: 'DEBUG',
        logging.INFO: 'INFO',
        logging.WARNING: 'WARNING',
        logging.FATAL: 'FATAL',
    }

    def __init__(self,
                 logger,
                 delayed=True):
        self._logger = logger
        self._delayed = delayed
        self._traces = defaultdict(list)

    def debug(self, msg: str) -> None:
        self._log_or_cache(msg, logging.DEBUG)

    def flush_debug(self) -> None:
        self._log_and_flush(logging.DEBUG)

    def info(self, msg: str) -> None:
        self._log_or_cache(msg, logging.INFO)

    def flush_info(self) -> None:
        self._log_and_flush(logging.INFO)

    def warning(self, msg: str) -> None:
        self._log_or_cache(msg, logging.WARNING)

    def flush_warning(self) -> None:
        self._log_and_flush(logging.WARNING)

    def fatal(self, msg: str) -> None:
        self._log_or_cache(msg, logging.FATAL)

    def flush_fatal(self) -> None:
        self._log_and_flush(logging.FATAL)

    def _log_or_cache(self,
                      msg: str,
                      level: int) -> None:
        if self._delayed:
            self._traces[level].append(msg)
        else:
            self._get_logging_func(level)

    def _log_and_flush(self,
                       level: int) -> None:
        for msg in self._traces[level]:
            self._get_logging_func(level)(msg)
        self._traces[level] = []

    def _get_logging_func(self, level: int):
        if level == logging.DEBUG:
            logging_fn = self._logger.debug
        elif level == logging.info:
            logging_fn = self._logger.info
        elif level == logging.WARNING:
            logging_fn = self._logger.warning
        elif level == logging.FATAL:
            logging_fn = self._logger.fatal
        return logging_fn


def starts_with_vowel_sound(word, pronunciations=cmudict.dict()):
    for syllables in pronunciations.get(word, []):
        return syllables[0][-1].isdigit()  # use only the first one


def flatten_dict(dic: Dict[str, Any]) -> Dict[str, Any]:
    flat_dic = {}
    for key, val in dic.items():
        if isinstance(val, dict):
            for child_key, child_val in flatten_dict(val).items():
                flat_key = '.'.join([key, child_key])
                flat_dic[flat_key] = child_val
        else:
            flat_dic[key] = val
    return flat_dic


def shuffle(elems: List[Any]) -> List[Any]:
    return random.sample(elems, len(elems))


def weighted_shuffle(weights: List[float]) -> Iterable[int]:
    """ Weighted shuffle = sampling elements in accordance with the their weights. The sampling sequence is made without replacement.   """
    done_indexes = set()
    for _ in range(0, len(weights)):

        not_done_weights = []
        shifted_idx_to_idx = {}
        shifted_idx = 0
        for idx, weight in enumerate(weights):
            if idx in done_indexes:
                continue

            not_done_weights.append(weight)
            shifted_idx_to_idx[shifted_idx] = idx
            shifted_idx += 1
            
        if sum(not_done_weights) == 0.0:
            return

        sampled_shifted_idx = weighted_sampling(not_done_weights)
        sampled_idx = shifted_idx_to_idx[sampled_shifted_idx]
        yield sampled_idx
        done_indexes.add(sampled_idx)


def weighted_sampling(weights: List[float]) -> int:
    weight_sum = sum(weights)
    if weight_sum == 0.0:
        raise ValueError()
    normalized_weights = [weight / weight_sum for weight in weights]
    r = random.random()
    cum = min(1e-7, min(normalized_weights))  # start from positive value in order to ensure that cum reached 1.0 at the end of the for loop
    for idx, weight in enumerate(normalized_weights):
        cum += weight
        if cum >= r:
            return idx
    raise Exception()
