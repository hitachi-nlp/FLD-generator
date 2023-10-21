import re
from typing import Tuple

from FLD_generator.formula import Formula


def is_simple_unary_implication_shared_const(formula: Formula) -> bool:
    """ {A}{a} -> {B}{a} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 1 and len(preds) == 2


def is_simple_unary_implication_unshared_const(formula: Formula) -> bool:
    """ {A}{a} -> {B}{b} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 2 and len(preds) == 2


def is_simple_universal_implication(formula: Formula) -> bool:
    """ (x): {A}x -> {B}x """

    if not re.match(r'^\(x\): {[^}]*}x -> {[^}]*}x$', formula.rep):
        return False

    preds = formula.predicates
    return len(preds) == 2


def get_if_then_constants(formula: Formula) -> Tuple[Formula, Formula]:
    consts = formula.constants

    if len(consts) == 1:
        return consts[0], consts[0]

    elif len(consts) == 2:
        const_if = (
            consts[0]
            if formula.rep.find(consts[0].rep) < formula.rep.find(consts[1].rep)
            else consts[1]
        )
        const_then = consts[0] if const_if == consts[1] else consts[1]

        return const_if, const_then

    else:
        raise ValueError()


def get_if_then_predicates(formula: Formula) -> Tuple[Formula, Formula]:
    preds = formula.unary_predicates

    if len(preds) == 1:
        return preds[0], preds[0]

    elif len(preds) == 2:
        pred_if = (
            preds[0]
            if formula.rep.find(preds[0].rep) < formula.rep.find(preds[1].rep)
            else preds[1]
        )
        pred_then = preds[0] if pred_if == preds[1] else preds[1]

        return pred_if, pred_then

    else:
        raise ValueError()
