from typing import List, Set
from formal_logic.formula import Formula


def test_formula():

    def check_reps(formulas: List[Formula], gold_reps: Set[str]) -> bool:
        return {f.rep for f in formulas} == gold_reps

    assert check_reps(Formula('{A}{a} -> {B}{b} v {C}x v {D}').predicates, {'{A}', '{B}', '{C}', '{D}'})
    assert check_reps(Formula('{A}{a} -> {B}{b} v {C}x v {D}').constants, {'{a}', '{b}'})
    assert check_reps(Formula('{A}{a} -> {B}{b} v {C}x v {D}').variables, {'x'})
    assert check_reps(Formula('{A}{a} -> {B}{b} v {C}x v {D}').PASs, {'{A}{a}', '{B}{b}', '{C}x', '{D}'})

    assert check_reps(Formula('{A}{a} {B}{b} {C} {D}').unary_predicates, {'{A}', '{B}'})
    assert check_reps(Formula('{A}{a} {B}{b} {C} {D}').zeroary_predicates, {'{C}', '{D}'})

    assert check_reps(Formula('(x): {A}x -> {B}x').universal_variables, {'x'})
    assert check_reps(Formula('(Ex): {A}x -> {B}x').existential_variables, {'x'})


if __name__ == '__main__':
    test_formula()
