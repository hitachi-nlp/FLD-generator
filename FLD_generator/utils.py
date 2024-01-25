from typing import Optional, Callable, List, Iterable, Any, Tuple, Optional, Union, Iterator
from pprint import pprint
from collections import defaultdict
import math
from typing import Dict, Any, List, Iterable, Set
import random
import logging
import zlib
from pprint import pformat
from ctypes import ArgumentError
import os
import logging

from z3.z3types import Z3Exception
from FLD_generator.argument import Argument
from nltk.corpus import cmudict
import timeout_decorator
from .exception import FormalLogicExceptionBase
from FLD_generator.formula import Formula
from FLD_generator.formula_checkers import is_provable, is_disprovable, is_consistent_set as is_consistent_formula_set
import line_profiling

utils_logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


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
    if isinstance(elems, set):
        elems = list(elems)
    return random.sample(elems, len(elems))


_shuffle_func = shuffle


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

    should_retry_func: Callable[[Any], bool] = lambda _: False,
    should_retry_exception: Optional[Exception] = None,

    max_retry: Optional[int] = None,
    timeout_per_trial: Optional[Union[int, float]] = None,
    best_effort=False,

    logger = None,
    log_title: Optional[str] = None,
) -> Any:
    if max_retry is not None and max_retry <= 0:
        raise ValueError()

    func_args = func_args or []
    func_kwargs = func_kwargs or {}
    max_retry = max_retry or 99999
    timeout_per_trial = timeout_per_trial or 99999
    logger = logger or utils_logger
    log_title = log_title or str(func)

    def _make_pretty_msg(i_trial: int, status: str, msg: Optional[str] = None):
        return make_pretty_msg(title='run_with_timeout_retry', status=status, subtitle=str(log_title),
                               trial=i_trial + 1, max_trial=max_retry, boundary_level=0,
                               msg=msg)

    trial_results = []
    for i_trial in range(0, max_retry):
        timeout_func = timeout_decorator.timeout(
            timeout_per_trial,
            timeout_exception=TimeoutError,
            use_signals=True,
            # use_signals=False,  # XXX this does not work
        )(func)

        is_fatal = False
        do_log_args = False
        exception = None
        try:
            result = timeout_func(*func_args, **func_kwargs)
            trial_results.append(result)

            if not should_retry_func(result):
                logger.info(_make_pretty_msg(i_trial, 'success', msg=None))
                return trial_results

            retry_msg = 'is_retry_func(result)'

        except ArgumentError as e:
            if str(e).find('TimeoutError') >= 0:
                exception = e
                retry_msg = f'ArgumentError(TimeoutError(timeout={timeout_per_trial})) (we guess this error occurs when timeout is come during the extenral z3 library is being executed)'
            else:
                raise e
        except Z3Exception as e:
            exception = e
            do_log_args = True
            logger.fatal('[checkers.py] Z3Exception occurred. We will continue the trials, however, we do not know the root cause of this.')

        except TimeoutError as e:
            exception = e
            retry_msg = f'TimeoutError(timeout={timeout_per_trial})'

        except should_retry_exception as e:
            exception = e
            retry_msg = str(e)

        if do_log_args:
            logger.info(pformat(func_args))
            logger.info(pformat(func_kwargs))
            logger.info(str(timeout_func))
            logger.info(str(exception))
            logger.info(str(type(exception)))

        if is_fatal:
            raise exception

        logger.info(_make_pretty_msg(i_trial, 'failure',
                                     msg=f'this is caused by the folllowing:\n{str(retry_msg)}'))

    if best_effort:
        logger.info(_make_pretty_msg(i_trial, 'failure', msg='return best effort results'))
        return trial_results
    else:
        raise RetryAndTimeoutFailure(_make_pretty_msg(i_trial, 'failure'))


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


def make_combination_from_iter(elem_generators: List[Iterable[Any]]) -> Iterable[List[Any]]:
    head_elem_generator = elem_generators[0]
    tail_elem_generators = elem_generators[1:]

    if len(tail_elem_generators) == 0:
        for elem in head_elem_generator:
            yield [elem]
    else:
        for head_elem in head_elem_generator:
            for tail_elems in make_combination_from_iter(tail_elem_generators):
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


def _build_bounded_msg(msg: str, level: int) -> str:
    if level == 0:
        return f'---------- {msg:<40} ----------'
    elif level == 1:
        return f'========== {msg:<40} =========='
    elif level == 2:
        return f'********** {msg:<40} **********'
    elif level == 3:
        return f'---------------------------------- {msg:<40} ----------------------------------'
    elif level == 4:
        return f'================================== {msg:<40} =================================='
    elif level == 5:
        return f'********************************** {msg:<40} **********************************'
    else:
        raise ValueError()


