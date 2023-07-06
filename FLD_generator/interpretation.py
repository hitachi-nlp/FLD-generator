import re
import random
from typing import Dict, List, Any, Iterable, Tuple, Optional, Union, Set
import copy
from itertools import permutations
from functools import lru_cache
from re import Match

from .formula import (
    Formula,
    NEGATION,
    DISJUNCTION,
    CONJUNCTION,
    IMPLICATION,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
    eliminate_double_negation,
    negate,
    strip_quantifier,
)
from .argument import Argument
import line_profiling

_QUANTIFICATION_DEGREES = [
    'one_constant',
    'all_constants_in_implication_premise_conclusion',
    'all_constants',
]


def _fill_str(no: int) -> str:
    return str(no).zfill(6)


def generate_complicated_arguments(src_arg: Argument,
                                   elim_dneg=False,
                                   suppress_op_expansion_if_exists=False,
                                   get_name=False) -> Union[Iterable[Tuple[Argument, Dict[str, str]]], Iterable[Tuple[Argument, Dict[str, str], str]]]:
    for mapping, name in generate_complication_mappings_from_formula(src_arg.all_formulas,
                                                                     suppress_op_expansion_if_exists=suppress_op_expansion_if_exists,
                                                                     get_name=True):
        complicated_argument = interpret_argument(src_arg, mapping, elim_dneg=elim_dneg)
        if get_name:
            yield complicated_argument, mapping, name
        else:
            yield complicated_argument, mapping


def generate_complicated_formulas(src_formula: Formula,
                                  elim_dneg=False,
                                  suppress_op_expansion_if_exists=False,
                                  get_name=False) -> Union[Iterable[Tuple[Formula, Dict[str, str]]], Iterable[Tuple[Formula, Dict[str, str], str]]]:
    done_reps: Dict[str, str] = {}
    for mapping, name in generate_complication_mappings_from_formula([src_formula],
                                                                     suppress_op_expansion_if_exists=suppress_op_expansion_if_exists,
                                                                     get_name=True):
        complicated_formula = interpret_formula(src_formula, mapping, elim_dneg=elim_dneg)
        done_reps[complicated_formula.rep] = name
        if get_name:
            yield complicated_formula, mapping, name
        else:
            yield complicated_formula, mapping


def generate_simplified_formulas(src_formula: Formula,
                                 elim_dneg=False,
                                 get_name=False) -> Union[Iterable[Formula], Iterable[Tuple[Formula, str]]]:
    # We will exclude negation, conjunction and disjunction from the src_formula.
    # For simplicity, we change one element at once

    rep = src_formula.rep

    for i_negation_match, negation_match in enumerate(re.finditer(NEGATION, rep)):
        rep_wo_negation = rep[:negation_match.start()] + rep[negation_match.end():]

        simplified_formula = Formula(rep_wo_negation)

        if elim_dneg:
            simplified_formula = eliminate_double_negation(simplified_formula)

        if get_name:
            yield simplified_formula, f'simplification.not-{_fill_str(i_negation_match)}'
        else:
            yield simplified_formula

    for op in [CONJUNCTION, DISJUNCTION]:
        op_regexp = f'\(([^\)]*) {op} ([^\)]*)\)'
        for i_match, match in enumerate(re.finditer(op_regexp, rep)):
            span_text = rep[match.start():match.end()]

            for i_target, target in enumerate(['\g<1>', '\g<2>']):
                span_text_replaced = re.sub(op_regexp, target, span_text)

                rep_wo_op = rep[:match.start()] + span_text_replaced + rep[match.end():]

                simplified_formula = Formula(rep_wo_op)

                if elim_dneg:
                    simplified_formula = eliminate_double_negation(simplified_formula)

                if get_name:
                    yield simplified_formula, f'simplification.{op}-{_fill_str(i_match)}.target_term-{_fill_str(i_target)}'
                else:
                    yield simplified_formula


