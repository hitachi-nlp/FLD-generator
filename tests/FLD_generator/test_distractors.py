from typing import List, Optional
import statistics
import math
import logging

from FLD_generator.proof import ProofTree, ProofNode
from FLD_generator.formula import Formula
from FLD_generator.formula_distractors import (
    FormulaDistractor,
    VariousFormUnkownInterprandsDistractor,
    SimplifiedFormulaDistractor,
    NegativeTreeDistractor,
)
from logger_setup import setup as setup_logger


def _generate_and_print(distractor: FormulaDistractor,
                        formulas: List[Formula],
                        num_distractors: int,
                        **kwargs) -> List[Formula]:
    print('\n=============== _generate_and_print() ======================')
    print('\nformulas:')
    for formula in formulas:
        print('    ', formula)

    nodes = [ProofNode(formula) for formula in formulas]
    tree = ProofTree()
    for node in nodes:
        tree.add_node(node)

    distractor_formulas, others = distractor.generate(tree,
                                                      num_distractors,
                                                      allow_smaller_proofs=True,
                                                      **kwargs)

    print('\ndistractors:')
    for distractor_formula in distractor_formulas:
        print('    ', distractor_formula)

    return distractor_formulas


def test_various_form_distractor():

    def _test_distractor(rep: str,
                         ng_reps: List[str],
                         prototype_formulas: Optional[List[Formula]] = None):
        num_distractors = 10
        distractor = VariousFormUnkownInterprandsDistractor(prototype_formulas=prototype_formulas,)

        ratios = []
        original_formula = Formula(rep)
        for _ in range(0, 10):
            distractor_formulas = _generate_and_print(
                distractor,
                [original_formula],
                num_distractors,
            )
            ratio = len([f for f in distractor_formulas if f.rep.endswith('{a}')]) / len(distractor_formulas)

            ratios.append(ratio)
            assert all(
                all(distractor_formula.rep != ng_rep for ng_rep in ng_reps)
                for distractor_formula in distractor_formulas
            )
        ratio = statistics.mean(ratios)

    _test_distractor(
        '{A}',
        ['{A}'],
    )

    _test_distractor(
        '{A}{a}',
        ['{A}{a}'],
    )

    _test_distractor(
        '({A} & {B})',
        ['({A} & {A})', '({A} & {B})', '({B} & {A})', '({B} & {B})'],
    )

    _test_distractor(
        '({A}{a} & {B}{b})',
        ['({A}{a} & {A}{a})', '({A}{a} & {B}{b})', '({B}{b} & {A}{a})', '({B}{b} & {B}{b})'],
    )

    _test_distractor(
        '({A}{a} & {B}{b})',
        ['({A}{a} v {A}{a})', '({A}{a} v {B}{b})', '({B}{b} v {A}{a})', '({B}{b} v {B}{b})'],
        prototype_formulas=[Formula('({C}{c} v {D}{d})')]
    )
    

def test_simplified_formula_distractor():

    distractor = SimplifiedFormulaDistractor()

    _generate_and_print(
        distractor,
        [
            Formula('(¬{A}{a} & {B}{b}) -> ¬{C}{c}'),
        ],
        5,
        best_effort=True,
    )

    _generate_and_print(
        distractor,
        [
            Formula('¬(¬{A}{a} & {B}{b}) -> ¬{C}{c}'),
        ],
        5,
        best_effort=True,
    )


if __name__ == '__main__':
    setup_logger(level=logging.INFO)

    test_various_form_distractor()
    # test_simplified_formula_distractor()
