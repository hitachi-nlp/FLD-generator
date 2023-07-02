from typing import Optional, Tuple, Any, Union, List, Dict
from collections import defaultdict
from pprint import pprint
import logging
from ctypes import ArgumentError
from z3.z3types import Z3Exception

from FLD_generator.formula import (
    Formula,
    IMPLICATION,
    CONTRADICTION,
    negate,
    is_contradiction_symbol,
    has_contradiction_symbol,
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
from .intermediates import (
    parse as parse_to_intermediate,
    I_IMPLICATION,
    I_AND,
    I_OR,
    I_NEGATION,
    I_UNIVERSAL,
    I_EXISTS,
)
import line_profiling

_interm_to = {
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

logger = logging.getLogger(__name__)


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


def _raise_with_contradiction(formula: Formula) -> None:
    if has_contradiction_symbol(formula):
        raise Exception(f'The formula with the contradiction symbol ("{CONTRADICTION}") is not supported: "{formula.rep}"')


def parse(rep: str):
    _raise_with_contradiction(Formula(rep))

    def go(interm: Union[str, Tuple]):

        if isinstance(interm, tuple):

            op, left, right = interm

            if isinstance(op, tuple):
                quant, var = op
                z3_op = _interm_to[quant]
                assert right is None

                args = [_ARGS(var), go(left)]

            else:

                z3_op = _interm_to[op]
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
                exception = None
                try:
                    return _UNARY_PREDICATES(pred)(_ARGS(arg))
                # except ArgumentError as e:
                #     exception = e
                #     logger.fatal('[checkers.py] ArgumentError occurred. We will continue the trials, however, we do not know the root cause of this.')
                except Z3Exception as e:
                    exception = e
                    logger.fatal('[checkers.py] Z3Exception occurred. We will continue the trials, however, we do not know the root cause of this.')
                logger.info('pred                          : ' + str(pred))
                logger.info('arg                           : ' + str(arg))
                logger.info('_UNARY_PREDICATES(pred)       : ' + str(_UNARY_PREDICATES(pred)))
                logger.info('type(_UNARY_PREDICATES(pred)) : ' + str(type(_UNARY_PREDICATES(pred))))
                logger.info('_ARGS(arg)                    : ' + str(_ARGS(arg)))
                logger.info('type(_ARGS(arg))              : ' + str(type(_ARGS(arg))))
                raise exception

            else:
                return _ZEROARY_PREDICATES(pred)

    interm = parse_to_intermediate(rep)
    return go(interm)


_CHECK_SAT_CACHE = {}
_CACHE_SIZE = 1000000

@profile
def check_sat(formulas: List[Formula],
              get_model=False,
              get_parse=False):
    for formula in formulas:
        _raise_with_contradiction(formula)

    global _CHECK_SAT_CACHE

    cache_key = tuple(sorted(formula.rep for formula in formulas))
    # model and parse is object, thus we do not cache them.
    if not get_model and not get_parse and cache_key in _CHECK_SAT_CACHE:
        return _CHECK_SAT_CACHE[cache_key]

    solver = Solver()
    parsed = [parse(formula.rep) for formula in formulas]

    solver.add(*parsed)

    is_sat = solver.check() == sat
    if is_sat:
        model = solver.model()
    else:
        model = None

    _CHECK_SAT_CACHE[cache_key] = is_sat
    if len(_CHECK_SAT_CACHE) >= _CACHE_SIZE:   # reset
        _CHECK_SAT_CACHE = {}

    if get_model or get_parse:
        ret = [is_sat]
        if get_model:
            ret.append(model)
        if get_parse:
            ret.append(parsed)
        return ret
    else:
        return is_sat


@profile
def is_tautology(formula: ForAll) -> bool:
    if is_contradiction_symbol(formula):
        return False
    return not check_sat([negate(formula)])


@profile
def is_contradiction(formula: ForAll) -> bool:
    if is_contradiction_symbol(formula):
        return True
    return is_tautology(negate(formula))


@profile
def is_provable(facts: List[Formula], hypothesis: Formula) -> bool:
    if is_contradiction_symbol(hypothesis):
        return not check_sat(facts)
    return not check_sat(facts + [negate(hypothesis)])


@profile
def is_disprovable(facts: List[Formula], hypothesis: Formula) -> bool:
    if is_contradiction_symbol(hypothesis):
        raise ValueError(f'we do not have a concept of "disproving the contradiction {hypothesis.rep}", i.e., proving the negated contradiction'
                         'because we do not have a concept of "negated contradiction"')
    return not check_sat(facts + [hypothesis])


@profile
def is_unknown(facts: List[Formula], hypothesis: Formula) -> bool:
    if is_contradiction_symbol(hypothesis):
        # here, "unknown" means "we can not prove contradiction"
        return not is_provable(facts, hypothesis)
    return not is_provable(facts, hypothesis) and not is_disprovable(facts, hypothesis)


@profile
def is_stronger(this: Formula, that: Formula) -> bool:
    return _imply(this, that, ignore_tautology=True) and not _imply(that, this, ignore_tautology=True)


@profile
def is_equiv(this: Formula, that: Formula) -> bool:
    return _imply(this, that, ignore_tautology=True) and _imply(that, this, ignore_tautology=True)


@profile
def is_weaker(this: Formula, that: Formula) -> bool:
    return not _imply(this, that, ignore_tautology=True) and _imply(that, this, ignore_tautology=True)


@profile
def _imply(this: Formula, that: Formula, ignore_tautology=False) -> bool:
    if ignore_tautology:
        if not check_sat([this]):
            # if this === 0 (i.e., this is always false) then this_imply_that === 1. But we do not regart it as "stronger"
            return False
        if not check_sat([negate(that)]):
            # if that === 1 (i.e., that is always true) then this_imply_that === 1. But we do not regart it as "stronger", too.
            return False

    this_imply_that = Formula(f'({this.rep}) {IMPLICATION} ({that.rep})')
    return not check_sat([negate(this_imply_that)])


@profile
def is_trivial(formula: Formula) -> bool:
    if is_contradiction_symbol(formula):
        return True
    return is_tautology(formula) or is_contradiction(formula)
