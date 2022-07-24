from typing import List
from aacorpus.formal_logic import (
    generate_replaced_formulas,
    generate_replacement_mappings,
    Formula,
)


def test_replacements():

    formula = Formula('(x): Fx Ga Gb -> Hx')
    other_formula = Formula('(y): Fy Ia Jb -> Ky')

    print('-------------------- placeholders --------------------')
    print('formula                          :', formula)
    print('formula placeholders             :', formula.predicates + formula.constants)

    print('other_formula                    :', other_formula)
    print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)

    replaced_formulas = list(generate_replacement_mappings(formula, other_formula, allow_negation=True))
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

    def __str__(self) -> str:
        return f'Argument(premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)


def test_argument():
    modus_ponens_arg = Argument(
        [Formula('(x): Fx -> ¬Gx'), Formula('Fa')],
        Formula('¬Ga'),
    )

    possible_args = [modus_ponens_arg]

    target_arg = modus_ponens_arg

    chainable_args = []
    for possible_arg in possible_args:
        is_chainable = False
        for premise in possible_arg.premises:
            for premise_variant in generate_replaced_formulas(premise, target_arg.conclusion):
                print(premise_variant, target_arg.conclusion)
                if premise_variant.rep == target_arg.conclusion:
                    is_chainable = True
                    break
            if is_chainable:
                break
        if is_chainable:
            chainable_args.append(possible_arg)
    print(chainable_args)


if __name__ == '__main__':
    test_replacements()
    test_argument()
