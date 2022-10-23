import re
import random
from typing import Dict, List, Any, Iterable, Tuple, Optional, Union, Set
import copy
from itertools import permutations

from .formula import (
    Formula,
    NEGATION,
    OR,
    AND,
    IMPLICATION,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
    eliminate_double_negation,
    negate,
)
from .argument import Argument
import kern_profiler


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
            and any([formula.rep.find(OR) >= 0 or formula.rep.find(AND) >= 0
                    for formula in formulas]):
        pass
    else:
        for op in [OR, AND]:
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


# -- block shuffle version --
# def _make_permutations(objs: List[Any],
#                        length: int,
#                        src_idx=0,
#                        constraints: Optional[Dict[int, Any]] = None,
#                        shuffle=False,
#                        block_size=10000,
#                        allow_many_to_one=True) -> Iterable[List[Any]]:
#     """
# 
#     shuffle=Trueであって，完全にshuffleできるわけではない．
#     for head in heads: のループにおいて，headごとにブロック化しているため．
#     しかし，ここをshuffleしようとすると，generatorではなくlistを作る必要があり，速度が落ちる．
#     """
#     if length < 1:
#         return
#     if shuffle:
#         objs = random.sample(objs, len(objs))  # shuffle
# 
#     if length == 1:
#         if constraints is not None and src_idx in constraints:
#             yield [constraints[src_idx]]
#         else:
#             for obj in objs:
#                 yield [obj]
#     else:
#         if constraints is not None and src_idx in constraints:
#             heads = [constraints[src_idx]]
#         else:
#             heads = objs
# 
#         block: List[Any] = []
#         for head in heads:
#             if allow_many_to_one:
#                 tail_objs = objs
#             else:
#                 tail_objs = objs.copy()
#                 while head in tail_objs:
#                     tail_objs.remove(head)
# 
#             for tail in _make_permutations(tail_objs,
#                                            length - 1,
#                                            src_idx=src_idx + 1,
#                                            constraints=constraints,
#                                            shuffle=shuffle,
#                                            allow_many_to_one=allow_many_to_one):
#                 if len(block) >= block_size:
#                     yield from block
#                     block = []
# 
#                 if shuffle:
#                     block.append([head] + tail)
#                 else:
#                     yield [head] + tail
# 
#         yield from block


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
    interpreted_conclusion = interpret_formula(arg.conclusion, mapping,
                                               quantifier_types=quantifier_types, elim_dneg=elim_dneg)
    return Argument(interpreted_premises,
                    interpreted_conclusion,
                    interpreted_assumptions,
                    id=arg.id,
                    base_scheme_group=arg.base_scheme_group,
                    scheme_variant=arg.scheme_variant)


@profile
def interpret_formula(formula: Formula,
                       mapping: Dict[str, str],
                       quantifier_types: Dict[str, str] = None,
                       elim_dneg=False) -> Formula:

    interpreted_formula = _expand_op(
        Formula(
            _interpret_rep(formula.rep, mapping, elim_dneg=elim_dneg)
        )
    )

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


_expand_op_regexp = re.compile(f'\([^\)]*\)({"|".join([arg for arg in CONSTANTS + VARIABLES])})')


def _expand_op(formula: Formula) -> Formula:
    rep = formula.rep

    while True:
        rep_wo_quantifier = Formula(rep).wo_quantifier.rep

        match = _expand_op_regexp.search(rep_wo_quantifier)
        if match is None:
            break

        op_PAS = match.group()
        op_pred, constant = op_PAS.lstrip('(').split(')')
        left_pred, op, right_pred = op_pred.split(' ')
        expanded_op_PAS = f'({left_pred}{constant} {op} {right_pred}{constant})'
        rep = rep.replace(f'{op_PAS}', f'{expanded_op_PAS}')

    return Formula(rep)


@profile
def _interpret_rep(rep: str,
                    mapping: Dict[str, str],
                    elim_dneg=False) -> str:
    interpreted_rep = rep

    if len(mapping) >= 1:
        pattern = re.compile("|".join(mapping.keys()))
        interpreted_rep = pattern.sub(lambda m: mapping[m.group(0)], rep)

    if elim_dneg:
        interpreted_rep = eliminate_double_negation(Formula(interpreted_rep)).rep

    return interpreted_rep


def formula_is_identical_to(this_formula: Formula,
                            that_formula: Formula,
                            allow_many_to_oneg=True,
                            add_complicated_arguments=False,
                            elim_dneg=False) -> bool:
    """ Check whether this formula can be the same as that formula by any mapping.

    Note that this and that is not symmetrical, unless allow_many_to_oneg=False.
    For example:
        this: {A}{a} -> {B}{b}
        that: {A}{a} -> {A}{a}

        formula_is_identical_to(this, that, allow_many_to_oneg=True): True
        formula_is_identical_to(that, this, allow_many_to_oneg=True): False

        formula_is_identical_to(this, that, allow_many_to_oneg=False): False
        formula_is_identical_to(that, this, allow_many_to_oneg=False): False
    """
    if elim_dneg:
        this_formula = eliminate_double_negation(this_formula)
        that_formula = eliminate_double_negation(that_formula)

    if formula_can_not_be_identical_to(this_formula, that_formula, add_complicated_arguments=add_complicated_arguments, elim_dneg=elim_dneg):
        return False

    for mapping in generate_mappings_from_formula([this_formula], [that_formula], add_complicated_arguments=add_complicated_arguments, allow_many_to_one=allow_many_to_oneg):
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
            for symbol in [AND, OR, IMPLICATION, NEGATION]]):
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