def log_results(logger,
                i_sample: Optional[int] = None,
                nlproof_json: Optional[Dict] = None,
                proof_tree = None,
                distractors: Optional[List[str]] = None,
                translation_distractors: Optional[List[str]] = None,
                stats: Optional[Dict] = None):
    logger.info(make_pretty_msg(title='results',
                                subtitle=f'sample = {i_sample}' if i_sample is not None else '',
                                boundary_level=4))

    if proof_tree is not None:
        logger.info('\n')
        logger.info(make_pretty_msg(title='proof tree', boundary_level=3))
        logger.info('\n')
        logger.info('\n' + proof_tree.format_str)

    if distractors is not None:
        logger.info('\n')
        logger.info(make_pretty_msg(title='distractors', boundary_level=3))
        logger.info('\n' + pformat(distractors))

    if translation_distractors is not None:
        logger.info('\n')
        logger.info(make_pretty_msg(title='translation distractors', boundary_level=3))
        logger.info('\n' + pformat(translation_distractors))

    if nlproof_json is not None:
        logger.info('\n')
        logger.info(make_pretty_msg(title='NLProofs json', boundary_level=3))
        logger.info('\n' + pformat(nlproof_json))

    if stats is not None:
        logger.info('\n')
        logger.info(make_pretty_msg(title='stats', boundary_level=3))
        for key in ['avg.word_count_all']:
            if key in stats:
                logger.info('%s: %s', key, stats[key])

    logger.info('\n\n')


def make_pretty_msg(title: Optional[str] = None,
                    status: Optional[str] = None,
                    subtitle: Optional[str] = None,
                    trial: Optional[int] = None,
                    max_trial: Optional[int] = None,
                    msg: Optional[str] = None,
                    boundary_level: Optional[int] = None):
    log_msg = ''

    if title is not None:
        log_msg += f'{"[" + title + "]":<25}'

    if status is not None:
        if status not in ['success', 'failure', 'start', 'finish']:
            raise ValueError(f'Unsupported status {status}')
        log_msg += f'  {"[" + status + "]":<10}'

    if subtitle is not None:
        log_msg += f'  {"[" + subtitle + "]":<25}'

    if trial is not None:
        if max_trial is not None:
            log_msg += f'  {"[" + str(trial):^3s}/{str(max_trial) + "]":^3s}'
        else:
            log_msg += f'  {"[" + str(trial) + "]":^4s}'

    if msg is not None:
        log_msg += f'  {msg:<50}'

    if boundary_level is not None:
        log_msg = _build_bounded_msg(log_msg, boundary_level)

    return log_msg


@profile
def provable_from_incomplete_facts(fact_formulas: List[Formula],
                                   distractor_formulas: List[Formula],
                                   hypothesis: Formula) -> Tuple[bool, Optional[Formula]]:
    # XXX: we can not find the other proofs constructed from all the fact_formulas.
    for remaining_formulas, dropped_formula in _drop_one_element(fact_formulas):
        if is_provable(remaining_formulas + distractor_formulas, hypothesis):
            return True, dropped_formula
    return False, None


def disprovable_from_incomplete_facts(fact_formulas: List[Formula],
                                      distractor_formulas: List[Formula],
                                      hypothesis: Formula) -> Tuple[bool, Optional[Formula]]:
    # XXX: we can not find the other disproofs constructed from all the fact_formulas.
    for remaining_formulas, dropped_formula in _drop_one_element(fact_formulas):
        if is_disprovable(remaining_formulas + distractor_formulas, hypothesis):
            return True, dropped_formula
    return False, None


def _drop_one_element(elems: List[Any]) -> Iterable[Tuple[List[Any], Any]]:
    for i_drop in range(len(elems)):
        dropped_elem = elems[i_drop]
        remaining_elems = elems[:i_drop] + elems[i_drop + 1:]
        yield remaining_elems, dropped_elem


