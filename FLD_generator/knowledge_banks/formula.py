import re
from typing import Tuple, Optional
from enum import Enum

from FLD_generator.formula import Formula, NEGATION, IMPLICATION


class FormulaType(Enum):
    F = 'F'
    nF = 'nF'

    Fa = 'Fa'
    nFa = 'nFa'

    Fx = 'Fx'
    nFx = 'nFx'

    F_G = 'F_G'
    nF_G = 'nF_G'
    F_nG = 'F_nG'
    nF_nG = 'nF_nG'

    Fa_Ga = 'Fa_Ga'
    nFa_Ga = 'nFa_Ga'
    Fa_nGa = 'Fa_nGa'
    nFa_nGa = 'nFa_nGa'

    Fa_Gb = 'Fa_Gb'
    nFa_Gb = 'nFa_Gb'
    Fa_nGb = 'Fa_nGb'
    nFa_nGb = 'nFa_nGb'

    Fx_Gb = 'Fx_Gb'
    nFx_Gb = 'nFx_Gb'
    Fx_nGb = 'Fx_nGb'
    nFx_nGb = 'nFx_nGb'

    Fx_Gx = 'Fx_Gx'
    nFx_Gx = 'nFx_Gx'
    Fx_nGx = 'Fx_nGx'
    nFx_nGx = 'nFx_nGx'

    # "Gy" does not exist in formulas, only in statements.
    # Fx_Gy = 'Fx_Gy'
    # nFx_Gy = 'nFx_Gy'
    # Fx_nGy = 'Fx_nGy'
    # nFx_nGy = 'nFx_nGy'

    OTHERS = 'OTHERS'


def get_type_fml(formula: Formula, allow_others=False) -> FormulaType:
    if _is_F_fml(formula, nF=False):
        return FormulaType.F
    elif _is_F_fml(formula, nF=True):
        return FormulaType.nF


    elif _is_Fa_fml(formula, nF=False):
        return FormulaType.Fa
    elif _is_Fa_fml(formula, nF=True):
        return FormulaType.nFa


    elif _is_Fx_fml(formula, nF=False):
        return FormulaType.Fx
    elif _is_Fx_fml(formula, nF=True):
        return FormulaType.nFx


    elif _is_F_G_fml(formula, nF=False, nG=False):
        return FormulaType.F_G
    elif _is_F_G_fml(formula, nF=True, nG=False):
        return FormulaType.nF_G
    elif _is_F_G_fml(formula, nF=False, nG=True):
        return FormulaType.F_nG
    elif _is_F_G_fml(formula, nF=True, nG=True):
        return FormulaType.nF_nG


    elif _is_Fa_Ga_fml(formula, nF=False, nG=False):
        return FormulaType.Fa_Ga
    elif _is_Fa_Ga_fml(formula, nF=True, nG=False):
        return FormulaType.nFa_Ga
    elif _is_Fa_Ga_fml(formula, nF=False, nG=True):
        return FormulaType.Fa_nGa
    elif _is_Fa_Ga_fml(formula, nF=True, nG=True):
        return FormulaType.nFa_nGa


    elif _is_Fa_Gb_fml(formula, nF=False, nG=False):
        return FormulaType.Fa_Gb
    elif _is_Fa_Gb_fml(formula, nF=True, nG=False):
        return FormulaType.nFa_Gb
    elif _is_Fa_Gb_fml(formula, nF=False, nG=True):
        return FormulaType.Fa_nGb
    elif _is_Fa_Gb_fml(formula, nF=True, nG=True):
        return FormulaType.nFa_nGb


    elif _is_Fx_Gx_fml(formula, nF=False, nG=False):
        return FormulaType.Fx_Gx
    elif _is_Fx_Gx_fml(formula, nF=True, nG=False):
        return FormulaType.nFx_Gx
    elif _is_Fx_Gx_fml(formula, nF=False, nG=True):
        return FormulaType.Fx_nGx
    elif _is_Fx_Gx_fml(formula, nF=True, nG=True):
        return FormulaType.nFx_nGx


    # elif _is_Fx_Gy_fml(formula, nF=False, nG=False):
    #     return FormulaType.Fx_Gy
    # elif _is_Fx_Gy_fml(formula, nF=True, nG=False):
    #     return FormulaType.nFx_Gy
    # elif _is_Fx_Gy_fml(formula, nF=False, nG=True):
    #     return FormulaType.Fx_nGy
    # elif _is_Fx_Gy_fml(formula, nF=True, nG=True):
    #     return FormulaType.nFx_nGy


    else:
        if allow_others:
            return FormulaType.OTHERS
        else:
            raise ValueError(formula)


