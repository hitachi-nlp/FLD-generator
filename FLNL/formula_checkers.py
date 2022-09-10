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
    CONSTANTS,
)
import kern_profiler

logger = logging.getLogger(__name__)


@profile
def is_consistent(formula: Formula) -> bool:
    return not _is_inconsistent(formula)


@profile
def is_consistent_set(formulas: List[Formula]) -> bool:
    """ consistent = satisfiable in formal meaning. """
    return not _is_inconsistent_set(formulas)


@profile
def is_predicate_arity_consistent(formula: Formula) -> bool:
    return is_predicate_arity_consistent_set([formula])


@profile
def is_predicate_arity_consistent_set(formulas: List[Formula]) -> bool:
    unary_predicates = {pred.rep
                        for formula in formulas
                        for pred in formula.unary_predicates}
    zeroary_predicates = {pred.rep
                          for formula in formulas
                          for pred in formula.zeroary_predicates}
    return len(unary_predicates.intersection(zeroary_predicates)) == 0


@profile
def is_senseful(formula: Formula) -> bool:
    return not _is_nonsense(formula)


@profile
def is_senseful_set(formulas: List[Formula]) -> bool:
    return all(is_senseful(formula) for formula in formulas)


@profile
def is_ok(formula: Formula) -> bool:
    return all([
        is_consistent(formula),
        is_predicate_arity_consistent(formula),
        is_senseful(formula)
    ])


@profile
def is_ok_set(formulas: List[Formula]) -> bool:
    return all([
        is_consistent_set(formulas),
        is_predicate_arity_consistent_set(formulas),
        is_senseful_set(formulas)
    ])


@profile
def _is_inconsistent(formula: Formula) -> bool:
    """ A formula is inconsistent if for any interpretation it can not be true.

    See the test code for example usecases.

    Limitation:
        Currently, we can not determine the inconsistency of formula with implications like A -> (B v C)

    TODO:
        use external consistency checkers to guarantee the correctness of this tool.
    """
    if formula.premise is not None:
        return False
    return any((
        PAS
        for PAS in formula.PASs
        if 'T' in _get_boolean_values(formula, PAS) and 'F' in _get_boolean_values(formula, PAS)
    ))


@profile
def _is_inconsistent_set(formulas: List[Formula]) -> bool:
    """ Detect whether a set of formulas is inconsistent, i.e., whether, for any interpretation, they can not be true at the same time.

    See the test code for example usecases.

    Limitations:
        The current algorithm is stepped as:
            1. We decide the boolean values of PASs in each formula assuming each formula is True.
            2. We conclude formulas are inconsistent if for any pair of formulas, any PAS is True and False.
        As seen, this algorithm does not implement the definition of inconsistency directly (see TODO),
        and thus, produces false negatives, e.g.:
            (i) Regarding 1, we can not decide boolean values of A or B in formula "(A v B)" nor "A -> B" (this is limitation of _get_boolean_values()).
                Thus, we can not detect the inconsistency between formulas like {"A v B", '^A', '^B'} or {"A -> B", "^B", "A"}
            (ii) Regarding 2, we only check pairwise inconsistency. Thus, again, we can not detect the inconsistency between multi-way formulas like {"A v B", '^A', '^B'}.

        Further, since the detection algorithm is specific for our small patterns of formulas, we also have to update the algorithm when we extend the patterns.

        We think, despite these incompletenesses, this function works well in our pipeline.
        This is because, since we randomly choose formulas from large predicates/constants space, it is rare that formulas share the same predicates/constants,
        and thus it is rare that formulas are inconsistent.

    TODO:
        * If we extend formula patterns, we must update this function accordingly.
        * Complete the function. We have mainly two directions:
            (i). Use external library like rableau generator
            (ii). Implement by ourselves. It might be better to use the other algorithm which folllow the definition of the inconsistency directry as:
                (a). We generate all the possible boolean assignments on predicate-argument.
                (b). We decide all the boolean values of formulas and check they are True at the same time.
        * It might be better to use external library like tableau generator for completeness and easiness of implementations.
    """
    formulas = [eliminate_double_negation(formula) for formula in formulas]

    # Check whether any of formulas are inconsistent by itself.
    if any((_is_inconsistent(formula) for formula in formulas)):
        return True

    # Check whether some PAS (like "Ga") appear both as true and as false in formulas.
    formulas_wo_implication = [formula for formula in formulas
                               if formula.premise is None]
    # Here, we only check PAS with constants,
    # since it is possible that variable PASs can be consistent between different formulas
    # even surfacecally
    for i_this, this_formula in enumerate(formulas_wo_implication):
        for that_formula in formulas_wo_implication[i_this + 1:]:
            # A Heuristic to choose the formula with less PASs.
            # Note that formula.PASs is slow so we don't want to call it to exactly judge which formula has less PASs.
            shorter_formula = this_formula if len(this_formula.rep) < len(that_formula.rep) else that_formula
            PASs = shorter_formula.PASs

            for PAS in PASs:
                this_bools = _get_boolean_values(this_formula, PAS)
                that_bools = _get_boolean_values(that_formula, PAS)
                if ('T' in this_bools and 'F' in that_bools)\
                        or ('F' in this_bools and 'T' in that_bools):
                    return True

    return False


