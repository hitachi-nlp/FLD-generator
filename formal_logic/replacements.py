import re
import random
from typing import Dict, List, Any, Iterable, Tuple, Optional, Union
import copy
from itertools import permutations

from .formula import (
    Formula,
    NOT,
    OR,
    AND,
    IMPLICATION,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
    eliminate_double_negation,
)
from .argument import Argument
import kern_profiler


def generate_complicated_arguments(src_arg: Argument,
                                   elim_dneg=False,
                                   get_name=False) -> Union[Iterable[Tuple[Argument, Dict[str, str]]], Iterable[Tuple[Argument, Dict[str, str], str]]]:
    for mapping, name in generate_complication_mappings_from_formula(src_arg.premises + [src_arg.conclusion], get_name=True):
        replaced_argument = replace_argument(src_arg, mapping, elim_dneg=elim_dneg)
        if get_name:
            yield replaced_argument, mapping, name
        else:
            yield replaced_argument, mapping


def generate_complicated_formulas(src_formula: Formula,
                                  elim_dneg=False,
                                  get_name=False) -> Union[Iterable[Tuple[Formula, Dict[str, str]]], Iterable[Tuple[Formula, Dict[str, str], str]]]:
    for mapping, name in generate_complication_mappings_from_formula([src_formula], get_name=True):
        replaced_formula = replace_formula(src_formula, mapping, elim_dneg=elim_dneg)
        if get_name:
            yield replaced_formula, mapping, name
        else:
            yield replaced_formula, mapping


def generate_complication_mappings_from_formula(formulas: List[Formula],
                                                get_name=False,
                                                suppress_op_expansion_if_exists=True) -> Union[Iterable[Dict[str, str]], Iterable[Tuple[Dict[str, str], str]]]:
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
            for prefix in ['', f'{NOT}']:
                yield [f'{prefix}{predicate}']
        else:
            predicate = predicates[0]
            for prefix in ['', f'{NOT}']:
                for tail in not_enhance(predicates[1:]):
                    yield [f'{prefix}{predicate}'] + tail

    def generate_not_enhanced_mappings(predicates) -> Iterable[Dict]:
        for i_enhance, predicates_with_not in enumerate(not_enhance(predicates)):
            if i_enhance == 0:  # this is the original mapping
                continue
            mapping = copy.deepcopy(identity_mapping)
            for predicate_with_not in predicates_with_not:
                original_predicate = predicate_with_not.lstrip(f'{NOT}')
                mapping[original_predicate] = predicate_with_not
            yield mapping

    for i_not, mapping in enumerate(generate_not_enhanced_mappings(predicates)):
        if get_name:
            yield mapping, f'not-{i_not}'
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
                    mapping[predicate_to_expand] = f'({not_enhanced_mapping[unk_pred0]} {op} {not_enhanced_mapping[unk_pred1]})'
                    if get_name:
                        yield mapping, f'{op}-{i_predicate_to_expand}.not-{i_not}'
                    else:
                        yield mapping