@profile
def have_smaller_proofs_with_logs(org_leaf_formulas: List[Formula],
                                  new_leaf_formulas: List[Formula],
                                  deleted_leaf_formulas: List[Formula],
                                  org_hypothesis_formula: Formula,
                                  new_hypothesis_formula: Formula,
                                  distractor_formulas: Optional[List[Formula]] = None,
                                  new_argument: Optional[Argument] = None) -> Tuple[bool, List[str]]:
    distractor_formulas = distractor_formulas or []
    remaining_leaf_formulas: List[Formula] = [
        formula for formula in org_leaf_formulas + new_leaf_formulas
        if formula.rep not in [_formula.rep for _formula in deleted_leaf_formulas]
    ]

    log_msgs: List[str] = []
    _is_provable, droppable_formula = provable_from_incomplete_facts(
        remaining_leaf_formulas,
        distractor_formulas,
        new_hypothesis_formula,
    )
    if _is_provable:
        log_msgs.append('original leafs:')
        for formula in org_leaf_formulas:
            log_msgs.append(f'    {formula.rep}')

        log_msgs.append('distractors   :')
        if len(distractor_formulas) > 0:
            for formula in distractor_formulas:
                log_msgs.append(f'    {formula.rep}')

        log_msgs.append('added leafs   :')
        for formula in new_leaf_formulas:
            log_msgs.append(f'    {formula.rep}')

        log_msgs.append('deleted leafs :')
        for formula in deleted_leaf_formulas:
            log_msgs.append(f'   {formula.rep}')

        log_msgs.append('droppable formulas:')
        for formula in [droppable_formula]:
            log_msgs.append(f'    {formula.rep}')

        log_msgs.append('original hypothesis :')
        for formula in [org_hypothesis_formula]:
            log_msgs.append(f'   {formula.rep}')

        log_msgs.append('new hypothesis      :')
        for formula in [new_hypothesis_formula]:
            log_msgs.append(f'   {formula.rep}')

        if new_argument is not None:
            log_msgs.append('used argument :')
            for premise in new_argument.premises:
                log_msgs.append(f'    premise: {premise.rep}')
            log_msgs.append(f'    conclusion: {new_argument.conclusion.rep}')

        return True, log_msgs

    return False, log_msgs


@profile
def is_consistent_formula_set_with_logs(org_formulas: List[Formula],
                                        new_formulas: List[Formula],
                                        deleted_formulas: List[Formula],
                                        new_argument: Optional[Argument] = None) -> Tuple[bool, List[str]]:

    remaining_formulas = [formula for formula in org_formulas + new_formulas
                          if formula.rep not in {_formula.rep for _formula in deleted_formulas}]
    log_msgs: List[str] = []
    if not is_consistent_formula_set(remaining_formulas):
        log_msgs.append('original      :')
        for formula in org_formulas:
            log_msgs.append(f'    {formula.rep}')

        log_msgs.append('added         :')
        for formula in new_formulas:
            log_msgs.append(f'    {formula.rep}')

        log_msgs.append('deleted       :')
        for formula in deleted_formulas:
            log_msgs.append(f'   {formula.rep}')

        if new_argument is not None:
            log_msgs.append('used argument :')
            for premise in new_argument.premises:
                log_msgs.append(f'    premise: {premise.rep}')
            log_msgs.append(f'    conclusion: {new_argument.conclusion.rep}')

        return False, log_msgs

    return True, log_msgs


