from typing import List
from FLD.interpretation import (
    _expand_op,
    generate_quantifier_axiom_arguments,
    formula_is_identical_to,
    argument_is_identical_to,
    interpret_formula,
    formula_can_not_be_identical_to,
    generate_quantifier_formulas,
    generate_partially_quantifier_arguments,
    generate_simplified_formulas,
)
from FLD.proof_tree_generators import generate_mappings_from_formula
from FLD.formula import Formula
from FLD.argument import Argument


# TODO: update this test code to be consistent with add_complicated_arguments=True
# def test_interpretation():
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
#     mappings = list(generate_mappings_from_formula([formula],
#                                                    [other_formula],
#                                                    add_complicated_arguments=True))
#     print('-------------------- interpretation --------------------')
#     for mapping in mappings:
#         print('')
#         print('mapping     :', mapping)
#         print('pushed formula :', interpret_formula(formula, mapping))
# 
#     assert(len(formula.predicates) == 3)
#     assert(len(formula.constants) == 2)
# 
#     assert(len(other_formula.predicates) == 4)
#     assert(len(other_formula.constants) == 2)
# 
#     assert(len(mappings) == (2 * 4)**3 * 2**2)  # 2*4 because of the negated patterns


def test_expand_op():
    assert _expand_op(Formula('(x): ({P} v ¬{Q})x -> ({R} v ¬{S})x')).rep == '(x): ({P}x v ¬{Q}x) -> ({R}x v ¬{S}x)'
    assert _expand_op(Formula('({P} v ¬{Q}){a} -> ({R} v ¬{S}){b}')).rep == '({P}{a} v ¬{Q}{a}) -> ({R}{b} v ¬{S}{b})'

    assert _expand_op(Formula('¬((x): ({P} v ¬{Q})x)')).rep == '¬((x): ({P}x v ¬{Q}x))'


def test_formula_can_not_be_identical_to():
    assert not formula_can_not_be_identical_to(
        Formula('{A}'),
        Formula('{B}'),
    )

    assert not formula_can_not_be_identical_to(
        Formula('{A}{a}'),
        Formula('{B}{b}'),
    )

    assert not formula_can_not_be_identical_to(
        Formula('(x): {A}x'),
        Formula('(x): {B}x'),
    )


    assert formula_can_not_be_identical_to(
        Formula('{A}'),
        Formula('{B} {C}'),
    )

    assert formula_can_not_be_identical_to(
        Formula('{A}'),
        Formula('{B}{b}'),
    )

    assert formula_can_not_be_identical_to(
        Formula('(x): {A}x'),
        Formula('(Ex): {A}x'),
    )

    assert formula_can_not_be_identical_to(
        Formula('{A}{a}'),
        Formula('{A}{b} {c}'),
    )


def test_formula_is_identical_to():
    this = Formula('{A}{a} -> {B}{b}')
    that = Formula('{A}{a} -> {A}{a}')

    assert formula_is_identical_to(this, that, allow_many_to_oneg=True)
    assert not formula_is_identical_to(that, this, allow_many_to_oneg=True)

    assert not formula_is_identical_to(this, that, allow_many_to_oneg=False)
    assert not formula_is_identical_to(that, this, allow_many_to_oneg=False)


def test_argument_is_identical_to():

    assert argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{A}'),
            {},
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
            {},
        ),
    )

    assert argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{C}'),
            {},
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
            {},
        ),
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{C}'),
            {},
        ),
        Argument(
            [Formula('¬{Q}'), Formula('{P} v {Q}')],
            Formula('{P}'),
            {},
        ),
        allow_many_to_oneg=False,
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('{A} v {B}'), Formula('¬{B}')],
            Formula('{A}'),
            {},
        ),
        Argument(
            [Formula('{P}'), Formula('{P} -> {Q}')],
            Formula('{Q}'),
            {},
        ),
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('(x): {A}x -> {B}x'), Formula('¬{B}')],
            Formula('{A}'),
            {},
        ),
        Argument(
            [Formula('{P}'), Formula('{P} -> {Q}')],
            Formula('{Q}'),
            {},
        ),

    )

    assert argument_is_identical_to(
        Argument(
            [Formula('{A}{a}')],
            Formula('(x): {A}x'),
            {},
            intermediate_constants=[Formula('{a}')]
        ),
        Argument(
            [Formula('{B}{b}')],
            Formula('(x): {B}x'),
            {},
            intermediate_constants=[Formula('{b}')]
        ),
        allow_many_to_oneg=False,
    )

    assert not argument_is_identical_to(
        Argument(
            [Formula('{A}{a}')],
            Formula('(x): {A}x'),
            {},
            intermediate_constants=[Formula('{a}')]
        ),
        Argument(
            [Formula('{B}{b}')],
            Formula('(x): {C}x'),
            {},
            intermediate_constants=[Formula('{b}')]
        ),
        allow_many_to_oneg=False,
    )