def generate_replaced_arguments(src_arg: Argument,
                                tgt_arg: Argument,
                                allow_complication=False,
                                constraints: Optional[Dict[str, str]] = None,
                                block_shuffle=False,
                                allow_replacement=True,
                                elim_dneg=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula(src_arg.premises + [src_arg.conclusion],
                                                              tgt_arg.premises + [tgt_arg.conclusion],
                                                              allow_complication=allow_complication,
                                                              constraints=constraints,
                                                              block_shuffle=block_shuffle,
                                                              allow_replacement=allow_replacement):
        yield replace_argument(src_arg, mapping, elim_dneg=elim_dneg), mapping


def generate_replaced_formulas(src_formula: Formula,
                               tgt_formula: Formula,
                               allow_complication=False,
                               constraints: Optional[Dict[str, str]] = None,
                               block_shuffle=False,
                               allow_replacement=True,
                               elim_dneg=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula([src_formula],
                                                              [tgt_formula],
                                                              allow_complication=allow_complication,
                                                              constraints=constraints,
                                                              block_shuffle=block_shuffle,
                                                              allow_replacement=allow_replacement):
        yield replace_formula(src_formula, mapping, elim_dneg=elim_dneg), mapping


@profile
def generate_replacement_mappings_from_argument(src_argument: Argument,
                                                tgt_argument: Argument,
                                                allow_complication=False,
                                                constraints: Optional[Dict[str, str]] = None,
                                                block_shuffle=False,
                                                allow_replacement=True) -> Iterable[Dict[str, str]]:
    yield from generate_replacement_mappings_from_formula(
        src_argument.all_formulas,
        tgt_argument.all_formulas,
        allow_complication=allow_complication,
        constraints=constraints,
        block_shuffle=block_shuffle,
        allow_replacement=allow_replacement,
    )


@profile
def generate_replacement_mappings_from_formula(src_formulas: List[Formula],
                                               tgt_formulas: List[Formula],
                                               allow_complication=False,
                                               constraints: Optional[Dict[str, str]] = None,
                                               block_shuffle=False,
                                               allow_replacement=True) -> Iterable[Dict[str, str]]:
    if allow_complication:
        complication_mappings = generate_complication_mappings_from_formula(src_formulas)
    else:
        complication_mappings = [
            {p.rep: p.rep
             for formula in src_formulas
             for p in formula.predicates}  # identity mapping
        ]

    for complication_mapping in complication_mappings:
        complicated_formulas = [replace_formula(formula, complication_mapping)
                                for formula in src_formulas]

        # Use "sorted" to eliminate randomness here.
        src_predicates = sorted(set([p.rep for src_formula in complicated_formulas for p in src_formula.predicates]))
        tgt_predicates = sorted(set([p.rep for tgt_formula in tgt_formulas for p in tgt_formula.predicates]))

        src_constants = sorted(set([c.rep for src_formula in complicated_formulas for c in src_formula.constants]))
        tgt_constants = sorted(set([c.rep for tgt_formula in tgt_formulas for c in tgt_formula.constants]))
        yield from generate_replacement_mappings_from_terms(src_predicates,
                                                            src_constants,
                                                            tgt_predicates,
                                                            tgt_constants,
                                                            constraints=constraints,
                                                            block_shuffle=block_shuffle,
                                                            allow_replacement=allow_replacement)


@profile
def generate_replacement_mappings_from_terms(src_predicates: List[str],
                                             src_constants: List[str],
                                             tgt_predicates: List[str],
                                             tgt_constants: List[str],
                                             constraints: Optional[Dict[str, str]] = None,
                                             block_shuffle=False,
                                             allow_replacement=True) -> Iterable[Dict[str, str]]:
    get_pred_replacements = lambda: _generate_replacement_mappings(
        src_predicates,
        tgt_predicates,
        constraints=constraints,
        block_shuffle=block_shuffle,
        allow_replacement=allow_replacement,
    )

    get_const_replacements = lambda: _generate_replacement_mappings(
        src_constants,
        tgt_constants,
        constraints=constraints,
        block_shuffle=block_shuffle,
        allow_replacement=allow_replacement,
    )

    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            if pred_replacements is None or const_replacements is None:
                continue
            replacements = copy.copy(pred_replacements)
            replacements.update(const_replacements)

            yield replacements


@profile
def _generate_replacement_mappings(src_objs: List[Any],
                                   tgt_objs: List[Any],
                                   constraints: Optional[Dict[Any, Any]] = None,
                                   block_shuffle=False,
                                   allow_replacement=True) -> Iterable[Optional[Dict[Any, Any]]]:
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
                                                  block_shuffle=block_shuffle,
                                                  allow_replacement=allow_replacement):
            yield {
                src_obj: tgt_obj
                for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
            }
    elif len(src_objs) == 0 and len(tgt_objs) == 0:
        yield {}
    elif len(src_objs) == 0 and len(tgt_objs) > 0:
        yield {}
    else:
        yield None


@profile
def _make_permutations(objs: List[Any],
                       length: int,
                       src_idx=0,
                       constraints: Optional[Dict[int, Any]] = None,
                       block_shuffle=False,
                       allow_replacement=True) -> Iterable[List[Any]]:
    """

    block_shuffle=Trueであって，完全にblock_shuffleできるわけではない．
    for head in heads: のループにおいて，headごとにブロック化しているため．
    しかし，ここをblock_shuffleしようとすると，generatorではなくlistを作る必要があり，速度が落ちる．
    """
    if length < 1:
        return
    if block_shuffle:
        objs = random.sample(objs, len(objs))  # shuffle

    if length == 1:
        if constraints is not None and src_idx in constraints:
            yield [constraints[src_idx]]
        else:
            for obj in objs:
                yield [obj]
    else:
        if constraints is not None and src_idx in constraints:
            heads = [constraints[src_idx]]
        else:
            heads = objs
        for head in heads:
            if allow_replacement:
                tail_objs = objs
            else:
                tail_objs = objs.copy()
                while head in tail_objs:
                    tail_objs.remove(head)
            for tail in _make_permutations(tail_objs,
                                           length - 1,
                                           src_idx=src_idx + 1,
                                           constraints=constraints,
                                           block_shuffle=block_shuffle,
                                           allow_replacement=allow_replacement):
                yield [head] + tail


def replace_argument(arg: Argument,
                     replacements: Dict[str, str],
                     elim_dneg=False) -> Argument:
    replaced_premises = [replace_formula(formula, replacements, elim_dneg=elim_dneg)
                         for formula in arg.premises]
    replaced_conclusion = replace_formula(arg.conclusion, replacements, elim_dneg=elim_dneg)
    return Argument(replaced_premises,
                    replaced_conclusion,
                    id=arg.id,
                    base_scheme_group=arg.base_scheme_group,
                    scheme_variant=arg.scheme_variant)


def replace_formula(formula: Formula,
                    replacements: Dict[str, str],
                    elim_dneg=False) -> Formula:
    return _expand_op(Formula(replace_rep(formula.rep, replacements, elim_dneg=elim_dneg)))


_expand_op_regexp = re.compile(f'\([^\)]*\)({"|".join([arg for arg in CONSTANTS + VARIABLES])})')


def _expand_op(formula: Formula) -> Formula:
    rep = formula.rep

    while True:
        rep_wo_quantifier = Formula(rep).wo_quantifier.rep

        match = _expand_op_regexp.search(rep_wo_quantifier)
        if match is None:
            break

        op_pred_arg = match.group()
        op_pred, constant = op_pred_arg.lstrip('(').split(')')
        left_pred, op, right_pred = op_pred.split(' ')
        expanded_op_pred_arg = f'({left_pred}{constant} {op} {right_pred}{constant})'
        rep = rep.replace(f'{op_pred_arg}', f'{expanded_op_pred_arg}')

    return Formula(rep)


def replace_rep(rep: str,
                replacements: Dict[str, str],
                elim_dneg=False) -> str:
    replaced = rep

    if len(replacements) >= 1:
        pattern = re.compile("|".join(replacements.keys()))
        replaced = pattern.sub(lambda m: replacements[m.group(0)], rep)

    if elim_dneg:
        replaced = eliminate_double_negation(Formula(replaced)).rep

    return replaced


def formula_is_identical_to(this_formula: Formula,
                            that_formula: Formula,
                            allow_many_to_one_replacements=True,
                            allow_complication=False,
                            elim_dneg=False) -> bool:
    """ Check whether this formula can be the same as that formula by any replacement mapping.

    Note that this and that is not symmetrical, unless allow_many_to_one_replacements=False.
    For example:
        this: {A}{a} -> {B}{b}
        that: {A}{a} -> {A}{a}

        formula_is_identical_to(this, that, allow_many_to_one_replacements=True): True
        formula_is_identical_to(that, this, allow_many_to_one_replacements=True): False

        formula_is_identical_to(this, that, allow_many_to_one_replacements=False): False
        formula_is_identical_to(that, this, allow_many_to_one_replacements=False): False
    """
    if elim_dneg:
        this_formula = eliminate_double_negation(this_formula)
        that_formula = eliminate_double_negation(that_formula)

    if formula_can_not_be_identical_to(this_formula, that_formula, allow_complication=allow_complication, elim_dneg=elim_dneg):
        return False

    for mapping in generate_replacement_mappings_from_formula([this_formula], [that_formula], allow_complication=allow_complication):
        if not allow_many_to_one_replacements and len(set(mapping.values())) < len(mapping):
            continue
        this_replaced = replace_formula(this_formula, mapping)
        if this_replaced.rep == that_formula.rep:
            return True
    return False


def formula_can_not_be_identical_to(this_formula: Formula,
                                    that_formula: Formula,
                                    allow_complication=False,
                                    elim_dneg=False) -> bool:
    """ Decide whether two formulas can not be identical by any mapping. Used for early rejection of is_formula_identical.

    NOTE that False does not mean two formulas are identical.
    """
    if elim_dneg:
        this_formula = eliminate_double_negation(this_formula)
        that_formula = eliminate_double_negation(that_formula)
    if allow_complication:
        # A little costly to implemente since the number of operators change by complication
        raise NotImplementedError()

    return any([this_formula.rep.count(symbol) != that_formula.rep.count(symbol)
                for symbol in [AND, OR, IMPLICATION, NOT]])


def argument_is_identical_to(this_argument: Argument,
                             that_argument: Argument,
                             allow_many_to_one_replacements=True,
                             allow_complication=False,
                             elim_dneg=False) -> bool:

    def _formula_can_not_be_identical_to(this_formula: Formula, that_formula: Formula) -> bool:
        return formula_can_not_be_identical_to(this_formula, that_formula,
                                               allow_complication=allow_complication,
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

    def is_conclusion_same(this_argument: Argument, that_argument: Argument) -> bool:
        return this_argument.conclusion.rep == that_argument.conclusion.rep

    def is_premises_same(this_argument: Argument, that_argument: Argument) -> bool:
        is_premises_same = False
        for that_premises_permutated in permutations(that_argument.premises):
            if all(this_premise.rep == that_premise.rep
                   for this_premise, that_premise, in zip(this_argument.premises, that_premises_permutated)):
                   is_premises_same = True
                   break
        return is_premises_same

    # check the exact identification condition.
    for mapping in generate_replacement_mappings_from_argument(this_argument,
                                                               that_argument,
                                                               allow_complication=allow_complication):
        if not allow_many_to_one_replacements and len(set(mapping.values())) < len(mapping):
            continue

        this_argument_replaced = replace_argument(this_argument, mapping, elim_dneg=elim_dneg)

        if is_conclusion_same(this_argument_replaced, that_argument)\
                and is_premises_same(this_argument_replaced, that_argument):
            return True
        else:
            False

    # It is possible that no mappings are found (e.g. when no predicate and constants are in arguments)
    # but the arguments are the same from the beggining
    if is_conclusion_same(this_argument, that_argument)\
            and is_premises_same(this_argument, that_argument):
        return True

    return False

