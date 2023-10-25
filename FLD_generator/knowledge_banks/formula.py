import re
from typing import Tuple, Optional
from enum import Enum

from FLD_generator.formula import Formula


class FormulaType(Enum):
    F = 'F'
    Fa = 'Fa'

    F_G = 'F_G'
    Fa_Ga = 'Fa_Ga'
    Fa_Gb = 'Fa_Gb'
    Fx_Gx = 'Fx_Gx'

    OTHERS = 'OTHERS'


def get_type_fml(formula: Formula) -> FormulaType:
    if _is_F_fml(formula):
        return FormulaType.F
    elif _is_Fa_fml(formula):
        return FormulaType.Fa
    elif _is_F_G_fml(formula):
        return FormulaType.F_G
    elif _is_Fa_Ga_fml(formula):
        return FormulaType.Fa_Ga
    elif _is_Fa_Gb_fml(formula):
        return FormulaType.Fa_Gb
    elif _is_Fx_Gx_fml(formula):
        return FormulaType.Fx_Gx
    else:
        return FormulaType.OTHERS


def _is_F_fml(formula: Formula) -> bool:
    """ {F} """
    return re.match('^{[^}]*}$', formula.rep) is not None


def _is_Fa_fml(formula: Formula) -> bool:
    """ {F}{a} """
    return re.match('^{[^}]*}{[^}]*}$', formula.rep) is not None


def _is_F_G_fml(formula: Formula) -> bool:
    """ {F} -> {G} """

    return re.match(r'^{[^}]*} -> {[^}]*}$', formula.rep) is not None

def _is_Fa_Ga_fml(formula: Formula) -> bool:
    """ {F}{a} -> {G}{a} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 1 and len(preds) == 2


def _is_Fa_Gb_fml(formula: Formula) -> bool:
    """ {F}{a} -> {G}{b} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 2 and len(preds) == 2


def _is_Fx_Gx_fml(formula: Formula) -> bool:
    """ (x): {F}x -> {G}x """

    if not re.match(r'^\(x\): {[^}]*}x -> {[^}]*}x$', formula.rep):
        return False

    preds = formula.predicates
    return len(preds) == 2


def get_if_then_constants_fml(formula: Formula) -> Tuple[Optional[Formula], Optional[Formula]]:
    consts = formula.constants

    if len(consts) == 0:
        return None, None

    elif len(consts) == 1:
        return consts[0], consts[0]

    elif len(consts) == 2:
        const_first = (
            consts[0]
            if formula.rep.find(consts[0].rep) < formula.rep.find(consts[1].rep)
            else consts[1]
        )
        const_second = consts[0] if const_first == consts[1] else consts[1]

        return const_first, const_second

    else:
        raise ValueError()


def get_if_then_predicates_fml(formula: Formula) -> Tuple[Formula, Formula]:
    preds = formula.unary_predicates or formula.zeroary_predicates

    if len(preds) == 0:
        return None, None

    elif len(preds) == 1:
        return preds[0], preds[0]

    elif len(preds) == 2:
        pred_first = (
            preds[0]
            if formula.rep.find(preds[0].rep) < formula.rep.find(preds[1].rep)
            else preds[1]
        )
        pred_second = preds[0] if pred_first == preds[1] else preds[1]

        return pred_first, pred_second

    else:
        raise ValueError()