def test_generate_quantifier_axiom_arguments():

    def check_generation(argument_type: str,
                         formula: Formula,
                         expected_arguments: List[Argument],
                         quantify_all_at_once=False):
        generated_arguments = list(
            generate_quantifier_axiom_arguments(argument_type, formula, id_prefix='test', quantify_all_at_once=quantify_all_at_once)
        )
        print()
        print(f'--------- quantifier_axiom_arguments {argument_type} for "{formula.rep}" (quantify_all_at_once={quantify_all_at_once}) ------')

        assert(len(generated_arguments) == len(expected_arguments))
        for generated_argument in generated_arguments:
            print(f'{str(generated_argument)}')
            assert(any(argument_is_identical_to(generated_argument, expected_argument, allow_many_to_oneg=False)
                       for expected_argument in expected_arguments))

    print('\n\n\n================= test_generate_quantifier_axiom_arguments() ====================')

    # ----------- universal_quantifier_elim --------------
    check_generation(
        'universal_quantifier_elim',
        Formula('{F}{a} -> {G}{a}'),
        [
            Argument(
                [Formula('(x): {F}x -> {G}x')],
                Formula('{F}{a} -> {G}{a}'),
                {},
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
                {},
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}x) -> {H}{c}')],
                Formula('({F}{a} v {G}{i}) -> {H}{c}'),
                {},
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}{b}) -> {H}x')],
                Formula('({F}{a} v {G}{b}) -> {H}{i}'),
                {},
            ),


            Argument(
                [Formula('(x): ({F}x v {G}x) -> {H}{c}')],
                Formula('({F}{i} v {G}{i}) -> {H}{c}'),
                {},
            ),
            Argument(
                [Formula('(x): ({F}x v {G}{b}) -> {H}x')],
                Formula('({F}{i} v {G}{b}) -> {H}{i}'),
                {},
            ),
            Argument(
                [Formula('(x): ({F}{a} v {G}x) -> {H}x')],
                Formula('({F}{a} v {G}{i}) -> {H}{i}'),
                {},
            ),

            Argument(
                [Formula('(x): ({F}x v {G}x) -> {H}x')],
                Formula('({F}{i} v {G}{i}) -> {H}{i}'),
                {},
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
                {},
            ),

        ],
        quantify_all_at_once=True
    )

    # ----------- universal_quantifier_intro --------------
    check_generation(
        'universal_quantifier_intro',
        Formula('{F}{a} -> {G}{a}'),
        [
            Argument(
                [Formula('{F}{a} -> {G}{a}')],
                Formula('(x): {F}x -> {G}x'),
                {},
                intermediate_constants=[Formula('{a}')]
            ),
        ]
    )

    check_generation(
        'universal_quantifier_intro',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('({F}{i} v {G}{b}) -> {H}{c}')],
                Formula('(x): ({F}x v {G}{b}) -> {H}{c}'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{c}')],
                Formula('(x): ({F}{a} v {G}x) -> {H}{c}'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),
            Argument(
                [Formula('({F}{a} v {G}{b}) -> {H}{i}')],
                Formula('(x): ({F}{a} v {G}{b}) -> {H}x'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),


            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{c}')],
                Formula('(x): ({F}x v {G}x) -> {H}{c}'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),
            Argument(
                [Formula('({F}{i} v {G}{b}) -> {H}{i}')],
                Formula('(x): ({F}x v {G}{b}) -> {H}x'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{i}')],
                Formula('(x): ({F}{a} v {G}x) -> {H}x'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),

            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{i}')],
                Formula('(x): ({F}x v {G}x) -> {H}x'),
                {},
                intermediate_constants=[Formula('{i}')]
            ),

        ]
    )

    check_generation(
        'universal_quantifier_intro',
        Formula('({F}{a} v {G}{b}) -> {H}{c}'),
        [
            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{i}')],
                Formula('(x): ({F}x v {G}x) -> {H}x'),
                {},
                intermediate_constants=[Formula('{i}')]
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
                {},
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
                {},
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{c}')],
                Formula('(Ex): ({F}{a} v {G}x) -> {H}{c}'),
                {},
            ),
            Argument(
                [Formula('({F}{a} v {G}{b}) -> {H}{i}')],
                Formula('(Ex): ({F}{a} v {G}{b}) -> {H}x'),
                {},
            ),


            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{c}')],
                Formula('(Ex): ({F}x v {G}x) -> {H}{c}'),
                {},
            ),
            Argument(
                [Formula('({F}{i} v {G}{b}) -> {H}{i}')],
                Formula('(Ex): ({F}x v {G}{b}) -> {H}x'),
                {},
            ),
            Argument(
                [Formula('({F}{a} v {G}{i}) -> {H}{i}')],
                Formula('(Ex): ({F}{a} v {G}x) -> {H}x'),
                {},
            ),

            Argument(
                [Formula('({F}{i} v {G}{i}) -> {H}{i}')],
                Formula('(Ex): ({F}x v {G}x) -> {H}x'),
                {},
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
                {},
            ),
        ],
        quantify_all_at_once=True,
    )


