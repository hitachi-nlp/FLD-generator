from aacorpus.formal_logic import (
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    generate_tree,
    Formula,
    Argument,
)


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
    for i in range(5):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(args, depth=3)
        print(proof_tree.format_str)


if __name__ == '__main__':
    # test_replacements()
    test_generation()
