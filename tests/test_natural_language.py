from aacorpus.natural_language import Scheme


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
