import re

_an_reg = re.compile(' a ([aeiou])')


def _adjust_indef(rep: str) -> str:
    # a apple => an apple
    return _an_reg.sub(r' an \1', rep)


def _lower(rep: str) -> str:
    return rep[0].lower() + rep[1:]


def normalize(rep: str) -> str:
    return _lower(_adjust_indef(rep.strip(' ')))
