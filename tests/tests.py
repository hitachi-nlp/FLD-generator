from aacorpus.formal_logic import (
    generate_replacements,
    replace,
    Formula,
    Scheme,
)


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

    for formula in mb_scheme.formulas:
        print('')
        print(f'-- {str(formula)} --')
        print('premise:', formula.premise)
        print('conclusion:', formula.conclusion)
        print('predicates:', formula.predicates)
        print('constants:', formula.constants)
        print('variables:', formula.variables)


def test_replacements():

    formula = Formula('(x): ${F}x ${G}${a} ${G}${b} -> ${H}x')
    other_formula = Formula('(y): ${F}y ${I}${a} ${J}${b} -> ${K}y')

    print('-------------------- placeholders --------------------')
    print('formula                          :', formula)
    print('formula placeholders             :', formula.predicates + formula.constants)

    print('other_formula                    :', other_formula)
    print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)

    print('-------------------- replacements --------------------')
    for replacements in generate_replacements(formula, other_formula):
        print('')
        print('replacements     :', replacements)
        print('replaced formula :', replace(formula, replacements))

    assert(len(formula.predicates) == 3)
    assert(len(formula.constants) == 2)

    assert(len(other_formula.predicates) == 4)
    assert(len(other_formula.constants) == 2)

    assert(len(list(generate_replacements(formula, other_formula))) == 4**3 * 2**2)


if __name__ == '__main__':
    test_scheme()
    test_replacements()
