from typing import List
from pprint import pprint

from FLD_generator.formula import Formula
from FLD_generator.formula_checkers.z3_checkers.checkers import (
    parse,
    check_sat,
    is_stronger,
    is_equiv,
    is_weaker,
)


def test_parse():

    def _test_parse(rep: str):
        print('\n\n============ _test_parse() ============')
        parsed = parse(rep)

        print('\n------------ rep ------------')
        print(rep)
        print('\n------------ parsed ------------')
        print(parsed)

    # unary
    _test_parse(
        '{A}{a}',
    )

    _test_parse(
        '¬¬{A}{a}',
    )

    _test_parse(
        '{A}{a} v {B}{b}',
    )

    _test_parse(
        '¬({A}{a} v {B}{b})',
    )

    _test_parse(
        '({A}{a} v {B}{b}) -> {C}{c}',
    )

    _test_parse(
        '({A}{a} v ({B}{b} v {C}{c})) -> {D}{d}',
    )

    _test_parse(
        '(x): ({A}x v {B}x) -> {C}x',
    )

    _test_parse(
        '¬((x): ({A}x v {B}x) -> {C}x)',
    )

    # zeroary
    _test_parse(
        '({A} v ({B} v {C})) -> {D}',
    )


def test_check_sat():

    def _test_check_sat(formula_reps: List[str], gold: bool):
        print('\n\n============ _test_check_sat() ============')
        is_sat, model, parse = check_sat([Formula(rep) for rep in formula_reps],
                                         get_model=True,
                                         get_parse=True)

        print('\n\n------------ formlas ------------')
        pprint(formula_reps)

        print('\n\n------------ sat ------------')
        print(is_sat)

        print('\n\n------------ model ------------')
        print(model)

        print('\n\n------------ parse ------------')
        print(parse)

        assert is_sat is gold

    _test_check_sat(
        [
            '{A}',
            '¬¬{A}',
        ],
        True,
    )

    _test_check_sat(
        [
            '{A}',
            '¬{A}',
        ],
        False,
    )

    _test_check_sat(
        [
            '{A} -> {B}',
            '{A}',
            '{B}',
        ],
        True,
    )

    _test_check_sat(
        [
            '{A} -> {B}',
            '{A}',
            '¬{B}',
        ],
        False,
    )

    _test_check_sat(
        [
            '{A} & {B}',
            '{A}',
            '{B}',
        ],
        True,
    )

    _test_check_sat(
        [
            '{A} & {B}',
            '{A}',
            '¬{B}',
        ],
        False,
    )

    _test_check_sat(
        [
            '{A} v {B}',
            '{A}',
            '{B}',
        ],
        True,
    )

    _test_check_sat(
        [
            '{A} v {B}',
            '{A}',
            '¬{B}',
        ],
        True,
    )

    _test_check_sat(
        [
            '{A} v {B}',
            '¬{A}',
            '¬{B}',
        ],
        False,
    )

    _test_check_sat(
        [
            '{A} -> {B}',
            '¬{B} -> ¬{A}',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x',
            '{A}{a}',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x',
            '¬{A}{a}',
        ],
        False,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '{A}{a}',
            '{B}{a}',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '{A}{a}',
            '¬{B}{a}',
        ],
        False,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): {A}x -> {B}x',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): {A}x -> ¬{B}x',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): ¬({A}x -> {B}x)',
        ],
        False,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '¬((Ex): {A}x -> {B}x)',
        ],
        False,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): ¬{B}x -> ¬{A}x',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): ¬({A}x -> {B}x)',
        ],
        False,
    )

    _test_check_sat(
        [
            '(x): {A}x -> {B}x',
            '(Ex): ¬(¬{B}x -> ¬{A}x)',
        ],
        False,
    )

    _test_check_sat(
        [
            '¬{FR} -> ¬({GP} & {CT})',
            '¬{A}',
            '¬{B}',
            '(¬{A} & ¬{B}) -> ¬{FR}',
        ],
        True,
    )

    _test_check_sat(
        [
            '({A} v ({B} v {C})) -> {D}',
            '{A}',
            '{B}',
            '{C}',
            '{D}',
        ],
        True,
    )

    _test_check_sat(
        [
            '({A} v ({B} v {C})) -> {D}',
            '{A}',
            '{B}',
            '{C}',
            '¬{D}',
        ],
        False,
    )

    _test_check_sat(
        [
            '({A} v ({B} v {C})) -> {D}',
            '¬{A}',
            '¬{B}',
            '¬{C}',
            '¬{D}',
        ],
        True,
    )

    _test_check_sat(
        [
            '(x): (¬{U}{a} & {A}{a}) -> ¬{FP}x',
            '({EH}{aa} & {JG}{aa})',
            '{A}{a}',
            '{B}{a}',
            '(x): (¬{JJ}{l} & ¬{EB}{l}) -> ¬{U}x',
            '(x): ({A}{a} & {B}{a}) -> ¬{JJ}x',
            '({FP}{am} & {FU}{am}) -> ¬{EB}{l}',
            '({FP}{am} & {FU}{am})',
        ],
        False,
    )


def test_strength():

    def _test_strength(this_rep: str, that_rep: str, is_stronger_gold: bool):
        print('\n\n============ _test_is_stronger() ============')
        print('\n------------ rep ------------')
        print(this_rep, that_rep)
        _is_stronger = is_stronger(
            this_rep,
            that_rep,
        )
        print('\n------------ is_stronger ------------')
        print(_is_stronger)
        assert _is_stronger is is_stronger_gold

        print('\n\n============ _test_is_weaker() ============')
        print('\n------------ rep ------------')
        print(this_rep, that_rep)
        _is_weaker = is_weaker(
            this_rep,
            that_rep,
        )
        print('\n------------ is_weaker ------------')
        print(_is_weaker)
        assert _is_weaker is not is_stronger_gold

    _test_strength(
        Formula('{A} & {B}'),
        Formula('{A}'),
        True,
    )

    _test_strength(
        Formula('{A}'),
        Formula('{A} & {B}'),
        False,
    )

    _test_strength(
        Formula('{A} -> {C}'),
        Formula('({A} & {B}) -> {C}'),
        True,
    )

    _test_strength(
        Formula('({A} & {B}) -> {C}'),
        Formula('{A} -> {C}'),
        False,
    )


def test_equiv():

    def _test_is_equiv(this_rep: str, that_rep: str, is_equiv_gold: bool):
        print('\n\n============ _test_is_equiv() ============')
        print('\n------------ rep ------------')
        print(this_rep, that_rep)
        _is_equiv = is_equiv(
            this_rep,
            that_rep,
        )
        print('\n------------ is_equiv ------------')
        print(_is_equiv)
        assert _is_equiv is is_equiv_gold

    _test_is_equiv(
        Formula('({A} & {B})'),
        Formula('({B} & {A})'),
        True,
    )

    _test_is_equiv(
        Formula('{A}'),
        Formula('({B} & {A})'),
        False,
    )

    _test_is_equiv(
        Formula('{A} -> {B}'),
        Formula('¬{B} -> ¬{A}'),
        True,
    )

    _test_is_equiv(
        Formula('{A} -> {B}'),
        Formula('{B} -> {A}'),
        False,
    )


if __name__ == '__main__':
    test_parse()
    test_check_sat()
    test_strength()
    test_equiv()