@profile
def argument_is_identical_to(this_argument: Argument,
                             that_argument: Argument,
                             allow_many_to_oneg=True,
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

    def is_conclusion_same(this_argument: Argument, that_argument: Argument) -> bool:
        return this_argument.conclusion.rep == that_argument.conclusion.rep

    def is_premises_same(this_argument: Argument, that_argument: Argument) -> bool:
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

    # check the exact identification condition.
    for mapping in generate_mappings_from_argument(this_argument,
                                                   that_argument,
                                                   add_complicated_arguments=add_complicated_arguments,
                                                   allow_many_to_one=allow_many_to_oneg):
        this_argument_interpreted = interpret_argument(this_argument, mapping, elim_dneg=elim_dneg)

        if is_conclusion_same(this_argument_interpreted, that_argument)\
                and is_premises_same(this_argument_interpreted, that_argument):
            return True

    # It is possible that no mappings are found (e.g. when no predicate and constants are in arguments)
    # but the arguments are the same from the beggining
    if is_conclusion_same(this_argument, that_argument)\
            and is_premises_same(this_argument, that_argument):
        return True

    return False


def generate_quantifier_axiom_arguments(
    argument_type: str,
    formula: Formula,
    id_prefix: Optional[str] = None,
    quantify_all_at_once=False,
) -> Iterable[Argument]:
    """

    Examples:
        See the test codes.
    """
    if len(formula.variables) > 0:
        raise NotImplementedError('Multiple quantifier is not supported yet.')

    de_quantifier_constant = sorted(set(CONSTANTS) - {c.rep for c in formula.constants})[0]
    for i, quantifier_mapping in enumerate(generate_quantifier_mappings([formula], quantify_all_at_once=quantify_all_at_once)):
        quantifier_variables = [tgt for src, tgt in quantifier_mapping.items()
                                if src != tgt]
        if len(quantifier_variables) == 0:
            continue
        quantifier_variable = quantifier_variables[0]

        de_quantifier_mapping = {
            src: (de_quantifier_constant if tgt == quantifier_variable else src)
            for src, tgt in quantifier_mapping.items()
        }

        if argument_type == 'universal_quantifier_elim':
            quantifier_formula = Formula(f'({quantifier_variable}): ' + interpret_formula(formula, quantifier_mapping).rep)
            de_quantifier_formula = interpret_formula(formula, de_quantifier_mapping)
            argument_id = f'{id_prefix}.quantifier_axiom.universal_elim-{i}' if id_prefix is not None else f'quantifier_axiom.universal_elim-{i}'
            argument = Argument(
                [quantifier_formula],
                de_quantifier_formula,
                {},
                id = argument_id,
            )
        elif argument_type == 'existential_quantifier_intro':
            quantifier_formula = Formula(f'(E{quantifier_variable}): ' + interpret_formula(formula, quantifier_mapping).rep)
            de_quantifier_formula = interpret_formula(formula, de_quantifier_mapping)
            argument_id = f'{id_prefix}.quantifier_axiom.existential_elim--{i}' if id_prefix is not None else f'quantifier_axiom.existential_elim--{i}'
            argument = Argument(
                [de_quantifier_formula],
                quantifier_formula,
                {},
                id = argument_id,
            )
        else:
            raise ValueError()

        yield argument


def generate_partially_quantifier_arguments(src_arg: Argument,
                                            quantifier_type: str,
                                            elim_dneg=False,
                                            quantify_all_at_once=False,
                                            quantify_all_at_once_in_a_formula=False,
                                            get_name=False) -> Union[Iterable[Tuple[Argument, Dict[str, str]]], Iterable[Tuple[Argument, Dict[str, str], str]]]:
    """

    Examples:
        See the test codes.
    """
    # XXX: We should not quantify the conclusion since such arguments do not hold
    raise NotImplementedError()

    for mapping, name in generate_quantifier_mappings(src_arg.all_formulas,
                                                      quantify_all_at_once=quantify_all_at_once,
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

        if quantify_all_at_once_in_a_formula:
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
                                 quantify_all_at_once=False,
                                 get_name=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for i, quantifier_mapping in enumerate(generate_quantifier_mappings([src_formula],
                                                                        quantify_all_at_once=quantify_all_at_once,
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


def generate_quantifier_mappings(formulas: List[Formula],
                                 quantify_all_at_once=False,
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
        tgt_constant_reps = [tgt_variable] if quantify_all_at_once else [src_constant, tgt_variable]
        for tgt_constant_rep in tgt_constant_reps:
            for mapping in enum_all_quantifier_mappings(constants[1:]):
                mapping[src_constant] = tgt_constant_rep
                yield mapping

    constants = {c.rep for formula in formulas for c in formula.constants}
    i = 0
    for mapping in enum_all_quantifier_mappings(list(constants)):
        quantifier_variables = [tgt for src, tgt in mapping.items()
                                if src != tgt and tgt in VARIABLES]
        if len(quantifier_variables) == 0:
            continue

        if get_name:
            yield mapping, f'quantifier-{_fill_str(i)}'
        else:
            yield mapping
        i += 1