def generate_complication_mappings_from_formula(formulas: List[Formula],
                                                suppress_op_expansion_if_exists=False,
                                                get_name=False) -> Union[Iterable[Dict[str, str]], Iterable[Tuple[Dict[str, str], str]]]:
    predicates = sorted(set([p.rep for formula in formulas for p in formula.predicates]))
    constants = sorted(set([p.rep for formula in formulas for p in formula.constants]))

    identity_mapping = {pred: pred for pred in predicates}
    identity_mapping.update({const: const for const in constants})

    unused_predicates = list(set(PREDICATES) - set(predicates))
    unk_pred0 = sorted(unused_predicates)[0]
    unk_pred1 = sorted(unused_predicates)[1]

    def not_enhance(predicates: List[str]) -> Iterable[List[str]]:
        if len(predicates) == 1:
            predicate = predicates[0]
            for prefix in ['', f'{NEGATION}']:
                yield [f'{prefix}{predicate}']
        else:
            predicate = predicates[0]
            for prefix in ['', f'{NEGATION}']:
                for tail in not_enhance(predicates[1:]):
                    yield [f'{prefix}{predicate}'] + tail

    def generate_not_enhanced_mappings(predicates) -> Iterable[Dict]:
        for i_enhance, predicates_with_not in enumerate(not_enhance(predicates)):
            if i_enhance == 0:  # this is the original mapping
                continue
            mapping = copy.deepcopy(identity_mapping)
            for predicate_with_not in predicates_with_not:
                original_predicate = predicate_with_not.lstrip(f'{NEGATION}')
                mapping[original_predicate] = predicate_with_not
            yield mapping

    for i_not, mapping in enumerate(generate_not_enhanced_mappings(predicates)):
        if get_name:
            yield mapping, f'complication.not-{_fill_str(i_not)}'
        else:
            yield mapping

    if suppress_op_expansion_if_exists\
            and any([formula.rep.find(DISJUNCTION) >= 0 or formula.rep.find(CONJUNCTION) >= 0
                    for formula in formulas]):
        pass
    else:
        for op in [DISJUNCTION, CONJUNCTION]:
            for i_predicate_to_expand, predicate_to_expand in enumerate(predicates):
                unk_extended_predicates = [unk_pred0, unk_pred1]\
                    + predicates[:i_predicate_to_expand]\
                    + predicates[i_predicate_to_expand + 1:]
                for i_not, not_enhanced_mapping in enumerate(generate_not_enhanced_mappings(unk_extended_predicates)):
                    mapping = copy.deepcopy(not_enhanced_mapping)
                    for i_total_negation, total_negation_prefix in enumerate(['', NEGATION]):
                        mapping[predicate_to_expand] = f'{total_negation_prefix}({not_enhanced_mapping[unk_pred0]} {op} {not_enhanced_mapping[unk_pred1]})'
                        not_name_id = i_not * 2 + i_total_negation
                        if get_name:
                            yield mapping, f'complication.{op}-{_fill_str(i_predicate_to_expand)}.not-{_fill_str(not_name_id)}'
                        else:
                            yield mapping