def fix_seed(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


class RandomCycle:

    def __init__(self,
                 base_elems: Union[Callable[[], Iterator[Any]], Iterable[Any]],
                 shuffle=True):
        self._cached_list: Optional[List[Any]] = None
        self._base_elems = base_elems

        if shuffle:
            if isinstance(self._base_elems, Callable):  # elems is generate
                self._cached_list = _shuffle_func(elem for elem in self._base_elems())
                self._is_elems_cached = True
            else:
                if isinstance(self._base_elems, list):
                    self._cached_list = _shuffle_func(self._base_elems)
                    self._is_elems_cached = True
                else:
                    self._cached_list = []
                    self._is_elems_cached = False
        else:
            if isinstance(self._base_elems, list):
                self._cached_list = self._base_elems
                self._is_elems_cached = True
            else:
                self._cached_list = []
                self._is_elems_cached = False

        def make_current_iterable():
            if self._is_elems_cached and not isinstance(self._base_elems, Callable):
                elems_repr = str(self._base_elems) if not isinstance(self._base_elems, list) else type(self._base_elems)
                logger.info('making iterable from %d elements, the original one is %s',
                            len(self._cached_list),
                            elems_repr)
                return iter(self._cached_list)
            else:
                if isinstance(self._base_elems, Callable):  # elems is generate
                    return self._base_elems()
                else:
                    if isinstance(self._base_elems, list):
                        return iter(self._base_elems)
                    else:
                        return self._base_elems

        self._make_current_iterable = make_current_iterable
        self._cur_iter = self._make_current_iterable()
        self._prev_is_stop_iteration = False

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                item = next(self._cur_iter)
                if not self._is_elems_cached and not isinstance(self._base_elems, Callable):
                    self._cached_list.append(item)
                self._prev_is_stop_iteration = False
                return item
            except StopIteration:
                if self._prev_is_stop_iteration:
                    raise ValueError('We encountered StopIteration successsibly. This is probably because the base_elems is empty.')
                self._prev_is_stop_iteration = True
                self._is_elems_cached = True
                self._cur_iter = self._make_current_iterable()


@profile
def down_sample_streaming(elems: Iterable[Any],
                          elem2type_func: Callable[[Any], Any],
                          distrib='sqrl',
                          min_sampling_prob=0.1,  # to prevent too many rejections
                          burn_in=1000,
                          recalc_interval=10):
    """
    サンプルのタイプをi (= 1 to N)とする．
    推定しした分布をPe(i)，実現したい分布をP0(i)とする．

    今，Pe(i)に対してダウンサンプル重み w(i) in [0.0, 1.0]を付与した分布 Pw(i) = w(i) x Pe(i) からサンプリングすることにより，P0(i)を実現することを考える．
    達成されるべき条件は，

    Pw(i) / Pw(m) = w(i) x Pe(i) / w(m) x Pe(m) = P0(i) / P0(m)  (i = 1 to N-1)

    である．ここで，mは基準点である．
    また，確率の正規化のため，条件はN - 1個で十分であることに注意せよ．

    さて，w(i)はN変数である一方で，条件式はN-1つである．
    よって，w(i)のうちの１つ，基準点w(m)を自由に選ぶことができる．

    今，解離度を以下で定義する: D(i) = P0(i) / Pe(i)．
    解離度が一番小さいj = argmin{D(i)}というのは，最もダウンサンプリングを"したくない"タイプである．
    よって，jに対しては，一切ダウンサンプルしないことが，効率化に繋がる．
    よって，m = j = argmin{D(i)}, w(m) = 1.0 とする．

    その他のw(i) は，
    w(i) = w(m) x (Pe(m) / Pe(i)) x (P0(i) / P0(m)) 
         = D(i) / D(m)
    として求まる．
    """

    if math.isclose(min_sampling_prob, 0.0, abs_tol=0.01):
        logger.warning('setting min_sampling_prob=0.0 may reject many samples, especially if there are very rare sample types'
                       ', because manjor samples must be down-sampled to be comparable to the rare samples.')
    counts = defaultdict(int)
    w: Dict[Any, float] = {}
    total_counts = 0

    @profile
    def should_sample(i: int, new_type: Any) -> bool:
        nonlocal counts
        nonlocal total_counts
        nonlocal w
        counts[new_type] += 1
        total_counts  += 1
        is_burn_in = i < burn_in

        if distrib == 'linear':
            scale_func = lambda c: c
        elif distrib == 'sqrt':
            scale_func = lambda c: math.sqrt(c)
        elif distrib == 'logE':
            scale_func = lambda c: math.log(c + 1)
        elif distrib == 'log10':
            scale_func = lambda c: math.log10(c + 1)
        else:
            raise ValueError()

        if is_burn_in or new_type not in w or i % recalc_interval == 0:
            P_estim = {type_: counts[type_] / total_counts for type_ in counts}

            scaled_counts = {type_: scale_func(count) for type_, count in counts.items()}
            scaled_count_sum = sum(scaled_counts.values())
            P_0 = {type_: scaled_count / scaled_count_sum for type_, scaled_count in scaled_counts.items()}

            D = {type_: P_0[type_] / P_estim[type_] for type_ in counts}

            m = sorted((count, type_) for type_, count in D.items())[-1][1]

            w = {type_: D[type_] / D[m] for type_ in P_0.keys()}

        DEBUG = False
        if DEBUG:
            print('\n\n\n')
            print(f'========================== down_sample_streaming [{total_counts}] ======================')
            for name, dic in [('P_estim', P_estim),
                              ('P_0', P_0),
                              ('D', D),
                              ('m', m),
                              ('w', w)]:
                print('')
                print(f'---------------------------------- {name} ------------------------')
                pprint(dic)

            print('')
            print(f'---------------------------------- w["{new_type}"] ------------------------')
            print(w[new_type])

        if is_burn_in:
            return False
        else:
            sampling_prob = w[new_type]
            return random.random() < max(sampling_prob, min_sampling_prob)

    for i_elem, elem in enumerate(elems):
        if should_sample(i_elem, elem2type_func(elem)):
            yield elem
        # else:
        #     logger.critical('rejected sample %s', str(elem))
