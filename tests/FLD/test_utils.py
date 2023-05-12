from typing import List
from pprint import pprint
from collections import defaultdict
from FLD_generator.utils import (
    weighted_sampling,
    weighted_shuffle,
    nested_merge,
    make_combination,
    chained_sampling_from_weighted_iterators,
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


if __name__ == '__main__':
    test_weighted_sampling()
    test_weighted_shuffle()
    test_nested_merge()
    test_make_combination()
    test_chained_sampling_from_weighted_iterators()