def _is_F_fml(formula: Formula, nF=False) -> bool:
    regex = '^\(*' + _PAS_rgx(neg=nF, no_const=True) + '\)*$'

    if nF:
        special_regex = f'^\(*{NEGATION}\(' + _PAS_rgx(neg=False, no_const=True) + '\)\)*$'
        if re.match(special_regex, formula.rep) is not None:
            return True

    return re.match(regex, formula.rep) is not None


def _is_Fa_fml(formula: Formula, nF=False) -> bool:
    regex = '^\(*' + _PAS_rgx(neg=nF) + '\)*$'

    if nF:
        special_regex = f'^\(*{NEGATION}\(' + _PAS_rgx(neg=False) + '\)\)*$'
        if re.match(special_regex, formula.rep) is not None:
            return True

    return re.match(regex, formula.rep) is not None


def _is_Fx_fml(formula: Formula, nF=False) -> bool:
    regex = '^\(*\(x\): ' + _PAS_rgx(neg=nF, x=True) + '\)*$'
    return re.match(regex, formula.rep) is not None


def _is_F_G_fml(formula: Formula, nF=False, nG=False) -> bool:
    regex = '^\(*' + _PAS_rgx(neg=nF, no_const=True) + f' {IMPLICATION} ' + _PAS_rgx(neg=nG, no_const=True) + '\)*$'
    if not re.match(regex, formula.rep):
        return False
    return True


def _is_Fa_Ga_fml(formula: Formula, nF=False, nG=False) -> bool:
    regex = '^\(*' + _PAS_rgx(neg=nF) + f' {IMPLICATION} ' + _PAS_rgx(neg=nG) + '\)*$'
    if not re.match(regex, formula.rep):
        return False
    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 1 and len(preds) == 2


def _is_Fa_Gb_fml(formula: Formula, nF=False, nG=False) -> bool:
    regex = '^\(*' + _PAS_rgx(neg=nF) + f' {IMPLICATION} ' + _PAS_rgx(neg=nG) + '\)*$'
    if not re.match(regex, formula.rep):
        return False
    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 2 and len(preds) == 2


def _is_Fx_Gx_fml(formula: Formula, nF=False, nG=False) -> bool:
    regex = '^\(*\(x\): ' + _PAS_rgx(neg=nF, x=True) + f' {IMPLICATION} ' + _PAS_rgx(neg=nG, x=True) + '\)*$'
    if not re.match(regex, formula.rep):
        return False
    return True


# def _is_Fx_Gy_fml(formula: Formula, nF=False, nG=False) -> bool:
#     regex = '^\(*\(x\): ' + _PAS_rgx(neg=nF, x=True) + f' {IMPLICATION} ' + _PAS_rgx(neg=nG, y=True) + '\)*$'
#     if not re.match(regex, formula.rep):
#         return False
#     return True



def _PAS_rgx(neg=False, x=False, y=False, no_const=False) -> str:
    if no_const:
        regex = '{[^}]*}'
    else:
        if x:
            regex = '{[^}]*}x'
        elif y:
            regex = '{[^}]*}y'
        else:
            regex = '{[^}]*}{[^}]*}'
    if neg:
        regex = NEGATION + regex
    return regex


def get_declare_constants_fml(formula: Formula) -> Optional[Formula]:
    consts = formula.constants
    if len(consts) == 0:
        return None
    elif len(consts) == 1:
        return consts[0]
    else:
        raise ValueError()


def get_declare_predicates_fml(formula: Formula) -> Formula:
    preds = formula.unary_predicates or formula.zeroary_predicates
    if len(preds) == 0:
        raise ValueError()
    elif len(preds) == 1:
        return preds[0]
    else:
        raise ValueError()


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
