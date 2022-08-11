from typing import List
from formal_logic.formula import Formula
from formal_logic.formula_checker import (
    # _search_inconsistent_subformula,
    _get_boolean_values,

    is_single_formula_inconsistent,
    is_formulas_inconsistent,
    is_single_formula_nonsense,
)

# def test_search_inconsistent_formula():
#     assert _search_inconsistent_subformula(Formula('{B} ({A} & ¬{A})')).group() == '({A} & ¬{A})'
#     assert _search_inconsistent_subformula(Formula('{B} v ({A}{a} & ¬{A}{a})')).group() == '({A}{a} & ¬{A}{a})'
#     assert _search_inconsistent_subformula(Formula('{B} v ({A}x & ¬{A}x)')).group() == '({A}x & ¬{A}x)'
#     assert _search_inconsistent_subformula(Formula('{B} v ({A} & ¬{A})')).group() == '({A} & ¬{A})'


def test_single_formula_is_inconsistent():
    assert is_single_formula_inconsistent(Formula('({A} & ¬{A})'))
    assert is_single_formula_inconsistent(Formula('({A}{a} & ¬{A}{a})'))

    assert is_single_formula_inconsistent(Formula('(x): ({A}x & ¬{A}x)'))
    assert is_single_formula_inconsistent(Formula('(Ex): ({A}x & ¬{A}x)'))

    # assert not _single_formula_is_inconsistent(Formula('{B} v ({A}x & ¬{A}x)'))


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

    # assert _get_boolean_values(Formula('{C} or ({A} & ¬{B})'), Formula('{A}')) == {'Unknown'}


# def test_is_senseful():
#     assert is_senseful(Formula('{F}{a}'))
#     assert is_senseful(Formula('{F}{a} -> {G}{a}'))
#     assert is_senseful(Formula('(x): {F}x -> {G}x'))
# 
#     assert not is_senseful(Formula('{F}{a} -> ¬{F}{a}'))
#     assert not is_senseful(Formula('(x): {F}x -> ¬{F}x'))
# 
#     assert is_senseful(Formula('({F} & {G}){a}'))
#     assert is_senseful(Formula('({F} & {G}){a} -> {H}{a}'))
#     assert is_senseful(Formula('{F}{a} -> ({G} & {H}){a}'))
#     assert is_senseful(Formula('(x): ({F} & {G})x -> {H}x'))
#     assert is_senseful(Formula('(x): {F}x -> ({G} & {H})x'))
# 
#     assert not is_senseful(Formula('({F} & ¬{F}){a}'))
#     assert not is_senseful(Formula('({F} & {G}){a} -> ¬{F}{a}'))
#     assert not is_senseful(Formula('(¬{F} & {G}){a} -> {F}{a}'))
#     assert not is_senseful(Formula('({F} & ¬{F}){a} -> {G}{a}'))
#     assert not is_senseful(Formula('¬{F}{a} -> ({F} & {H}){a}'))
#     assert not is_senseful(Formula('{F}{a} -> (¬{F} & {H}){a}'))
#     assert not is_senseful(Formula('(x): (¬{F} & {G})x -> {F}x'))
#     assert not is_senseful(Formula('(x): ¬{F}x -> ({F} & {H})x'))
# 
#     assert is_senseful(Formula('({F} v {G}){a}'))
#     assert is_senseful(Formula('({F} v {G}){a} -> {H}{a}'))
#     assert is_senseful(Formula('{F}{a} -> ({G} v {H}){a}'))
#     assert is_senseful(Formula('(x): ({F} v {G})x -> {H}x'))
#     assert is_senseful(Formula('(x): {F}x -> ({G} v {H})x'))
# 
#     assert is_senseful(Formula('({F} v ¬{F}){a}'))
#     assert is_senseful(Formula('(¬{F} v {G}){a} -> {F}{a}'))
#     assert is_senseful(Formula('¬{F}{a} -> ({F} v {H}){a}'))
#     assert is_senseful(Formula('(x): (¬{F} v {G})x -> {F}x'))
#     assert is_senseful(Formula('(x): {F}x -> (¬{F} v {H})x'))


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
        Formula('(x): {A}x'),
        Formula('(x): (¬{A}x & {B}x)'),
    ])
    assert is_formulas_inconsistent([
        Formula('(x): {A}x'),
        Formula('(Ex): (¬{A}x & {B}x)'),
    ])
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
    # test_is_senseful()
    # test_search_inconsistent_formula()
    test_single_formula_is_inconsistent()
    test_get_boolean_values()
    test_is_formulas_inconsistent()
    test_is_single_formula_nonsense()
