from typing import List
from FLD_generator.argument import Argument
from FLD_generator.formula_checkers import is_trivial as is_formula_trivial
from FLD_generator.formula_checkers import is_nonsense as is_formula_nonsense
from FLD_generator.formula import is_contradiction_symbol


def is_trivial(arg: Argument) -> bool:
    if any(is_formula_trivial(formula)
           for formula in arg.all_formulas
           if not is_contradiction_symbol(formula)):
        return True
    return _is_conclusion_in_premises(arg)


def is_nonsense(arg: Argument, allow_detect_tautology_contradiction=False) -> bool:
    return any(is_formula_nonsense(formula, allow_detect_tautology_contradiction=allow_detect_tautology_contradiction)
               for formula in arg.all_formulas
               if not is_contradiction_symbol(formula))


def _is_conclusion_in_premises(arg: Argument) -> bool:
    if any(arg.conclusion.rep == premise.rep for premise in arg.premises):
        return True
    return False
