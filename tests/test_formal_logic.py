from formal_logic import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    generate_tree,
    Formula,
    Argument,
)
from formal_logic.scheme import Scheme


def test_scheme():
    mb_scheme_config = {
        "id": "mb0",
        "base_scheme_group": "Modus barbara",
        "scheme_variant": "base_scheme",
        "scheme": [
            [
                "(x): ${F}x -> ${G}x",
                {
                    "F": "A",
                    "G": "B"
                }
            ],
            [
                "${F}${a}",
                {
                    "F": "A",
                    "a": "a"
                }
            ],
            [
                "${G}${a}",
                {
                    "G": "A",
                    "a": "a"
                }
            ]
        ],
        "predicate-placeholders": [
            "F",
            "G",
        ],
        "entity-placeholders": [
            "a",
        ]
    }

    mb_scheme = Scheme.parse_obj(mb_scheme_config)
    assert(mb_scheme.formulas[0].rep == "(x): Fx -> Gx")

    for formula in mb_scheme.formulas:
        print('')
        print(f'-- {str(formula)} --')
        print('premise:', formula.premise)
        print('conclusion:', formula.conclusion)
        print('predicates:', formula.predicates)
        print('constants:', formula.constants)
        print('variables:', formula.variables)


if __name__ == '__main__':
    test_scheme()

def test_replacements():

    formula = Formula('(x): Fx Ga Gb -> Hx')
    other_formula = Formula('(y): Fy Ia Jb -> Ky')

    print('-------------------- placeholders --------------------')
    print('formula                          :', formula)
    print('formula placeholders             :', formula.predicates + formula.constants)

    print('other_formula                    :', other_formula)
    print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)

    replaced_formulas = list(generate_replacement_mappings_from_formula([formula],
                                                                        [other_formula],
                                                                        allow_negation=True))
    # print('-------------------- replacements --------------------')
    # for replacements in replaced_formlas:
    #     print('')
    #     print('replacements     :', replacements)
    #     print('replaced formula :', replace(formula, replacements))

    assert(len(formula.predicates) == 3)
    assert(len(formula.constants) == 2)

    assert(len(other_formula.predicates) == 4)
    assert(len(other_formula.constants) == 2)

    assert(len(replaced_formulas) == (2 * 4)**3 * 2**2)  # 2*4 because of the negated patterns


def test_generation():
    from logger_setup import setup as setup_logger
    setup_logger()
    args = [
        # modus ponens
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('Fa')],
            Formula('Ga'),
        ),
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('(x): Gx -> Hx')],
            Formula('(x): Fx -> Hx'),
        ),

    ]
    for i in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(args, depth=5)
        if proof_tree is not None:
            print(proof_tree.format_str)


if __name__ == '__main__':
    # test_scheme()
    # test_replacements()
    test_generation()
