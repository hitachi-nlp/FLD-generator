from typing import List
from .argument import Argument


def is_senseful(arg: Argument) -> bool:
    return not _is_nonsense(arg)


def is_senseful_set(args: List[Argument]) -> bool:
    return all(is_senseful(arg) for arg in args)


def _is_nonsense(arg: Argument) -> bool:
    return _is_conclusion_in_premises(arg)


def _is_conclusion_in_premises(arg: Argument) -> bool:
    if any(arg.conclusion.rep == premise.rep for premise in arg.premises):
        return True
    if any(arg.conclusion.rep == premise_descendant.rep for premise_descendant in arg.premise_descendants
           if premise_descendant is not None):
        return True
    return False
