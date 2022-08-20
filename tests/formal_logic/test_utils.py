from typing import List
from pprint import pprint
from collections import defaultdict
from formal_logic.utils import weighted_sampling, weighted_shuffle


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

    print('\n\n\n ======== test_weighted_samplings_wo_replacement() ========')

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


if __name__ == '__main__':
    test_weighted_sampling()
    test_weighted_shuffle()
