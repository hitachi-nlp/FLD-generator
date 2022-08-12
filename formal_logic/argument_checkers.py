from .argument import Argument


def is_argument_nonsense(arg: Argument) -> bool:
    return _is_conclusion_in_premises(arg)


def _is_conclusion_in_premises(arg: Argument) -> bool:
    return any([arg.conclusion.rep == premise.rep
                for premise in arg.premises])
