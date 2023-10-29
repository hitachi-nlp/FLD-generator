from typing import List
import random
import math
from pprint import pprint
from collections import defaultdict

from FLD_generator.utils import (
    weighted_sampling,
    weighted_shuffle,
    nested_merge,
    make_combination,
    chained_sampling_from_weighted_iterators,
    down_sample_streaming,
)


def test_weighted_sampling():
    print('\n\n\n ======== test_weighted_sampling() ========')

    def stochastic_test(weights: List[float], trial=10000):
        print('\n\n') 
        print(f'---- stochastic_test (weights={weights}) ----')

        counts = defaultdict(int)
        for _ in range(trial):
            counts[weighted_sampling(weights)] += 1
        pprint(dict(counts))

        sum_weight = sum(weights)
        ratios = [weight / sum_weight for weight in weights]
        for sampled_idx, count in counts.items():
            assert(abs(count - trial * ratios[sampled_idx]) < trial * 0.05)

    stochastic_test([1.0, 0.0, 0.0])
    stochastic_test([0.0, 1.0, 1.0])
    stochastic_test([0.4, 0.3, 0.3])
    stochastic_test([1.0, 1.0, 1.0])


def test_weighted_shuffle():

    print('\n\n\n ======== test_weighted_shuffle() ========')

    def stochastic_test(weights: List[float], trial=10000):
        print('\n\n') 
        print(f'---- stochastic_test (weights={weights}) ----')

        non_zero_weight_idxs = [i_weight for i_weight, weight in enumerate(weights) if weight != 0.0]
        counts = defaultdict(int)
        for _ in range(trial):
            sampled_idxs = [sampled_idx for sampled_idx in weighted_shuffle(weights)]

            assert(len(sampled_idxs) == len(non_zero_weight_idxs))
            assert(set(sampled_idxs) == set(non_zero_weight_idxs))

            counts[sampled_idxs[0]] += 1  # only the first sample is unbiased.
        pprint(dict(counts))

        sum_weight = sum(weights)
        ratios = [weight / sum_weight for weight in weights]
        for sampled_idx, count in counts.items():
            assert(abs(count - trial * ratios[sampled_idx]) < trial * 0.05)

    stochastic_test([1.0, 0.0, 0.0])
    stochastic_test([0.0, 1.0, 1.0])
    stochastic_test([0.4, 0.3, 0.3])
    stochastic_test([1.0, 1.0, 1.0])


def test_nested_merge():

    this = {
        'A': {
            'a': [0, 1]
        },
        'B': {
            'a': [0, 1],
        },
    }
    that = {
        'A': {
            'a': [2, 3]
        },
        'B': {
            'a': [2, 3],
            'b': [2, 3],
        },
    }
    merged = nested_merge(this, that)

    assert merged['A']['a'] == [0, 1, 2, 3]
    assert merged['B']['a'] == [0, 1, 2, 3]
    assert merged['B']['b'] == [2, 3]


def test_make_combination():
    print('\n\ntest_make_combination()')

    def int_generator():
        for i in range(0, 3):
            yield i


    def str_generator1():
        for rep in ['a', 'b', 'c']:
            yield rep


    def str_generator2():
        for rep in ['hoge', 'fuga', 'piyo']:
            yield rep

    combs = make_combination([
        int_generator,
        str_generator1,
        str_generator2,
    ])

    combs = list(combs)
    for comb in combs:
        print(comb)
    assert(len(combs) == 3**3)


def test_chained_sampling_from_weighted_iterators():

    def generator_large():
        for i in range(0, 100):
            yield 'large'

    def generator_small():
        for i in range(0, 10):
            yield 'small'

    def show_sampling(weights: List[float]) -> None:
        print('\n\n')
        print(f'==== show_sampling (weights={weights} ====')
        for item in chained_sampling_from_weighted_iterators(
            [generator_large(), generator_small()],
            weights,
        ):
            print('    ', item)
            
    show_sampling([10.0, 1.0])
    show_sampling([1.0, 1.0])
    show_sampling([0.1, 1.0])


def test_down_sample():

    def skewed_generator(total_count: int, second_weight: float):
        for _ in range(total_count):
            rnd = random.random()
            if rnd < second_weight:
                yield 1
            else:
                yield 0

    def _test_sampling(second_weight: float, distrib: str):
        total_count = 10000

        print('\n\n\n')
        print(f'================== test sampling with distrib = {distrib} ==================')
        distribd_elems = down_sample_streaming(
            skewed_generator(total_count, second_weight),
            lambda elem: elem,
            distrib=distrib,
            min_sampling_prob=0.0,
        )

        counts = defaultdict(int)
        total_counts = 0
        for elem in distribd_elems:
            counts[elem] += 1
            total_counts += 1

        for elem, count in sorted(counts.items()):
            print(f'{elem}: {count / total_counts:.5f}')

        if distrib == 'linear':
            weight_func = lambda c: c
        elif distrib == 'sqrt':
            weight_func = lambda c: math.sqrt(c)
        elif distrib == 'logE':
            weight_func = lambda c: math.log(c + 1)
        elif distrib == 'log10':
            weight_func = lambda c: math.log10(c + 1)
        else:
            raise ValueError()

        gold_ratio = weight_func(second_weight * total_count) / weight_func(1 * total_count - second_weight * total_count)
        pred_ratio = counts[1] / counts[0]
        print('\n\n')
        print(f'================================= restuls with distrib={distrib} =================================')
        print(f'gold_ratio: {gold_ratio:.5f}   pred_ratio: {pred_ratio:.5f}')

        assert math.isclose(gold_ratio, pred_ratio, abs_tol=0.1)

    second_weight = 0.1
    _test_sampling(second_weight, 'linear')
    _test_sampling(second_weight, 'sqrt')
    _test_sampling(second_weight, 'logE')
    _test_sampling(second_weight, 'log10')


if __name__ == '__main__':
    # test_weighted_sampling()
    # test_weighted_shuffle()
    # test_nested_merge()
    # test_make_combination()
    # test_chained_sampling_from_weighted_iterators()
    test_down_sample()
