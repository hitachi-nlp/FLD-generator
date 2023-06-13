from typing import Optional, Tuple, Any, Union, List, Dict
from collections import defaultdict
from pprint import pprint

from FLD_generator.formula import (
    Formula,
    IMPLICATION,
    negate,
)
from z3 import (
    DeclareSort,
    BoolSort,

    Function,
    Bool,

    Const,

    Implies,
    And,
    Or,
    Not,
    ForAll,
    Exists,
    Solver,

    sat,
    is_true,
    ModelRef,
)
from FLD_generator.formula_checkers.z3_checkers.intermediates import (
    parse as parse_to_intermediate,
    I_IMPLICATION,
    I_AND,
    I_OR,
    I_NEGATION,
    I_UNIVERSAL,
    I_EXISTS,
)

_interm_to_z3 = {
    I_IMPLICATION: Implies,
    I_AND: And,
    I_OR: Or,
    I_NEGATION: Not,
    I_UNIVERSAL: ForAll,
    I_EXISTS: Exists,
}


_Object = DeclareSort('Object')

_UNARY_PREDICATES_SINGLETON: Dict[str, Function] = {}
_ZEROARY_PREDICATES_SINGLETON: Dict[str, Bool] = {}
_ARGS_SINGLETON: Dict[str, Const] = {}


def _UNARY_PREDICATES(pred: str) -> Function:
    if pred not in _UNARY_PREDICATES_SINGLETON:
        _UNARY_PREDICATES_SINGLETON[pred] = Function(pred, _Object, BoolSort())
    return _UNARY_PREDICATES_SINGLETON[pred]


def _ZEROARY_PREDICATES(pred: str) -> Bool:
    if pred not in _ZEROARY_PREDICATES_SINGLETON:
        _ZEROARY_PREDICATES_SINGLETON[pred] = Bool(pred)
    return _ZEROARY_PREDICATES_SINGLETON[pred]


def _ARGS(arg: str) -> Const:
    if arg not in _ARGS_SINGLETON:
        _ARGS_SINGLETON[arg] = Const(arg, _Object)
    return _ARGS_SINGLETON[arg]


def parse(rep: str):

    def go(interm: Union[str, Tuple]):

        if isinstance(interm, tuple):

            op, left, right = interm

            if isinstance(op, tuple):
                quant, var = op
                z3_op = _interm_to_z3[quant]
                assert right is None

                args = [_ARGS(var), go(left)]

            else:

                z3_op = _interm_to_z3[op]
                assert left is not None

                args = [go(left)]
                if right is not None:
                    args.append(go(right))

            return z3_op(*args)

        else:
            formula = Formula(interm)

            assert len(formula.PASs) == 1
            PAS = formula.PASs[0]

            pred = PAS.predicates[0].rep
            if len(PAS.constants) > 0:
                arg = PAS.constants[0].rep
            elif len(PAS.variables) > 0:
                arg = PAS.variables[0].rep
            else:
                arg = None

            if arg is not None:
                return _UNARY_PREDICATES(pred)(_ARGS(arg))
            else:
                return _ZEROARY_PREDICATES(pred)

    interm = parse_to_intermediate(rep)
    return go(interm)


def check_sat(formulas: List[Formula],
              get_model=False,
              get_parse=False):
    solver = Solver()
    parsed = [parse(formula.rep) for formula in formulas]
    solver.add(*parsed)

    is_sat = solver.check() == sat
    if is_sat:
        model = solver.model()
    else:
        model = None

    ret = [is_sat]
    if get_model:
        ret.append(model)
    if get_parse:
        ret.append(parsed)

    if len(ret) == 1:
        return ret[0]
    else:
        return ret


def is_stronger(this: Formula, that: Formula) -> bool:
    this_imply_that = Formula(f'({this.rep}) {IMPLICATION} ({that.rep})')
    that_imply_this = Formula(f'({that.rep}) {IMPLICATION} ({this.rep})')
    return not check_sat([negate(this_imply_that)]) and check_sat([negate(that_imply_this)])


def is_equiv(this: Formula, that: Formula) -> bool:
    this_imply_that = Formula(f'({this.rep}) {IMPLICATION} ({that.rep})')
    that_imply_this = Formula(f'({that.rep}) {IMPLICATION} ({this.rep})')
    return not check_sat([negate(this_imply_that)]) and not check_sat([negate(that_imply_this)])


def is_weaker(this: Formula, that: Formula) -> bool:
    this_imply_that = Formula(f'({this.rep}) {IMPLICATION} ({that.rep})')
    that_imply_this = Formula(f'({that.rep}) {IMPLICATION} ({this.rep})')
    return check_sat([negate(this_imply_that)]) and not check_sat([negate(that_imply_this)])