@profile
def _is_nonsense(formula: Formula) -> bool:
    """ Detect fomula which is nonsense.

    "Nonsense" means that, in the sense of human commonsense of natural language, the formula is not that useful.
    The nonsense formulas includes the inconsistent formulas plus following types of formulas:
        {A} -> ¬{A},
        ¬{A} -> {A}

        ({A} & {A})
        (¬{A} & ¬{A})

        ({A} v {A})
        (¬{A} v ¬{A})

        ({A} -> {A})
        (¬{A} -> ¬{A})
    """
    formula = eliminate_double_negation(formula)

    if formula.premise is None and _is_inconsistent_set([formula]):
        return True

    # detect fromulas like: {A} -> ¬{A}
    if formula.premise is not None:
        premise, conclusion = formula.premise, formula.conclusion
        for PAS in conclusion.PASs:
            bool_in_conclusion = _get_boolean_values(conclusion, PAS)
            bool_in_premise = _get_boolean_values(premise, PAS)
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


@profile
def _get_boolean_values(formula: Formula, PAS: Formula) -> Set[str]:
    """ Detect the boolean values of PASs which is neccesary for the given formula to be true.

    See the test code for example usecases.

    Note that this function is valid only for our tiny set of formula patterns.

    TODO:
        * When we extend formula patterns, we must update this function
        * It might be more robust to use external solvers like tableau generators.
    """
    if len(PAS.predicates) != 1:
        raise ValueError(f'PAS must have exactly one predicate. actual: {PAS}')

    formula = eliminate_double_negation(formula)

    if formula.premise is not None:
        raise ValueError(f'The boolean appearance of formulas can not be determined for formula of type A -> B: input is "{formula.rep}"')

    # e.g.) formula: "(x): ^{A}x"    PAS: "{A}{a}"
    if len(formula.universal_variables) == 1:
        variable = formula.universal_variables[0]
        for constant in CONSTANTS:
            bound_formula = Formula(formula.wo_quantifier.rep.replace(variable.rep, constant))
            bound_PAS = Formula(PAS.rep.replace(variable.rep, constant))
            booleans_on_bound_formula = _get_boolean_values(bound_formula, bound_PAS)
            if len(booleans_on_bound_formula) >= 1:
                return booleans_on_bound_formula
        return {}

    # e.g.) formula: "(Ex): {B}x -> {A}x"     PAS: "{A}x"
    if len(formula.existential_variables) == 1 and PAS.variables[0].rep in [v.rep for v in formula.existential_variables]:
        # We can not determine
        # since we regard "x" without quantification denotes all the constants.
        return {}

    if PAS.rep not in [_pa.rep for _pa in formula.PASs]:  # SLOW, called many times
        return set()

    values = set()
    PAS_rep = PAS.rep
    rep = formula.wo_quantifier.rep
    if rep.find(AND) >= 0:
        if re.match(f'^\({PAS_rep} {AND} .*\)$', rep):
            values.add('T')
        elif re.match(f'^\({NOT}{PAS_rep} {AND} .*\)$', rep):
            values.add('F')
        if re.match(f'^\(.* {AND} {PAS_rep}\)$', rep):
            values.add('T')
        elif re.match(f'^\(.* {AND} {NOT}{PAS_rep}\)$', rep):
            values.add('F')

        # AND with is converted to OR by DeMorgan, thus it is undecidable.
        elif re.match(f'^{NOT}\({PAS_rep} {AND} .*\)$', rep):
            values.add('Unknown')
        elif re.match(f'^{NOT}\({NOT}{PAS_rep} {AND} .*\)$', rep):
            values.add('Unknown')
        if re.match(f'^{NOT}\(.* {AND} {PAS_rep}\)$', rep):
            values.add('Unknown')
        elif re.match(f'^{NOT}\(.* {AND} {NOT}{PAS_rep}\)$', rep):
            values.add('Unknown')

    elif rep.find(OR) >= 0:
        is_decidable_or = False
        if re.match(f'^\({PAS_rep} {OR} {PAS_rep}\)$', rep):
            values.add('T')
            is_decidable_or = True
        elif re.match(f'^\({NOT}{PAS_rep} {OR} {NOT}{PAS_rep}\)$', rep):
            values.add('F')
            is_decidable_or = True

        if re.match(f'^{NOT}\({PAS_rep} {OR} .*\)$', rep):
            values.add('F')
            is_decidable_or = True
        elif re.match(f'^{NOT}\({NOT}{PAS_rep} {OR} .*\)$', rep):
            values.add('T')
            is_decidable_or = True
        if re.match(f'^{NOT}\(.* {OR} {PAS_rep}\)$', rep):
            values.add('F')
            is_decidable_or = True
        elif re.match(f'^{NOT}\(.* {OR} {NOT}{PAS_rep}\)$', rep):
            values.add('T')
            is_decidable_or = True

        if not is_decidable_or:
            values.add('Unknown')
    else:
        if re.match(f'^{PAS_rep}$', rep):
            values.add('T')
        elif re.match(f'^{NOT}{PAS_rep}$', rep):
            values.add('F')

    if len(values) == 0:
        logger.warning('Could not determine the boolean appearance of "%s" in "%s". Please implement logic to handle the pattern.',
                       PAS_rep,
                       rep)
        # raise NotImplementedError(f'Please add patterns to handle {rep}')

    return values