def test_generate_quantifier_formulas():

    def check_generation(type_: str,
                         formula: Formula,
                         expected_formulas: List[Formula],
                         quantify_all_at_once=False):

        quantified_formulas = [
            formula
            for formula, _ in generate_quantifier_formulas(formula, type_, quantify_all_at_once=quantify_all_at_once)
        ]

        print()
        print(f'--------- quantifier_axiom_formulas {type_} for "{formula.rep}" (quantify_all_at_once={quantify_all_at_once}) ------')

        assert(len(quantified_formulas) == len(expected_formulas))
        for generated_formula in quantified_formulas:
            print(f'{str(generated_formula)}')
            assert(any(formula_is_identical_to(generated_formula, expected_formula, allow_many_to_oneg=False)
                       for expected_formula in expected_formulas))

    check_generation(
        'universal',
        Formula('{F}{a}'),
        [
            Formula('(x): {F}x'),
        ],
        quantify_all_at_once=False,
    )

    check_generation(
        'universal',
        Formula('({F}{a} v {G}{b})'),
        [
            Formula('(x): ({F}x v {G}{b})'),
            Formula('(x): ({F}{a} v {G}x)'),
            Formula('(x): ({F}x v {G}x)'),
        ],
        quantify_all_at_once=False,
    )

    check_generation(
        'universal',
        Formula('({F}{a} v {G}{b})'),
        [
            Formula('(x): ({F}x v {G}x)'),
        ],
        quantify_all_at_once=True,
    )

    check_generation(
        'universal',
        Formula('{A}'),
        [
        ],
        quantify_all_at_once=False,
    )


