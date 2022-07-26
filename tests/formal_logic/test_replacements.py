from formal_logic.generation import generate_replacement_mappings_from_formula
from formal_logic.formula import Formula


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


if __name__ == '__main__':
    test_replacements()
