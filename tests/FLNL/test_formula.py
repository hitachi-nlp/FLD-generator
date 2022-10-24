from typing import List, Set
from FLNL.formula import Formula, negate


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


def test_wo_quantifier():

    def _test_wo_quantifier(rep: str, gold: str):
        assert Formula(rep).wo_quantifier.rep == gold

    _test_wo_quantifier('(x): {A}x', '{A}x')
    _test_wo_quantifier('(x): ({A}x & {B}x)', '({A}x & {B}x)')
    _test_wo_quantifier('((x): ({A}x & {B}x))', '(({A}x & {B}x))')
    _test_wo_quantifier('¬((x): ({A}x & {B}x))', '¬(({A}x & {B}x))')


def test_negate():

    def _test_negate(rep: str, gold: str) -> bool:
        return negate(Formula(rep)).rep == gold

    assert _test_negate('{A}', '¬{A}')
    assert _test_negate('{A}{a}', '¬{A}{a}')
    assert _test_negate('({A})', '¬({A})')

    assert _test_negate('{A} v {B}', '¬({A} v {B})')
    assert _test_negate('({A} v {B})', '¬({A} v {B})')
    assert _test_negate('({A} v {B}) -> {C}', '¬(({A} v {B}) -> {C})')
    assert _test_negate('({A} v {B}) -> ({C} v {D})', '¬(({A} v {B}) -> ({C} v {D}))')
    assert _test_negate('({A} v {B}) -> ({C} v {D})', '¬(({A} v {B}) -> ({C} v {D}))')
        
    assert _test_negate('¬{A}', '¬¬{A}')
    assert _test_negate('¬{A}{a}', '¬¬{A}{a}')
    assert _test_negate('¬({A})', '¬¬({A})')
    assert _test_negate('¬({A} v {B})', '¬¬({A} v {B})')
    assert _test_negate('¬({A} v {B}) -> {C}', '¬(¬({A} v {B}) -> {C})')

    assert _test_negate('(x): ¬(¬{A}x v {B}x)', '¬((x): ¬(¬{A}x v {B}x))')

    assert _test_negate('¬((x): {A}x)', '¬¬((x): {A}x)')


if __name__ == '__main__':
    test_formula()
    test_wo_quantifier()
    test_negate()
