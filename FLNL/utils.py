from typing import Optional, Callable
import logging
from typing import Dict, Any, List, Iterable
import random
import logging
import zlib

from nltk.corpus import cmudict
import timeout_decorator
from .exception import FormalLogicExceptionBase

utils_logger = logging.getLogger(__name__)


class RetryAndTimeoutFailure(FormalLogicExceptionBase):
    pass


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


def nested_merge(this: Any, that: Any) -> Any:
    if type(this) is not type(that):
        ValueError(f'type(this) {type(this)} does not match type(that){type(that)}')

    if isinstance(this, dict):
        updated = {}
        for this_key, this_val in this.items():
            if this_key in that:
                that_val = that[this_key]
                updated_val = nested_merge(this_val, that_val)
                updated[this_key] = updated_val
            else:
                updated[this_key] = this_val
        for that_key, that_val in that.items():
            if that_key not in updated:
                updated[that_key] = that_val
        return updated
    elif isinstance(this, list):
        unique_elems = []
        for elem in this + that:
            if elem not in unique_elems:
                unique_elems.append(elem)
        return unique_elems
    else:
        raise ValueError(f'this and that are not containers. Thus, we can not append that to this.\nThis: {str(this)}\nThat: {str(that)}')


def run_with_timeout_retry(
    func: Callable,
    func_args: List[Any] = None,
    func_kwargs: Dict[Any, Any] = None,
    retry_exception_class: Optional[Exception] = None,
    max_retry: Optional[int] = None,
    timeout: Optional[int] = None,
    logger = None,
    log_title: Optional[str] = None,
) -> Any:

    func_args = func_args or []
    func_kwargs = func_kwargs or {}
    max_retry = max_retry or 99999
    timeout = timeout or 99999
    logger = logger or utils_logger
    log_title = log_title or str(func)

    logger.info('=================== run_with_timeout_retry [%s]', log_title)
    for i_trial in range(0, max_retry):
        logger.info('---- trial=%d ----', i_trial)
        try:
            result = timeout_decorator.timeout(timeout, timeout_exception=TimeoutError, use_signals=True)(func)(*func_args, **func_kwargs)
            logger.info('-- succeeded!')
            return result
        except TimeoutError:
            logger.warning('-- the LAST trial failed with TimeoutError(timeout=%d)', timeout)
        except retry_exception_class as e:
            logger.warning('-- failed. The message of the LAST trial is the followings:')
            logger.warning('%s', str(e))
    raise RetryAndTimeoutFailure(f'-- {log_title} failed with max_retry={max_retry}.')


def compress(text: str) -> bytes:
    return zlib.compress(text.encode('utf-8'))


def decompress(binary: bytes) -> str:
    return zlib.decompress(binary).decode('utf-8')
