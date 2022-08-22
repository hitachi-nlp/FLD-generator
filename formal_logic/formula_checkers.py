import re
from typing import List, Optional, Set
import logging

from .formula import (
    Formula,
    eliminate_double_negation,
    IMPLICATION,
    AND,
    OR,
    NOT,
)

logger = logging.getLogger(__name__)


def is_tautology(formula: Formula) -> bool:
    raise NotImplementedError()


def is_formulas_consistent(formulas: List[Formula]) -> bool:
    """ consistent = satisfiable in formal meaning. """
    return not is_formulas_inconsistent(formulas)


def is_formulas_inconsistent(formulas: List[Formula]) -> bool:
    """ Detect whether a set of formulas is inconsistent, i.e., whether, for any interpretation, they can not be true at the same time.

    See the test code for example usecases.

    Limitations:
        (i) The detection algorithm is specific for our small patterns of formulas. If we extend the pattern, we also have to update the algorithm.
        (ii) The current version can not detect the inconsistency between formulas with implications,
        such as {A -> ¬A, ¬A -> A}. We guess this is not that problematic, since such formulas are rare.
        (iii) We can not handle quantified variables.

    TODO:
        We must update this function if we extend formula patterns.
        It might be better to use external library like tableau generator.
    """
    formulas = [eliminate_double_negation(formula) for formula in formulas]

    # Check whether any of formulas are inconsistent by itself.
    if any((is_single_formula_inconsistent(formula) for formula in formulas)):
        return True

    # Check whether some predicate_argument (like "Ga") appear both as true and as false in formulas.
    formulas_wo_implication = [formula for formula in formulas
                               if formula.premise is None]
    pred_args_wo_variables = {
        pred_arg
        for formula in formulas_wo_implication
        for pred_arg in formula.interprand_predicate_arguments
    }
    for pred_arg in pred_args_wo_variables:
        for i_this, this_formula in enumerate(formulas_wo_implication):
            for that_formula in formulas_wo_implication[i_this + 1:]:
                this_bools = _get_boolean_values(this_formula, pred_arg)
                that_bools = _get_boolean_values(that_formula, pred_arg)
                if ('T' in this_bools and 'F' in that_bools)\
                        or ('F' in this_bools and 'T' in that_bools):
                    if len(this_formula.variables) == 0:
                        # The formulas are composed of constants like: "{G}{a}", "¬{G}{a}"
                        return True
                    else:
                        # The formulas are composed of variables like: "(x): {G}x", "(x): ¬{G}x"
                        assert len(this_formula.variables) == 1
                        assert this_formula.variables[0].rep == that_formula.variables[0].rep
                        variable = this_formula.variables[0]
                        if variable.rep in [v.rep for v in this_formula.universal_variables]\
                                or [v.rep for v in that_formula.universal_variables]:
                            # this and that are like:
                            #     "(x): {G}x",   "(x): ¬{G}x"
                            #     "(Ex): {G}x",  "(x): ¬{G}x"
                            #     "(x): {G}x",   "(Ex): ¬{G}x"
                            # not that "(Ex)" ¬{G}x and "(Ex)" {G}x are consistent.
                            return True

    return False


def is_single_formula_consistent(formula: Formula) -> bool:
    return not is_single_formula_inconsistent(formula)


def is_single_formula_inconsistent(formula: Formula) -> bool:
    """ A formula is inconsistent if for any interpretation it can not be true.
   
    See the test code for example usecases.

    Limitation:
        Currently, we can not determine the inconsistency of formula with implications like A -> (B v C)
    """
    if formula.premise is not None:
        return False
    return any((
        PAS
        for PAS in formula.interprand_predicate_arguments
        if 'T' in _get_boolean_values(formula, PAS) and 'F' in _get_boolean_values(formula, PAS)
    ))


def is_formula_set_senseful(formulas: List[Formula]) -> bool:
    return not is_formula_set_nonsense(formulas)


def is_formula_set_nonsense(formulas: List[Formula]) -> bool:
    if is_formulas_inconsistent(formulas):
        return True
    return any((is_single_formula_nonsense(formula)
                for formula in formulas))


def is_single_formula_senseful(formula: Formula) -> bool:
    return not is_single_formula_nonsense(formula)


