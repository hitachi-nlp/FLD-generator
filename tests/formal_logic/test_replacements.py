from typing import List
from formal_logic.replacements import (
    _expand_op,
    generate_quantifier_arguments,
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

    assert formula_is_identical_to(this, that, allow_many_to_one_replacementg=True)
    assert not formula_is_identical_to(that, this, allow_many_to_one_replacementg=True)

    assert not formula_is_identical_to(this, that, allow_many_to_one_replacementg=False)
    assert not formula_is_identical_to(that, this, allow_many_to_one_replacementg=False)


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
        allow_many_to_one_replacementg=False,
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


def test_generate_quantifier_arguments():

    def check_generation(argument_type: str,
                         formula: Formula,
                         expected_arguments: List[Argument],
                         quantify_all_at_once=False):
        generated_arguments = list(
            generate_quantifier_arguments(argument_type, formula, id_prefix='test', quantify_all_at_once=quantify_all_at_once))
        print()
        print(f'--------- {argument_type} for "{formula.rep}" (quantify_all_at_once={quantify_all_at_once}) ------')
        for generated_argument in generated_arguments:
            print(f'{str(generated_argument)}')

        assert(len(generated_arguments) == len(expected_arguments))
        for generated_argument in generated_arguments:
            assert(any(argument_is_identical_to(generated_argument, expected_argument, allow_many_to_one_replacementg=False)
                       for expected_argument in expected_arguments))

    print('\n\n\n================= test_generate_quantifier_arguments() ====================')

    # ----------- universal_quantifier_elim --------------
    check_generation(
        'universal_quantifier_elim',
        Formula('{F}{a} -> {G}{a}'),
        [
            Argument(
                [Formula('(x): {F}x -> {G}x')],
                Formula('{F}{a} -> {G}{a}'),
            ),
        ]
    )

    check_generation(
        'universal_quantifier_elim',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('(x): ({F}x v {G}{b}) -> {H}{c}')],
                Formula('({F}{i} v {G}{b}) -> {H}{c}'),
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}x) -> {H}{c}')],
                Formula('({F}{a} v {G}{i}) -> {H}{c}'),
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}{b}) -> {H}x')],
                Formula('({F}{a} v {G}{b}) -> {H}{i}'),
            ),


            Argument(
                [Formula('(x): ({F}x v {G}x) -> {H}{c}')],
                Formula('({F}{i} v {G}{i}) -> {H}{c}'),
            ),
            Argument(
                [Formula('(x): ({F}x v {G}{b}) -> {H}x')],
                Formula('({F}{i} v {G}{b}) -> {H}{i}'),
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}x) -> {H}x')],
                Formula('({F}{a} v {G}{i}) -> {H}{i}'),
            ),

            Argument(
                [Formula('(x): ({F}x v {G}x) -> {H}x')],
                Formula('({F}{i} v {G}{i}) -> {H}{i}'),
            ),

        ]
    )

    check_generation(
        'universal_quantifier_elim',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('(x): ({F}x v {G}x) -> {H}x')],
                Formula('({F}{i} v {G}{i}) -> {H}{i}'),
            ),

        ],
        quantify_all_at_once=True
    )

    # ----------- existential_quantifier_intro --------------
    check_generation(
        'existential_quantifier_intro',
        Formula('{F}{a} -> {G}{a}'),
        [
            Argument(
                [Formula('{F}{a} -> {G}{a}')],
                Formula('(Ex): {F}x -> {G}x'),
            ),
        ]
    )

    check_generation(
        'existential_quantifier_intro',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('({F}{i} v {G}{b}) -> {H}{c}')],
                Formula('(Ex): ({F}x v {G}{b}) -> {H}{c}'),
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{c}')],
                Formula('(Ex): ({F}{a} v {G}x) -> {H}{c}'),
            ),
            Argument(
                [Formula('({F}{a} v {G}{b}) -> {H}{i}')],
                Formula('(Ex): ({F}{a} v {G}{b}) -> {H}x'),
            ),


            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{c}')],
                Formula('(Ex): ({F}x v {G}x) -> {H}{c}'),
            ),
            Argument(
                [Formula('({F}{i} v {G}{b}) -> {H}{i}')],
                Formula('(Ex): ({F}x v {G}{b}) -> {H}x'),
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{i}')],
                Formula('(Ex): ({F}{a} v {G}x) -> {H}x'),
            ),

            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{i}')],
                Formula('(Ex): ({F}x v {G}x) -> {H}x'),
            ),

        ]
    )

    check_generation(
        'existential_quantifier_intro',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{i}')],
                Formula('(Ex): ({F}x v {G}x) -> {H}x'),
            ),
        ],
        quantify_all_at_once=True,
    )


if __name__ == '__main__':
    # test_replacements()
    test_expand_op()
    test_formula_is_identical_to()
    test_argument_is_identical_to()
    test_generate_quantifier_arguments()
