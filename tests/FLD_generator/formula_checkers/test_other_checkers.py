from typing import List
from FLD_generator.formula import Formula
from FLD_generator.formula_checkers.other_checkers import (
    _get_boolean_values,
    is_predicate_arity_consistent_set,
    is_nonsense,
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

    assert _get_boolean_values(Formula('¬({A} v {B})'), Formula('{A}')) == {'F'}
    assert _get_boolean_values(Formula('¬({A} & {B})'), Formula('{A}')) == {'Unknown'}

    assert _get_boolean_values(Formula('¬({A} & {B})'), Formula('{A}')) == {'Unknown'}

    assert _get_boolean_values(Formula('(x): {A}x'), Formula('{A}x')) == {'T'}
    assert _get_boolean_values(Formula('(x): ({A}x & {B}x)'), Formula('{A}x')) == {'T'}
    assert _get_boolean_values(Formula('¬((x): {A}x)'), Formula('{A}x')) == {'Unknown'}


def test_is_predicate_arity_consistent():
    assert is_predicate_arity_consistent_set(
        [Formula('{A}{a} v {B}{b}'), Formula('{C}')]
    )

    assert not is_predicate_arity_consistent_set(
        [Formula('{A}{a} v {B}{b}'), Formula('{A}')]
    )


def test_is_nonsense():
    def _is_nonsense(*args, **kwargs):
        return is_nonsense(*args, **kwargs, allow_detect_tautology_contradiction=True)

    assert not is_nonsense(Formula('{A}{a} -> ¬{A}{a}'))
    assert not is_nonsense(Formula('¬{A}{a} -> {A}{a}'))
    assert is_nonsense(Formula('¬{A}{a} -> {A}{b}'))

    assert not is_nonsense(Formula('(x): {A}x -> ¬{A}x'))
    assert not is_nonsense(Formula('(x): ¬{A}x -> {A}x'))
    assert is_nonsense(Formula('(x): ¬{A}x -> {B}x'))

    assert not is_nonsense(Formula('({A}{a} & {B}{b}) -> ¬{A}{a}'))
    assert not is_nonsense(Formula('(¬{A}{a} & {B}{b}) -> {A}{a}'))

    assert is_nonsense(Formula('({A}{a} v {B}{b}) -> ¬{A}{a}'))
    assert is_nonsense(Formula('(¬{A}{a} v {B}{b}) -> {A}{a}'))

    assert not is_nonsense(Formula('{A}{a} -> {A}{a}'))
    assert not is_nonsense(Formula('({A}{a} & {A}{a})'))
    assert not is_nonsense(Formula('({A}{a} v {A}{a})'))


if __name__ == '__main__':
    setup_logger()

    test_get_boolean_values()
    test_is_predicate_arity_consistent()
    test_is_nonsense()