def is_single_formula_nonsense(formula: Formula) -> bool:
    """ Detect fomula which is nonsense.

    "Nonsense" means that, in the sense of human commonsense for natural language, the formula is not that useful.
    In addition to the inconsistent formulas, following types of formulas are nonsense:
        {A} -> ¬{A},
        ¬{A} -> {A}

        ({A} & {A})
        (¬{A} & ¬{A})

        ({A} v {A})
        (¬{A} v ¬{A})

        ({A} -> {A})
        (¬{A} -> ¬{A})

    Note that these formulas are still consistent.
    """
    formula = eliminate_double_negation(formula)

    if formula.premise is None and is_formulas_inconsistent([formula]):
        return True

    # detect fromulas like: {A} -> ¬{A}
    if formula.premise is not None:
        premise, conclusion = formula.premise, formula.conclusion
        for pred_arg in conclusion.interprand_predicate_arguments:
            bool_in_conclusion = _get_boolean_values(conclusion, pred_arg)
            bool_in_premise = _get_boolean_values(premise, pred_arg)
            if ('T' in bool_in_conclusion and 'F' in bool_in_premise)\
                    or ('F' in bool_in_conclusion and 'T' in bool_in_premise):
                # this block means "contradiction getween premise and conclusion"
                return True

            if ('T' in bool_in_conclusion and 'T' in bool_in_premise)\
                    or ('F' in bool_in_conclusion and 'F' in bool_in_premise):
                # this block is like "A -> A", "A -> (A & B)"
                return True
    else:
        pass

    # detect fromulas like: ({A} v {A})
    for op in [AND, OR, IMPLICATION]:
        match = re.search(f'[^ ]* {op} [^ ]*', formula.rep)
        if match is not None:
            left, right = match.group().lstrip('(').rstrip(')').split(f' {op} ')
            if left == right:
                return True

    return False


def _get_boolean_values(formula: Formula, predicate_argument: Formula) -> Set[str]:
    """ Detect the boolean value of predicate_arguments which is neccesary for the given formula to be true.

    See the test code for example usecases.
    Note that this function is valid only for our tiny set of formula patterns.

    TODO: We must update this function if we extend formula patterns.
    """
    formula = eliminate_double_negation(formula)

    pred_arg_rep = predicate_argument.rep

    if formula.premise is not None:
        raise ValueError(f'The boolean appearance of formulas can not be determined for formula of type A -> B: input is "{formula.rep}"')
    if pred_arg_rep not in [_pa.rep
                            for _pa in formula.predicate_arguments]:
        return {}

    values = set()

    rep = formula.wo_quantifier.rep
    if rep.find(AND) >= 0:
        if re.match(f'^\({pred_arg_rep} {AND} .*\)$', rep):
            values.add('T')
        elif re.match(f'^\({NOT}{pred_arg_rep} {AND} .*\)$', rep):
            values.add('F')
        if re.match(f'^\(.* {AND} {pred_arg_rep}\)$', rep):
            values.add('T')
        elif re.match(f'^\(.* {AND} {NOT}{pred_arg_rep}\)$', rep):
            values.add('F')

        # AND with is converted to OR by DeMorgan, thus it is undecidable.
        elif re.match(f'^{NOT}\({pred_arg_rep} {AND} .*\)$', rep):
            values.add('Unknown')
        elif re.match(f'^{NOT}\({NOT}{pred_arg_rep} {AND} .*\)$', rep):
            values.add('Unknown')
        if re.match(f'^{NOT}\(.* {AND} {pred_arg_rep}\)$', rep):
            values.add('Unknown')
        elif re.match(f'^{NOT}\(.* {AND} {NOT}{pred_arg_rep}\)$', rep):
            values.add('Unknown')

    elif rep.find(OR) >= 0:
        is_decidable_or = False
        if re.match(f'^\({pred_arg_rep} {OR} {pred_arg_rep}\)$', rep):
            values.add('T')
            is_decidable_or = True
        elif re.match(f'^\({NOT}{pred_arg_rep} {OR} {NOT}{pred_arg_rep}\)$', rep):
            values.add('F')
            is_decidable_or = True

        if re.match(f'^{NOT}\({pred_arg_rep} {OR} .*\)$', rep):
            values.add('F')
            is_decidable_or = True
        elif re.match(f'^{NOT}\({NOT}{pred_arg_rep} {OR} .*\)$', rep):
            values.add('T')
            is_decidable_or = True
        if re.match(f'^{NOT}\(.* {OR} {pred_arg_rep}\)$', rep):
            values.add('F')
            is_decidable_or = True
        elif re.match(f'^{NOT}\(.* {OR} {NOT}{pred_arg_rep}\)$', rep):
            values.add('T')
            is_decidable_or = True

        if not is_decidable_or:
            values.add('Unknown')
    else:
        if re.match(f'^{pred_arg_rep}$', rep):
            values.add('T')
        elif re.match(f'^{NOT}{pred_arg_rep}$', rep):
            values.add('F')

    if len(values) == 0:
        logger.warning('Could not determine the boolean appearance of "%s" in "%s". Please implement logic to handle the pattern.',
                       pred_arg_rep,
                       rep)
        # raise NotImplementedError(f'Please add patterns to handle {rep}')

    return values
