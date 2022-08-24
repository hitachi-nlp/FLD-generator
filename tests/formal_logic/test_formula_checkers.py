from typing import List
from formal_logic.formula import Formula
from formal_logic.formula_checkers import (
    # _search_inconsistent_subformula,
    _get_boolean_values,

    is_single_formula_inconsistent,
    is_formulas_inconsistent,
    is_single_formula_nonsense,
)
from logger_setup import setup as setup_logger


def test_get_boolean_values():
    assert _get_boolean_values(Formula('{A}'), Formula('{A}')) == {'T'}
    assert _get_boolean_values(Formula('¬{A}'), Formula('{A}')) == {'F'}
    assert _get_boolean_values(Formula('{A}{a}'), Formula('{A}{a}')) == {'T'}
    assert _get_boolean_values(Formula('¬{A}{a}'), Formula('{A}{a}')) == {'F'}
    assert _get_boolean_values(Formula('{A}x'), Formula('{A}x')) == {'T'}
    assert _get_boolean_values(Formula('¬{A}x'), Formula('{A}x')) == {'F'}

    assert _get_boolean_values(Formula('({A} & {B})'), Formula('{A}')) == {'T'}
    assert _get_boolean_values(Formula('(¬{A} & {B})'), Formula('{A}')) == {'F'}
    assert _get_boolean_values(Formula('({A} & {B})'), Formula('{B}')) == {'T'}
    assert _get_boolean_values(Formula('({A} & ¬{B})'), Formula('{B}')) == {'F'}

    assert _get_boolean_values(Formula('({A} v {B})'), Formula('{A}')) == {'Unknown'}
    assert _get_boolean_values(Formula('(¬{A} v {B})'), Formula('{A}')) == {'Unknown'}
    assert _get_boolean_values(Formula('({A} v {B})'), Formula('{B}')) == {'Unknown'}
    assert _get_boolean_values(Formula('({A} v ¬{B})'), Formula('{B}')) == {'Unknown'}

    assert _get_boolean_values(Formula('({A} & ¬{A})'), Formula('{A}')) == {'T', 'F'}

    # assert _get_boolean_values(Formula('{C} or ({A} & ¬{B})'), Formula('{A}')) == {'Unknown'}


def test_single_formula_is_inconsistent():
    assert is_single_formula_inconsistent(Formula('({A} & ¬{A})'))
    assert is_single_formula_inconsistent(Formula('({A}{a} & ¬{A}{a})'))

    assert is_single_formula_inconsistent(Formula('(x): ({A}x & ¬{A}x)'))

    # The following formula is inconsistent but we can not detect it,
    # since we do not determine the boolean values of predicate-arguments which include existential variables.
    assert not is_single_formula_inconsistent(Formula('(Ex): ({A}x & ¬{A}x)'))

    # assert not _single_formula_is_inconsistent(Formula('{B} v ({A}x & ¬{A}x)'))


def test_is_formulas_inconsistent():
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('{B}{b}'),
    ])


    assert is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('¬{A}{a}'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('¬{A}{b}'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('¬{B}{b}'),
    ])


    assert is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('(¬{A}{a} & {B}{a})'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('({A}{a} & {B}{a})'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('({B}{a} & {C}{a})'),
    ])


    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('(¬{A}{a} v {B}{a})'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('({A}{a} v {B}{a})'),
    ])
    assert not is_formulas_inconsistent([
        Formula('{A}{a}'),
        Formula('({B}{a} v {C}{a})'),
    ])

    assert is_formulas_inconsistent([
        Formula('(x): ¬{A}x'),
        Formula('{A}{a}'),
    ])

    assert is_formulas_inconsistent([
        Formula('(x): {A}x'),
        Formula('(x): (¬{A}x & {B}x)'),
    ])

    # The following formulas are inconsistent
    # but we can not detect since we can not say nothing about (Ex) for technical reasons.
    # assert is_formulas_inconsistent([
    #     Formula('(x): {A}x'),
    #     Formula('(Ex): (¬{A}x & {B}x)'),
    # ])

    assert not is_formulas_inconsistent([
        Formula('(Ex): {A}x'),
        Formula('(Ex): (¬{A}x & {B}x)'),
    ])


def test_is_single_formula_nonsense():
    assert is_single_formula_nonsense(Formula('{A}{a} -> ¬{A}{a}'))
    assert is_single_formula_nonsense(Formula('¬{A}{a} -> {A}{a}'))
    assert not is_single_formula_nonsense(Formula('¬{A}{a} -> {A}{b}'))

    assert is_single_formula_nonsense(Formula('(x): {A}x -> ¬{A}x'))
    assert is_single_formula_nonsense(Formula('(x): ¬{A}x -> {A}x'))
    assert not is_single_formula_nonsense(Formula('(x): ¬{A}x -> {B}x'))

    assert is_single_formula_nonsense(Formula('({A}{a} & {B}{b}) -> ¬{A}{a}'))
    assert is_single_formula_nonsense(Formula('(¬{A}{a} & {B}{b}) -> {A}{a}'))

    assert not is_single_formula_nonsense(Formula('({A}{a} v {B}{b}) -> ¬{A}{a}'))
    assert not is_single_formula_nonsense(Formula('(¬{A}{a} v {B}{b}) -> {A}{a}'))

    assert is_single_formula_nonsense(Formula('{A}{a} -> {A}{a}'))
    assert is_single_formula_nonsense(Formula('({A}{a} & {A}{a})'))
    assert is_single_formula_nonsense(Formula('({A}{a} v {A}{a})'))


if __name__ == '__main__':
    setup_logger()

    test_single_formula_is_inconsistent()
    test_get_boolean_values()
    test_is_formulas_inconsistent()
    test_is_single_formula_nonsense()
