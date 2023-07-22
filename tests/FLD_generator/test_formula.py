from typing import List, Set
from FLD_generator.formula import Formula, negate, require_outer_brace


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



def test_require_outer_brace():

    def _test(rep: str,
              gold_do_require: bool,
              require_for_single_predicate=False,
              require_for_negated_formula=False) -> bool:
        do_require = require_outer_brace(Formula(rep),
                                         require_for_single_predicate=require_for_single_predicate,
                                         require_for_negated_formula=require_for_negated_formula)
        return do_require is gold_do_require

    assert _test('{A}', False)
    assert _test('{A}', True, require_for_single_predicate=True)
    assert _test('¬{A}', False)
    assert _test('¬{A}', True, require_for_negated_formula=True)


    assert _test('{A} & {B}', True)
    assert _test('({A} & {B})', False)
    assert _test('({A}) & {B}', True)
    assert _test('{A} & ({B})', True)

    assert _test('¬{A} & {B}', True)
    assert _test('¬({A} & {B})', False)
    assert _test('¬({A} & {B})', True, require_for_negated_formula=True)
    assert _test('¬(¬{A} & {B})', False)
    assert _test('¬({A} & ¬{B})', False)


    assert _test('({A} & {B}) & ({C} & {D})', True)
    assert _test('(({A} & {B}) & ({C} & {D}))', False)


    assert _test('({A} & {B}) & {C}', True)
    assert _test('(({A} & {B}) & {C})', False)

    assert _test('¬({A} & {B}) & {C}', True)
    assert _test('(({A} & {B}) & {C})', False)


    assert _test('(x): {A}x', True)
    assert _test('(x): {A}x & {B}x', True)
    assert _test('((x): {A}x & {B}x)', False)



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

    assert _test_negate('({A} & {B})', '¬({A} & {B})')

    assert _test_negate('({C}{c} & {B}{c})', '¬({C}{c} & {B}{c})')


if __name__ == '__main__':
    test_formula()
    test_wo_quantifier()
    test_require_outer_brace()
    test_negate()