def generate_arguments_in_target_space(src_arg: Argument,
                                       tgt_arg: Argument,
                                       add_complicated_arguments=False,
                                       constraints: Optional[Dict[str, str]] = None,
                                       shuffle=False,
                                       allow_many_to_one=True,
                                       elim_dneg=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_mappings_from_formula(src_arg.all_formulas,
                                                  tgt_arg.all_formulas,
                                                  add_complicated_arguments=add_complicated_arguments,
                                                  constraints=constraints,
                                                  shuffle=shuffle,
                                                  allow_many_to_one=allow_many_to_one):
        yield interpret_argument(src_arg, mapping, elim_dneg=elim_dneg), mapping


def generate_formulas_in_target_space(src_formula: Formula,
                                      tgt_formula: Formula,
                                      add_complicated_arguments=False,
                                      constraints: Optional[Dict[str, str]] = None,
                                      shuffle=False,
                                      allow_many_to_one=True,
                                      elim_dneg=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_mappings_from_formula([src_formula],
                                                  [tgt_formula],
                                                  add_complicated_arguments=add_complicated_arguments,
                                                  constraints=constraints,
                                                  shuffle=shuffle,
                                                  allow_many_to_one=allow_many_to_one):
        yield interpret_formula(src_formula, mapping, elim_dneg=elim_dneg), mapping


def generate_mappings_from_argument(src_argument: Argument,
                                    tgt_argument: Argument,
                                    add_complicated_arguments=False,
                                    constraints: Optional[Dict[str, str]] = None,
                                    shuffle=False,
                                    allow_many_to_one=True) -> Iterable[Dict[str, str]]:
    yield from generate_mappings_from_formula(
        src_argument.all_formulas,
        tgt_argument.all_formulas,
        add_complicated_arguments=add_complicated_arguments,
        constraints=constraints,
        shuffle=shuffle,
        allow_many_to_one=allow_many_to_one,
    )


def generate_mappings_from_formula(src_formulas: List[Formula],
                                   tgt_formulas: List[Formula],
                                   add_complicated_arguments=False,
                                   constraints: Optional[Dict[str, str]] = None,
                                   shuffle=False,
                                   allow_many_to_one=True,
                                   suppress_op_expansion_if_exists=False) -> Iterable[Dict[str, str]]:
    if add_complicated_arguments:
        complication_mappings = generate_complication_mappings_from_formula(
            src_formulas,
            suppress_op_expansion_if_exists=suppress_op_expansion_if_exists,
        )
    else:
        complication_mappings = [
            {p.rep: p.rep
             for formula in src_formulas
             for p in formula.predicates}  # identity mapping
        ]

    for complication_mapping in complication_mappings:
        complicated_formulas = [interpret_formula(formula, complication_mapping)
                                for formula in src_formulas]

        # Use "sorted" to eliminate randomness here.
        src_predicates = sorted(set([p.rep for src_formula in complicated_formulas for p in src_formula.predicates]))
        tgt_predicates = sorted(set([p.rep for tgt_formula in tgt_formulas for p in tgt_formula.predicates]))

        src_constants = sorted(set([c.rep for src_formula in complicated_formulas for c in src_formula.constants]))
        tgt_constants = sorted(set([c.rep for tgt_formula in tgt_formulas for c in tgt_formula.constants]))
        yield from generate_mappings_from_predicates_and_constants(src_predicates,
                                                                   src_constants,
                                                                   tgt_predicates,
                                                                   tgt_constants,
                                                                   constraints=constraints,
                                                                   shuffle=shuffle,
                                                                   allow_many_to_one=allow_many_to_one)


@profile
def generate_mappings_from_predicates_and_constants(src_predicates: List[str],
                                                    src_constants: List[str],
                                                    tgt_predicates: List[str],
                                                    tgt_constants: List[str],
                                                    constraints: Optional[Dict[str, str]] = None,
                                                    shuffle=False,
                                                    allow_many_to_one=True) -> Iterable[Dict[str, str]]:
    if len(src_predicates) == 0 or len(tgt_predicates) == 0:
        # identity mapping for formulas that do not have predicates.
        get_pred_mappings = lambda : [{}]
    else:
        get_pred_mappings = lambda: _generate_mappings(
            src_predicates,
            tgt_predicates,
            constraints=constraints,
            shuffle=shuffle,
            allow_many_to_one=allow_many_to_one,
        )

    if len(src_constants) == 0 or len(tgt_constants) == 0:
        # identity mapping for formulas that do not have constants.
        get_const_mappings = lambda: [{}]
    else:
        get_const_mappings = lambda: _generate_mappings(
            src_constants,
            tgt_constants,
            constraints=constraints,
            shuffle=shuffle,
            allow_many_to_one=allow_many_to_one,
        )

    for pred_mappings in get_pred_mappings():
        for const_mappings in get_const_mappings():
            mappings = copy.copy(pred_mappings)
            mappings.update(const_mappings)
            yield mappings


@profile
def _generate_mappings(src_objs: List[Any],
                       tgt_objs: List[Any],
                       constraints: Optional[Dict[Any, Any]] = None,
                       shuffle=False,
                       allow_many_to_one=True) -> Iterable[Optional[Dict[Any, Any]]]:
    if len(set(src_objs)) != len(src_objs):
        raise ValueError('Elements in src_objs are not unique: {src_objs}')
    if len(set(tgt_objs)) != len(tgt_objs):
        raise ValueError('Elements in tgt_objs are not unique: {tgt_objs}')

    if len(src_objs) > 0 and len(tgt_objs) > 0:
        if constraints is not None:
            idx_constraints = {src_objs.index(key): val
                               for key, val in constraints.items()
                               if key in src_objs}
        else:
            idx_constraints = None
        for chosen_tgt_objs in _make_permutations(tgt_objs,
                                                  len(src_objs),
                                                  constraints=idx_constraints,
                                                  shuffle=shuffle,
                                                  allow_many_to_one=allow_many_to_one):
            yield {
                src_obj: tgt_obj
                for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
            }
    else:
        raise ValueError()


def _make_permutations(objs: List[Any],
                       length: int,
                       src_idx=0,
                       constraints: Optional[Dict[int, Any]] = None,
                       shuffle=False,
                       allow_many_to_one=True,
                       indent=0) -> Iterable[List[Any]]:
    do_print = False
    if shuffle and do_print:
        print('\n')
        print(' ' * indent + '_make_permutations()')
        print(' ' * indent + '  shuffle:', shuffle)
        print(' ' * indent + '  objs:', objs)
        print(' ' * indent + '  length:', length)
    if length < 1:
        return
    if shuffle:
        objs = random.sample(objs, len(objs))  # shuffle

    if length == 1:
        if constraints is not None and src_idx in constraints:
            if shuffle and do_print:
                print(' ' * indent + '  yield0:', [constraints[src_idx]])
            yield [constraints[src_idx]]
        else:
            for obj in objs:
                if shuffle and do_print:
                    print(' ' * indent + '  yield1:', [obj])
                yield [obj]
    else:
        if constraints is not None and src_idx in constraints:
            heads = [constraints[src_idx]]
        else:
            heads = objs

        permutators = []
        for head in heads:
            if allow_many_to_one:
                tail_objs = objs
            else:
                tail_objs = objs.copy()

                while head in tail_objs:
                    tail_objs.remove(head)

                # the samle speed
                # while True:
                #     try:
                #         tail_objs.remove(head)
                #     except ValueError:
                #         break

                # slower
                # for obj in tail_objs:
                #     if obj == head:
                #         tail_objs.remove(head)

                # slower
                # for idx, obj in enumerate(reversed(tail_objs)):
                #     if obj == head:
                #         del tail_objs[len(tail_objs) - idx - 1]

                # slower
                # tail_objs = [obj for obj in objs
                #              if obj != head]

            tail_permutator = _make_permutations(tail_objs,
                                                 length - 1,
                                                 src_idx=src_idx + 1,
                                                 constraints=constraints,
                                                 shuffle=shuffle,
                                                 allow_many_to_one=allow_many_to_one,
                                                 indent=indent + 8)
            permutators.append((head, tail_permutator))

        if shuffle and do_print:
            is_done = [False] * len(permutators)
            i_head = 0
            while True:
                i_head = i_head % len(permutators)
                head, tail_permutator = permutators[i_head]
                if shuffle and do_print:
                    print(' ' * indent + f'  {i_head}: {str(head)}')
                if all(is_done):
                    break
                if is_done[i_head]:
                    i_head += 1
                    continue
                try:
                    tail = next(tail_permutator)
                    if shuffle and do_print:
                        print(' ' * indent + '  yield2:', [head] + tail)
                    yield [head] + tail
                except StopIteration:
                    is_done[i_head] = True
                i_head += 1
        else:
            for head, tail_permutator in permutators:
                for tail in tail_permutator:
                    if shuffle and do_print:
                        print(' ' * indent + '  yield3:', [head] + tail)
                    yield [head] + tail


@profile
def interpret_argument(arg: Argument,
                       mapping: Dict[str, str],
                       quantifier_types: Dict[str, str] = None,
                       elim_dneg=False) -> Argument:
    interpreted_premises = [interpret_formula(formula, mapping,
                                              quantifier_types=quantifier_types, elim_dneg=elim_dneg)
                            for formula in arg.premises]
    interpreted_assumptions = {
        interpreted_premise: interpret_formula(arg.assumptions[premise], mapping,
                                               quantifier_types=quantifier_types, elim_dneg=elim_dneg)
        for premise, interpreted_premise in zip(arg.premises, interpreted_premises)
        if premise in arg.assumptions
    }

    interpreted_intermediate_constants = [
        interpret_formula(constant, mapping,
                          quantifier_types=quantifier_types, elim_dneg=elim_dneg)
        for constant in arg.intermediate_constants
    ]

    interpreted_conclusion = interpret_formula(arg.conclusion, mapping,
                                               quantifier_types=quantifier_types, elim_dneg=elim_dneg)
    return Argument(interpreted_premises,
                    interpreted_conclusion,
                    interpreted_assumptions,
                    intermediate_constants=interpreted_intermediate_constants,
                    id=arg.id)


@profile
def interpret_formula(formula: Formula,
                      mapping: Dict[str, str],
                      quantifier_types: Dict[str, str] = None,
                      elim_dneg=False) -> Formula:

    interpreted_rep = _interpret_rep(formula.rep, mapping, elim_dneg=elim_dneg)
    interpreted_formula = Formula(interpreted_rep)
    return _interpret_formula_postprocess(interpreted_formula, quantifier_types=quantifier_types)



@profile
def interpret_formulas(formulas: List[Formula],
                       mapping: Dict[str, str],
                       quantifier_types: Dict[str, str] = None,
                       elim_dneg=False) -> List[Formula]:
    interpreted_reps = _interpret_reps([formula.rep for formula in formulas], mapping, elim_dneg=elim_dneg)
    interpreted_formulas = [Formula(interpreted_rep) for interpreted_rep in interpreted_reps]
    return [_interpret_formula_postprocess(interpreted_formula, quantifier_types=quantifier_types)
            for interpreted_formula in interpreted_formulas]


@profile
def _interpret_formula_postprocess(interpreted_formula: Formula,
                                   quantifier_types: Dict[str, str] = None) -> Formula:
    _expand_op_rep = _expand_op(interpreted_formula.rep)
    interpreted_formula = Formula(_expand_op_rep)

    if quantifier_types is not None:
        for var, type_ in quantifier_types.items():
            if var not in [var.rep for var in interpreted_formula.variables]:
                continue
            if var not in VARIABLES:
                raise ValueError(f'non-variable symbol {var} is specified in quantifier_types.')
            cur_rep = interpreted_formula.rep
            if type_ == 'universal':
                if cur_rep.find(':') >= 0:
                    next_rep = f'({var})' + cur_rep
                else:
                    next_rep = f'({var}): ' + cur_rep
            elif type_ == 'existential':
                if cur_rep.find(':') >= 0:
                    next_rep = f'(E{var})' + cur_rep
                else:
                    next_rep = f'(E{var}): ' + cur_rep
            else:
                raise ValueError(f'Unknown quantifier type {type_}')
            interpreted_formula = Formula(next_rep)

    return interpreted_formula


_EXPAND_OP_REGEXP = re.compile(f'\([^\(\)]*\)({"|".join([arg for arg in CONSTANTS + VARIABLES])})')


@profile
def _expand_op(rep: str) -> str:
    while True:
        # rep_wo_quantifier = Formula(rep).wo_quantifier.rep
        rep_wo_quantifier = strip_quantifier(rep)  # fast

        match = _get_expand_op_match(rep_wo_quantifier)
        if match is None:
            break

        op_PAS = match.group()
        op_pred, constant = op_PAS.lstrip('(').split(')')
        left_pred, op, right_pred = op_pred.split(' ')
        expanded_op_PAS = f'({left_pred}{constant} {op} {right_pred}{constant})'
        rep = rep.replace(f'{op_PAS}', f'{expanded_op_PAS}')
    return rep


@lru_cache(maxsize=10000000)
def _get_expand_op_match(rep: str) -> Optional[Match]:
    return _EXPAND_OP_REGEXP.search(rep)


# _INTERPRET_REP_CACHE = {}
# _INTERPRET_REP_CACHE_SIZE = 1000000


@profile
def _interpret_rep(rep: str,
                   mapping: Dict[str, str],
                   elim_dneg=False) -> str:
    # -- the cache does not speedup much
    # global _INTERPRET_REP_CACHE
    # cache_key = (rep, tuple(sorted(mapping.items())), elim_dneg)
    # if cache_key in _INTERPRET_REP_CACHE:
    #     return _INTERPRET_REP_CACHE[cache_key]

    interpreted_rep = rep

    if len(mapping) >= 1:
        pattern = re.compile("|".join(mapping.keys()))
        interpreted_rep = pattern.sub(lambda m: mapping[m.group(0)], rep)

    if elim_dneg:
        interpreted_rep = eliminate_double_negation(Formula(interpreted_rep)).rep

    # _INTERPRET_REP_CACHE[cache_key] = interpreted_rep
    return interpreted_rep



@profile
def _interpret_reps(reps: List[str],
                    mapping: Dict[str, str],
                    elim_dneg=False) -> str:
    splitter = '::::'
    rep = splitter.join(reps)
    interpreted_rep = _interpret_rep(rep, mapping, elim_dneg=elim_dneg)
    return interpreted_rep.split(splitter)



def formula_is_identical_to(this_formula: Formula,
                            that_formula: Formula,
                            allow_many_to_one=True,
                            add_complicated_arguments=False,
                            elim_dneg=False) -> bool:
    """ Check whether this formula can be the same as that formula by any mapping.

    Note that this and that is not symmetrical, unless allow_many_to_one=False.
    For example:
        this: {A}{a} -> {B}{b}
        that: {A}{a} -> {A}{a}

        formula_is_identical_to(this, that, allow_many_to_one=True): True
        formula_is_identical_to(that, this, allow_many_to_one=True): False

        formula_is_identical_to(this, that, allow_many_to_one=False): False
        formula_is_identical_to(that, this, allow_many_to_one=False): False
    """
    if elim_dneg:
        this_formula = eliminate_double_negation(this_formula)
        that_formula = eliminate_double_negation(that_formula)

    if formula_can_not_be_identical_to(this_formula, that_formula, add_complicated_arguments=add_complicated_arguments, elim_dneg=elim_dneg):
        return False

    for mapping in generate_mappings_from_formula([this_formula], [that_formula], add_complicated_arguments=add_complicated_arguments, allow_many_to_one=allow_many_to_one):
        this_interpreted = interpret_formula(this_formula, mapping, elim_dneg=elim_dneg)
        if this_interpreted.rep == that_formula.rep:
            return True
    return False


def formula_can_not_be_identical_to(this_formula: Formula,
                                    that_formula: Formula,
                                    add_complicated_arguments=False,
                                    elim_dneg=False) -> bool:
    """ Decide whether two formulas can not be identical by any mapping. Used for early rejection of is_formula_identical.

    NOTE that False does not mean two formulas are identical.
    """
    if elim_dneg:
        this_formula = eliminate_double_negation(this_formula)
        that_formula = eliminate_double_negation(that_formula)
    if add_complicated_arguments:
        # A little costly to implemente since the number of operators change by complication
        raise NotImplementedError()

    if (this_formula.premise is None) is not (that_formula.premise is None):
        return True
    elif this_formula.premise is not None:
        if formula_can_not_be_identical_to(this_formula.premise,
                                           that_formula.premise,
                                           add_complicated_arguments=add_complicated_arguments,
                                           elim_dneg=elim_dneg):
            return True
        elif formula_can_not_be_identical_to(this_formula.conclusion,
                                             that_formula.conclusion,
                                             add_complicated_arguments=add_complicated_arguments,
                                             elim_dneg=elim_dneg):
            return True

    if len(this_formula.universal_variables) != len(that_formula.universal_variables):
        return True

    if len(this_formula.existential_variables) != len(that_formula.existential_variables):
        return True

    this_zeroary_pred_cnt = _get_appearance_cnt(this_formula.zeroary_predicates, this_formula)
    that_zeroary_pred_cnt = _get_appearance_cnt(that_formula.zeroary_predicates, that_formula)
    if this_zeroary_pred_cnt != that_zeroary_pred_cnt:
        return True

    this_unary_pred_cnt = _get_appearance_cnt(this_formula.unary_predicates, this_formula)
    that_unary_pred_cnt = _get_appearance_cnt(that_formula.unary_predicates, that_formula)
    if this_unary_pred_cnt != that_unary_pred_cnt:
        return True

    this_constant_cnt = _get_appearance_cnt(this_formula.constants, this_formula)
    that_constant_cnt = _get_appearance_cnt(that_formula.constants, that_formula)
    if this_constant_cnt != that_constant_cnt:
        return True

    this_univ_variable_cnt = _get_appearance_cnt(this_formula.universal_variables, this_formula)
    that_univ_variable_cnt = _get_appearance_cnt(that_formula.universal_variables, that_formula)
    if this_univ_variable_cnt != that_univ_variable_cnt:
        return True

    this_exist_variable_cnt = _get_appearance_cnt(this_formula.existential_variables, this_formula)
    that_exist_variable_cnt = _get_appearance_cnt(that_formula.existential_variables, that_formula)
    if this_exist_variable_cnt != that_exist_variable_cnt:
        return True

    if any([this_formula.rep.count(symbol) != that_formula.rep.count(symbol)
            for symbol in [CONJUNCTION, DISJUNCTION, IMPLICATION, NEGATION]]):
        return True

    return False


def _get_appearance_cnt(formulas: List[Formula], tgt_formula: Formula) -> int:
    # Calculate the appearance  of formulas in formula
    # e.g.)
    #   formulas: ['{A}', '{B}']
    #   tgt_formula: '{A} & {B} -> {A}'
    #   return 3
    return sum(
        [tgt_formula.rep.count(formula.rep) for formula in formulas]
        or [0]
    )


def argument_is_identical_to(this_argument: Argument,
                             that_argument: Argument,
                             allow_many_to_one=True,
                             add_complicated_arguments=False,
                             elim_dneg=False) -> bool:

    def _formula_can_not_be_identical_to(this_formula: Formula, that_formula: Formula) -> bool:
        return formula_can_not_be_identical_to(this_formula, that_formula,
                                               add_complicated_arguments=add_complicated_arguments,
                                               elim_dneg=elim_dneg)

    # early rejections by conclusion
    if _formula_can_not_be_identical_to(this_argument.conclusion, that_argument.conclusion):
        return False

    # early rejections by premises
    if len(this_argument.premises) != len(that_argument.premises):
        return False
    if len(this_argument.premises) >= 1:
        if any(
            all(_formula_can_not_be_identical_to(this_premise, that_premise)
                for that_premise in that_argument.premises)
            for this_premise in this_argument.premises
        ):
            return False
        for this_premise in this_argument.premises:
            if this_premise not in this_argument.assumptions:
                continue

            this_assumption = this_argument.assumptions[this_premise]

            that_assumptions = [that_argument.assumptions[that_premise] for that_premise in that_argument.premises
                                if that_premise in that_argument.assumptions]

            if not any(not _formula_can_not_be_identical_to(this_assumption, that_assumption)
                       for that_assumption in that_assumptions):
                return False

    # early rejections by intermediate_constants
    if len(this_argument.intermediate_constants) != len(that_argument.intermediate_constants):
        return False
    if len(this_argument.intermediate_constants) >= 1:
        if any(
            all(_formula_can_not_be_identical_to(this_constant, that_constant)
                for that_constant in that_argument.intermediate_constants)
            for this_constant in this_argument.intermediate_constants
        ):
            return False

    def is_premises_and_assumptions_same(this_argument: Argument, that_argument: Argument) -> bool:
        _is_premises_same = False
        for premise_indexes in permutations(range(len(that_argument.premises))):
            that_premises_permuted = [that_argument.premises[i] for i in premise_indexes]
            for this_premise, that_premise in zip(this_argument.premises, that_premises_permuted):
                if this_premise.rep != that_premise.rep:
                    continue

                this_assumption = this_argument.assumptions.get(this_premise, None)
                that_assumption = that_argument.assumptions.get(that_premise, None)

                if this_assumption is None and that_assumption is None:
                    _is_premises_same = True
                    break
                elif this_assumption is not None and that_assumption is not None:
                    if this_assumption.rep == that_assumption.rep:
                        _is_premises_same = True
                        break
                else:
                    continue
        return _is_premises_same

    def is_intermediate_constants_same(this_argument: Argument, that_argument: Argument) -> bool:
        return set(constant.rep for constant in this_argument.intermediate_constants)\
            == set(constant.rep for constant in that_argument.intermediate_constants)

    def is_conclusion_same(this_argument: Argument, that_argument: Argument) -> bool:
        return this_argument.conclusion.rep == that_argument.conclusion.rep

    # check the exact identification condition.
    for mapping in generate_mappings_from_argument(this_argument,
                                                   that_argument,
                                                   add_complicated_arguments=add_complicated_arguments,
                                                   allow_many_to_one=allow_many_to_one):
        this_argument_interpreted = interpret_argument(this_argument, mapping, elim_dneg=elim_dneg)

        # XXX: DO NOT change the order of validation. It is now ordered as "faster former"
        if is_conclusion_same(this_argument_interpreted, that_argument)\
                and is_intermediate_constants_same(this_argument_interpreted, that_argument)\
                and is_premises_and_assumptions_same(this_argument_interpreted, that_argument):
            return True

    # It is possible that no mappings are found (e.g. when no predicate and constants are in arguments)
    # but the arguments are the same from the beggining
    if is_conclusion_same(this_argument, that_argument)\
            and is_intermediate_constants_same(this_argument, that_argument)\
            and is_premises_and_assumptions_same(this_argument, that_argument):
        return True

    return False


@profile
def generate_quantifier_axiom_arguments(
    argument_type: str,
    formula: Formula,
    id_prefix: Optional[str] = None,
    quantification_degree: str = 'one_constant',
    e_elim_conclusion_formula_prototype: Optional[Formula] = None,
) -> Iterable[Argument]:
    """

    Examples:
        See the test codes.
    """
    available_arguments = ['universal_quantifier_intro', 'universal_quantifier_elim', 'existential_quantifier_intro', 'existential_quantifier_elim']
    if argument_type not in available_arguments:
        raise ValueError(f'Unsupported quantifier axiom {argument_type}')
    if len(formula.variables) > 0:
        raise NotImplementedError()

    if quantification_degree not in _QUANTIFICATION_DEGREES:
        raise ValueError(f'Unknown quantification degree "{dquantification_degreeegree}"')
    if quantification_degree == 'all_constants_in_implication_premise_conclusion' and formula.rep.count(IMPLICATION) >= 2:
        raise NotImplementedError()

    def is_constant_only(formula: Formula) -> bool:
        return len(formula.constants) > 0 and len(formula.variables) == 0

    def is_variable_only(formula: Formula) -> bool:
        return len(formula.variables) > 0 and len(formula.constants) == 0

    def is_individual_type_single(formula: Formula) -> bool:
        return is_constant_only(formula) or is_variable_only(formula)

    de_quantifier_constant = sorted(set(CONSTANTS) - {c.rep for c in formula.constants})[0]
    for i, quantifier_mapping in enumerate(
        generate_quantifier_mappings([formula],
                                     all_constants=quantification_degree == 'all_constants')):
        quantifier_variables = {
            tgt for src, tgt in quantifier_mapping.items()
            if src != tgt
        }
        if len(quantifier_variables) == 0:
            continue
        elif len(quantifier_variables) >= 2:
            raise NotImplementedError()
        quantifier_variable = list(quantifier_variables)[0]

        de_quantifier_mapping = {
            src: (de_quantifier_constant if tgt == quantifier_variable else src)
            for src, tgt in quantifier_mapping.items()
        }

        xyz_formula = interpret_formula(formula, quantifier_mapping)
        abc_formula = interpret_formula(formula, de_quantifier_mapping)

        if quantification_degree == 'all_constants_in_implication_premise_conclusion':
            if (xyz_formula.premise is not None and not is_individual_type_single(xyz_formula.premise))\
                    or (xyz_formula.conclusion is not None and not is_individual_type_single(xyz_formula.conclusion)):
                continue

        if argument_type.startswith('universal_'):
            quantifier_formula = Formula(f'({quantifier_variable}): {xyz_formula.rep}')
            de_quantifier_formula = abc_formula

            if argument_type == 'universal_quantifier_elim':
                argument_id = f'{id_prefix}.quantifier_axiom.universal_elim-{i}' if id_prefix is not None else f'quantifier_axiom.universal_elim-{i}'
                argument = Argument(
                    [quantifier_formula],
                    de_quantifier_formula,
                    {},
                    id = argument_id,
                )
            elif argument_type == 'universal_quantifier_intro':
                quantified_constant_reps = list(
                    set([constant.rep for constant in de_quantifier_formula.constants])
                    - set([constant.rep for constant in quantifier_formula.constants])
                )
                quantified_constants = [Formula(rep) for rep in quantified_constant_reps]

                argument_id = f'{id_prefix}.quantifier_axiom.universal_intro-{i}' if id_prefix is not None else f'quantifier_axiom.universal_intro-{i}'
                argument = Argument(
                    [de_quantifier_formula],
                    quantifier_formula,
                    {},
                    intermediate_constants=quantified_constants,
                    id=argument_id,
                )

        elif argument_type == 'existential_quantifier_intro':
            quantifier_formula = Formula(f'(E{quantifier_variable}): {xyz_formula.rep}')
            de_quantifier_formula = abc_formula
            argument_id = f'{id_prefix}.quantifier_axiom.existential_intro--{i}' if id_prefix is not None else f'quantifier_axiom.existential_intro--{i}'
            argument = Argument(
                [de_quantifier_formula],
                quantifier_formula,
                {},
                id = argument_id,
            )

        elif argument_type == 'existential_quantifier_elim':
            if e_elim_conclusion_formula_prototype is None:
                raise ValueError()
            used_predicate_reps = {predicate.rep for predicate in xyz_formula.predicates}
            unused_predicate_reps = [predicate_rep for predicate_rep in PREDICATES if predicate_rep not in used_predicate_reps]

            used_constant_reps = {constant.rep for constant in xyz_formula.constants}
            unused_constant_reps = [constant_rep for constant_rep in CONSTANTS if constant_rep not in used_constant_reps]

            # remove predicate and constant used by quantifier formulas.
            e_elim_conclusion_formula_unentangled: Optional[Formula] = None
            for mapping in generate_mappings_from_predicates_and_constants(
                [p.rep for p in e_elim_conclusion_formula_prototype.predicates],
                [c.rep for c in e_elim_conclusion_formula_prototype.constants],
                unused_predicate_reps,
                unused_constant_reps,
                allow_many_to_one=False,
            ):
                e_elim_conclusion_formula_unentangled = interpret_formula(e_elim_conclusion_formula_prototype, mapping)
                break
            if e_elim_conclusion_formula_unentangled is None:
                raise Exception()

            existential_quantifier_formula = Formula(f'(E{quantifier_variable}): {xyz_formula.rep}')
            universal_quantifier_formula = Formula(f'({quantifier_variable}): {xyz_formula.rep} {IMPLICATION} {e_elim_conclusion_formula_unentangled.rep}')

            argument_id = f'{id_prefix}.quantifier_axiom.existential_elim--{i}' if id_prefix is not None else f'quantifier_axiom.existential_elim--{i}'
            argument = Argument(
                [existential_quantifier_formula, universal_quantifier_formula],
                e_elim_conclusion_formula_unentangled,
                {},
                id = argument_id,
            )

        yield argument


def generate_partially_quantifier_arguments(src_arg: Argument,
                                            quantifier_type: str,
                                            elim_dneg=False,
                                            quantification_degree: str = 'one_constant',
                                            get_name=False) -> Union[Iterable[Tuple[Argument, Dict[str, str]]], Iterable[Tuple[Argument, Dict[str, str], str]]]:
    """

    Examples:
        See the test codes.
    """
    # XXX: We should not quantify the conclusion since such arguments do not hold
    raise NotImplementedError()
    if quantification_degree == 'all_constants_in_implication_premise_conclusion':
        raise NotImplementedError()

    for mapping, name in generate_quantifier_mappings(src_arg.all_formulas,
                                                      all_constants = quantification_degree == 'all_constants',
                                                      get_name=True):
        constants_appearing_only_in_one_formula = set()
        for i_formula, formula in enumerate(src_arg.all_formulas):
            other_formulas = [other_formula
                              for other_formula in src_arg.all_formulas
                              if other_formula != formula]
            for constant in formula.constants:
                if all(constant.rep not in [other_constant.rep for other_constant in other_formula.constants]
                       for other_formula in other_formulas):
                    constants_appearing_only_in_one_formula.add(constant.rep)

        quantified_constants = [src for src, tgt in mapping.items() if tgt in VARIABLES]
        quantified_variables = [tgt for tgt in mapping.values() if tgt in VARIABLES]
        if not all(src_constant in constants_appearing_only_in_one_formula
                   for src_constant in quantified_constants):
            continue

        if quantification_degree == 'all_constants':
            is_all_or_nothing = True  # In a formula, all or no constants should be converted to variable at once
            for formula in src_arg.all_formulas:
                constant_reps = {constant.rep for constant in formula.constants}
                if len(constant_reps - set(quantified_constants)) not in [0, len(constant_reps)]:
                    is_all_or_nothing = False
                    break
            if not is_all_or_nothing:
                continue

        complicated_argument = interpret_argument(
            src_arg,
            mapping,
            quantifier_types={tgt_var: quantifier_type for tgt_var in quantified_variables},
            elim_dneg=elim_dneg
        )

        if get_name:
            yield complicated_argument, mapping, name
        else:
            yield complicated_argument, mapping


def generate_quantifier_formulas(src_formula: Formula,
                                 quantifier_type: str,
                                 all_constants=False,
                                 get_name=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for i, (quantifier_mapping, name) in enumerate(generate_quantifier_mappings([src_formula],
                                                                                all_constants=all_constants,
                                                                                get_name=True)):
        quantifier_variables = [tgt for tgt in quantifier_mapping.values()
                                if tgt in VARIABLES]

        quantifier_formula = interpret_formula(
            src_formula,
            quantifier_mapping,
            quantifier_types={var: quantifier_type for var in quantifier_variables}
        )

        if get_name:
            name = f'quantifier-{_fill_str(i)}'
            yield quantifier_formula, quantifier_mapping, name
        else:
            yield quantifier_formula, quantifier_mapping


@profile
def generate_quantifier_mappings(formulas: List[Formula],
                                 all_constants=False,
                                 get_name=False)\
        -> Union[Iterable[Dict[str, str]], Iterable[Tuple[Dict[str, str], str]]]:

    tgt_variable = sorted(
        set(VARIABLES) - {v.rep for formula in formulas for v in formula.variables}
    )[0]

    def enum_all_quantifier_mappings(constants: List[str]) -> Iterable[Dict]:

        if len(constants) == 0:
            yield {}
            return

        src_constant = constants[0]
        tgt_constant_reps = [tgt_variable] if all_constants else [src_constant, tgt_variable]
        for tgt_constant_rep in tgt_constant_reps:
            for mapping in enum_all_quantifier_mappings(constants[1:]):
                mapping[src_constant] = tgt_constant_rep
                yield mapping

    constants = sorted({c.rep for formula in formulas for c in formula.constants})[::-1]
    i = 0
    for mapping in enum_all_quantifier_mappings(constants):
        quantifier_variables = [tgt for src, tgt in sorted(mapping.items())
                                if src != tgt and tgt in VARIABLES]
        if len(quantifier_variables) == 0:
            continue

        if get_name:
            yield mapping, f'quantifier-{_fill_str(i)}'
        else:
            yield mapping
        i += 1
