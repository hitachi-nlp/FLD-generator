from typing import List
import statistics
import math

from FLNL.proof import ProofTree, ProofNode
from FLNL.formula import Formula
from FLNL.distractors import (
    FormalLogicDistractor,
    UnkownPASDistractor,
    SameFormUnkownInterprandsDistractor,
    NegatedHypothesisTreeDistractor,
)


def _generate_and_print(distractor: FormalLogicDistractor, formulas: List[Formula], num_distractors: int) -> List[Formula]:
    print('\nformulas:')
    for formula in formulas:
        print('    ', formula)

    nodes = [ProofNode(formula) for formula in formulas]
    tree = ProofTree()
    for node in nodes:
        tree.add_node(node)

    distractor_formulas = distractor.generate(tree, num_distractors)

    print('\ndistractors:')
    for distractor_formula in distractor_formulas:
        print('    ', distractor_formula)

    return distractor_formulas


def test_unknown_PAS_distractor():
    num_distractors = 1000
    distractor = UnkownPASDistractor(num_distractors)

    distractor_formulas = _generate_and_print(
        distractor,
        [
            Formula('{A}{a}'),
        ],
        num_distractors,
    )
    ratio = len([f for f in distractor_formulas if f.rep.endswith('{a}')]) / len(distractor_formulas)
    assert math.fabs(ratio - 0.5) < 0.1


def test_same_form_distractor():

    def _test_same_form_distractor(rep: str):
        num_distractors = 10
        distractor = SameFormUnkownInterprandsDistractor()

        ratios = []
        original_formula = Formula(rep)
        for _ in range(0, 100):
            distractor_formulas = _generate_and_print(
                distractor,
                [original_formula],
                num_distractors,
            )
            ratio = len([f for f in distractor_formulas if f.rep.endswith('{a}')]) / len(distractor_formulas)
            ratios.append(ratio)
            assert all(distractor_formula.rep != original_formula.rep for distractor_formula in distractor_formulas)
        ratio = statistics.mean(ratios)
        # assert math.fabs(ratio - 0.7) < 0.1

    _test_same_form_distractor('{A}{a}')
    _test_same_form_distractor('({A} & {B})')



if __name__ == '__main__':
    test_unknown_PAS_distractor()
    test_same_form_distractor()
