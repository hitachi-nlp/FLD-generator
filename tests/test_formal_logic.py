from typing import List
from aacorpus.formal_logic import (
    generate_replacements,
    replace,
    Formula,
)


def test_replacements():

    formula = Formula('(x): ${F}x ${G}${a} ${G}${b} -> ${H}x')
    other_formula = Formula('(y): ${F}y ${I}${a} ${J}${b} -> ${K}y')

    print('-------------------- placeholders --------------------')
    print('formula                          :', formula)
    print('formula placeholders             :', formula.predicates + formula.constants)

    print('other_formula                    :', other_formula)
    print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)

    replaced_formulas = list(generate_replacements(formula, other_formula, allow_negation=True))
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


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula):
        self.premises = premises
        self.conclusion = conclusion


def test_argument():
    modus_ponens_arg = Argument(
        [Formula('(x): ${F}x -> ${G}x'), Formula('${F}${a}')],
        Formula('${G}${a}'),
    )


if __name__ == '__main__':
    test_replacements()