def test_generate_quantifier_arguments():

    def check_generation(quantifier_type: str,
                         src_arg: Argument,
                         expected_arguments: List[Argument],
                         quantify_all_at_once=False,
                         quantify_all_at_once_in_a_formula=False):
        generated_arguments = list(
            generate_partially_quantifier_arguments(src_arg, quantifier_type, quantify_all_at_once=quantify_all_at_once, quantify_all_at_once_in_a_formula=quantify_all_at_once_in_a_formula)
        )
        print()
        print(f'--------- quantifier_arguments {quantifier_type} for "{str(src_arg)}" (quantify_all_at_once={quantify_all_at_once}, quantify_all_at_once_in_a_formula={quantify_all_at_once_in_a_formula}) ------')

        for generated_argument, _ in generated_arguments:
            print(f'{str(generated_argument)}')

        assert(len(generated_arguments) == len(expected_arguments))
        for generated_argument, _ in generated_arguments:
            print(f'{str(generated_argument)}')

            assert(any(argument_is_identical_to(generated_argument, expected_argument, allow_many_to_oneg=False)
                       for expected_argument in expected_arguments))

    print('\n\n\n================= test_generate_quantifier_arguments() ====================')

    check_generation(
        'universal',
        Argument(
            [Formula('{A}{a}')],
            Formula('{B}{b}'),
            {},
        ),
        [
            Argument(
                [Formula('(x): {A}x')],
                Formula('{B}{b}'),
                {},
            ),

            Argument(
                [Formula('{A}{a}')],
                Formula('(x): {B}x'),
                {},
            ),

            Argument(
                [Formula('(x): {A}x')],
                Formula('(x): {B}x'),
                {},
            ),

        ],
    )

    check_generation(
        'universal',
        Argument(
            [Formula('({A}{a} v {B}{b})')],
            Formula('{C}{b}'),
            {},
        ),
        [
            Argument(
                [Formula('(x): ({A}x v {B}{b})')],
                Formula('{C}{b}'),
                {},
            ),
        ],
    )

    check_generation(
        'universal',
        Argument(
            [Formula('({A}{a} v {B}{b})')],
            Formula('{C}{c}'),
            {},
        ),
        [
            Argument(
                [Formula('(x): ({A}x v {B}x)')],
                Formula('(x): {C}x'),
                {},
            ),
        ],
        quantify_all_at_once=True,
    )

    check_generation(
        'universal',
        Argument(
            [Formula('({A}{a} v {B}{b})')],
            Formula('{C}{c}'),
            {},
        ),
        [
            Argument(
                [Formula('(x): ({A}x v {B}x)')],
                Formula('{C}{b}'),
                {},
            ),

            Argument(
                [Formula('({A}{a} v {B}{b})')],
                Formula('(x): {C}x'),
                {},
            ),

            Argument(
                [Formula('(x): ({A}x v {B}x)')],
                Formula('(x): {C}x'),
                {},
            ),
        ],
        quantify_all_at_once_in_a_formula=True,
    )

    premise = Formula('{A}{a}')
    quantified_premise = Formula('(x): {A}x')
    check_generation(
        'universal',
        Argument(
            [premise],
            Formula('{B}{b}'),
            {premise: Formula('{C}{c}')},
        ),
        [

            Argument(
                [quantified_premise],
                Formula('{B}{b}'),
                {quantified_premise: Formula('{C}{c}')},
            ),

            Argument(
                [premise],
                Formula('(x): {B}x'),
                {premise: Formula('{C}{c}')},
            ),

            Argument(
                [premise],
                Formula('{B}{b}'),
                {premise: Formula('(x): {C}x')},
            ),

            Argument(
                [quantified_premise],
                Formula('(x): {B}x'),
                {quantified_premise: Formula('{C}{c}')},
            ),

            Argument(
                [quantified_premise],
                Formula('{B}{b}'),
                {quantified_premise: Formula('(x): {C}x')},
            ),

            Argument(
                [premise],
                Formula('(x): {B}x'),
                {premise: Formula('(x): {C}x')},
            ),


            Argument(
                [quantified_premise],
                Formula('(x): {B}x'),
                {quantified_premise: Formula('(x): {C}x')},
            ),
        ],
    )

    premise = Formula('{A}{a}')
    quantified_premise = Formula('(x): {A}x')
    check_generation(
        'universal',
        Argument(
            [premise],
            Formula('{B}{b}'),
            {premise: Formula('{C}{b}')},
        ),
        [
            Argument(
                [quantified_premise],
                Formula('{B}{b}'),
                {quantified_premise: Formula('{C}{b}')},
            ),
        ],
    )

    check_generation(
        'universal',
        Argument(
            [Formula('{A}{a}')],
            Formula('{B}{a}'),
            {},
        ),
        [],
    )
    
    check_generation(
        'universal',
        Argument(
            [Formula('(x): {A}x')],
            Formula('{B}{a}'),
            {},
        ),
        [
            Argument(
                [Formula('(x): {A}x')],
                Formula('(y): {B}y'),
                {},
            ),
        ],
    )

    # # TODO: update argument_is_identical_to so that it can identify "(x): {A}x" and "(y): {B}y"
    # check_generation(
    #     'universal',
    #     Argument(
    #         [Formula('(x): {A}x')],
    #         Formula('{B}{a}'),
    #         {},
    #     ),
    #     [
    #         Argument(
    #             [Formula('(y): {A}y')],
    #             Formula('(y): {B}y'),
    #             {},
    #         ),
    #     ],
    # )


def test_generate_simplified_formulas():

    def check(src_rep: str, gold_reps: List[str]):
        print(f'================ src_rep = {src_rep} ================')
        src_formula = Formula(src_rep)
        generated_reps = [f.rep for f in generate_simplified_formulas(src_formula)]
        for generated_rep in generated_reps:
            print(generated_rep)
        assert all(gold_rep in generated_reps for gold_rep in gold_reps)

    check(
        '¬{A}',
        [
            '{A}',
        ],
    )

    check(
        '(¬{A} & {B}) -> ({C} v ¬{D})',
        [
            '({A} & {B}) -> ({C} v ¬{D})',
            '(¬{A} & {B}) -> ({C} v {D})',
            '¬{A} -> ({C} v ¬{D})',
            '(¬{A} & {B}) -> {C}',
        ],
    )


if __name__ == '__main__':
    # test_expand_op()
    # test_formula_is_identical_to()
    # test_formula_can_not_be_identical_to()
    # test_argument_is_identical_to()

    test_generate_quantifier_axiom_arguments()

    # test_generate_quantifier_formulas()
    # # test_generate_quantifier_arguments()

    # test_generate_simplified_formulas()
