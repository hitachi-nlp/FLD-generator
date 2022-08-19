from typing import List
from formal_logic.replacements import (
    _expand_op,
    generate_universal_quantifier_elimination_arguments,
    formula_is_identical_to,
    argument_is_identical_to,
)
from formal_logic.proof_tree_generators import generate_replacement_mappings_from_formula
from formal_logic.formula import Formula
from formal_logic.argument import Argument


# TODO: update this test code to be consistent with allow_complication=True
# def test_replacements():
# 
#     formula = Formula('(x): {F}x {G}{a} {G}{b} -> {H}x')
#     other_formula = Formula('(y): {F}y {I}{a} {J}{b} -> {K}{y}')
# 
#     print('-------------------- placeholders --------------------')
#     print('formula                          :', formula)
#     print('formula placeholders             :', formula.predicates + formula.constants)
# 
#     print('other_formula                    :', other_formula)
#     print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)
# 
#     replaced_formulas = list(generate_replacement_mappings_from_formula([formula],
#                                                                         [other_formula],
#                                                                         allow_complication=True))
#     # print('-------------------- replacements --------------------')
#     # for replacements in replaced_formlas:
#     #     print('')
#     #     print('replacements     :', replacements)
#     #     print('replaced formula :', replace(formula, replacements))
# 
#     assert(len(formula.predicates) == 3)
#     assert(len(formula.constants) == 2)
# 
#     assert(len(other_formula.predicates) == 4)
#     assert(len(other_formula.constants) == 2)
# 
#     assert(len(replaced_formulas) == (2 * 4)**3 * 2**2)  # 2*4 because of the negated patterns


def test_expand_op():
    assert _expand_op(Formula('(x): ({P} v ¬{Q})x -> ({R} v ¬{S})x')).rep == '(x): ({P}x v ¬{Q}x) -> ({R}x v ¬{S}x)'
    assert _expand_op(Formula('({P} v ¬{Q}){a} -> ({R} v ¬{S}){b}')).rep == '({P}{a} v ¬{Q}{a}) -> ({R}{b} v ¬{S}{b})'


def test_formula_is_identical_to():
    this = Formula('{A}{a} -> {B}{b}')
    that = Formula('{A}{a} -> {A}{a}')

    assert formula_is_identical_to(this, that, allow_many_to_one_replacements=True)
    assert not formula_is_identical_to(that, this, allow_many_to_one_replacements=True)

    assert not formula_is_identical_to(this, that, allow_many_to_one_replacements=False)
    assert not formula_is_identical_to(that, this, allow_many_to_one_replacements=False)


def test_argument_is_identical_to():

    assert argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{A}'),
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
        ),
    )

    assert argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{C}'),
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
        ),
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{C}'),
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
        ),
        allow_many_to_one_replacements=False,
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{A}'),
        ),
        Argument(
            [Formula('{P}'), Formula('{P} -> {Q}')],
            Formula('{Q}'),
        ),
    )


def test_generate_universal_quantifier_elimination_arguments():

    def check_generation(formula: Formula, expected_formulas: List[Formula]):
        generated_formulas = list(generate_universal_quantifier_elimination_arguments(formula))
        print('input formula:')
        print(f'    {formula.rep}')
        print('output formula:')
        for generated_formula in generated_formulas:
            print(f'    {generated_formula.rep}')

        assert(len(generated_formula) == len(expected_formulas))


if __name__ == '__main__':
    # test_replacements()
    test_expand_op()
    test_formula_is_identical_to()
    test_argument_is_identical_to()
