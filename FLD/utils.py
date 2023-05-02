from typing import Optional, Callable, List, Iterable, Any
import math
import logging
from typing import Dict, Any, List, Iterable
import random
import logging
import zlib
from pprint import pformat

from nltk.corpus import cmudict
import timeout_decorator
from .exception import FormalLogicExceptionBase
import kern_profiler

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

    def _bouded_log(i_trial: int, message: str):
        logger.info(
            build_bounded_msg('run_with_timeout_retry for %-20s [%d/%d] %s', 0),
            f'"{log_title or "None"}"',
            i_trial,
            max_retry,
            message,
        )

    for i_trial in range(0, max_retry):
        exception_msg = None
        try:
            result = timeout_decorator.timeout(timeout, timeout_exception=TimeoutError, use_signals=True)(func)(*func_args, **func_kwargs)
            _bouded_log(i_trial, '[succeeded]')
            return result
        except TimeoutError as e:
            exception_msg = f'TimeoutError(timeout={timeout})'
        except retry_exception_class as e:
            exception_msg = str(e)
        if exception_msg is not None:
            _bouded_log(i_trial, '[failed] due to the folllowing error')
            logger.info('\n%s', exception_msg)
        else:
            _bouded_log(i_trial, '[failed]')
    raise RetryAndTimeoutFailure(f'run_with_timeout_retry for "{str(log_title)}" [{i_trial}/{max_retry}] failed')


def compress(text: str) -> bytes:
    return zlib.compress(text.encode('utf-8'))


def decompress(binary: bytes) -> str:
    return zlib.decompress(binary).decode('utf-8')


def make_combination(elem_generators: List[Callable[[], Iterable[Any]]]) -> Iterable[List[Any]]:
    head_elem_generator = elem_generators[0]
    tail_elem_generators = elem_generators[1:]

    if len(tail_elem_generators) == 0:
        for elem in head_elem_generator():
            yield [elem]
    else:
        for head_elem in head_elem_generator():
            for tail_elems in make_combination(tail_elem_generators):
                yield [head_elem] + tail_elems


@profile
def chained_sampling_from_weighted_iterators(iterators: List[Iterable[Any]], weights: List[float]) -> Iterable[Any]:
    sum_weights = sum(weights)
    if math.isclose(sum_weights, 0):
        return

    normalized_weights = [weight / sum_weights for weight in weights]
    aliving_iterators = iterators
    while True:
        if len(aliving_iterators) == 0:
            break
        rand = random.random()
        _w = 0.0
        chosen_idx = None
        margin = 0.000001
        for i, weight in enumerate(normalized_weights):
            if _w - margin <= rand <= _w + weight + margin:
                chosen_idx = i
                break
            _w += weight

        try:
            item = next(aliving_iterators[chosen_idx])
            yield item
        except StopIteration:
            aliving_iterators = [iterator for idx, iterator in enumerate(aliving_iterators)
                                 if idx != chosen_idx]
            aliving_weights = [weight for idx, weight in enumerate(normalized_weights)
                               if idx != chosen_idx]
            sum_weights = sum(aliving_weights)
            if math.isclose(sum_weights, 0):
                return
            normalized_weights = [weight / sum_weights for weight in aliving_weights]


def build_bounded_msg(msg: str, level: int) -> str:
    if level == 0:
        return f'---------- {msg<:40} ----------'
    elif level == 1:
        return f'========== {msg<:40} =========='
    elif level == 2:
        return f'********** {msg<:40} **********'
    elif level == 3:
        return f'---------------------------------- {msg<:40} ----------------------------------'
    elif level == 4:
        return f'================================== {msg<:40} =================================='
    elif level == 5:
        return f'********************************** {msg<:40} **********************************'
    else:
        raise ValueError()


def log_results(logger,
                nlproof_json: Optional[Dict] = None,
                proof_tree = None,
                distractors: Optional[List[str]] = None,
                translation_distractors: Optional[List[str]] = None,
                stats: Optional[Dict] = None):
    logger.info(build_bounded_msg('results', 4))
    
    if proof_tree is not None:
        logger.info('\n')
        logger.info(build_bounded_msg('proof tree', 3))

        logger.info('\n')
        logger.info('\n' + proof_tree.format_str)

    if distractors is not None:
        logger.info('\n')
        logger.info(build_bounded_msg('distractors', 3))
        logger.info('\n' + pformat(distractors))

    if translation_distractors is not None:
        logger.info('\n')
        logger.info(build_bounded_msg('translation distractors', 3))
        logger.info('\n' + pformat(translation_distractors))

    if nlproof_json is not None:
        logger.info('\n')
        logger.info(build_bounded_msg('NLProofs json', 3))
        logger.info('\n' + pformat(nlproof_json))

    if stats is not None:
        logger.info('\n')
        logger.info(build_bounded_msg('stats', 3))
        for key in ['avg.word_count_all']:
            if key in stats:
                logger.info('%s: %s', key, stats[key])


    logger.info('\n\n')
