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
                                   suppress_op_expansion_if_exists=False,
                                   get_name=False) -> Union[Iterable[Tuple[Argument, Dict[str, str]]], Iterable[Tuple[Argument, Dict[str, str], str]]]:
    for mapping, name in generate_complication_mappings_from_formula(src_arg.premises + [src_arg.conclusion] + [ancestor for ancestor in src_arg.premise_ancestors if ancestor is not None],
                                                                     suppress_op_expansion_if_exists=suppress_op_expansion_if_exists,
                                                                     get_name=True):
        complicated_argument = interprete_argument(src_arg, mapping, elim_dneg=elim_dneg)
        if get_name:
            yield complicated_argument, mapping, name
        else:
            yield complicated_argument, mapping


def generate_complicated_formulas(src_formula: Formula,
                                  elim_dneg=False,
                                  suppress_op_expansion_if_exists=False,
                                  get_name=False) -> Union[Iterable[Tuple[Formula, Dict[str, str]]], Iterable[Tuple[Formula, Dict[str, str], str]]]:
    for mapping, name in generate_complication_mappings_from_formula([src_formula],
                                                                     suppress_op_expansion_if_exists=suppress_op_expansion_if_exists,
                                                                     get_name=True):
        complicated_formula = interprete_formula(src_formula, mapping, elim_dneg=elim_dneg)
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

    def filled_str(no: int) -> str:
        return str(no).zfill(6)

    for i_not, mapping in enumerate(generate_not_enhanced_mappings(predicates)):
        if get_name:
            yield mapping, f'not-{filled_str(i_not)}'
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
                    for brace_not_prefix in ['', NOT]:
                        mapping[predicate_to_expand] = f'{brace_not_prefix}({not_enhanced_mapping[unk_pred0]} {op} {not_enhanced_mapping[unk_pred1]})'
                        if get_name:
                            yield mapping, f'{op}-{filled_str(i_predicate_to_expand)}.not-{filled_str(i_not)}'
                        else:
                            yield mapping


def generate_arguments_in_target_space(src_arg: Argument,
                                       tgt_arg: Argument,
                                       add_complicated_arguments=False,
                                       constraints: Optional[Dict[str, str]] = None,
                                       block_shuffle=False,
                                       allow_many_to_one=True,
                                       elim_dneg=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_mappings_from_formula(src_arg.premises + [src_arg.conclusion] + [ancestor for ancestor in src_arg.premise_ancestors if ancestor is not None],
                                                  tgt_arg.premises + [tgt_arg.conclusion] + [ancestor for ancestor in src_arg.premise_ancestors if ancestor is not None],
                                                  add_complicated_arguments=add_complicated_arguments,
                                                  constraints=constraints,
                                                  block_shuffle=block_shuffle,
                                                  allow_many_to_one=allow_many_to_one):
        yield interprete_argument(src_arg, mapping, elim_dneg=elim_dneg), mapping


def generate_formulas_in_target_space(src_formula: Formula,
                                      tgt_formula: Formula,
                                      add_complicated_arguments=False,
                                      constraints: Optional[Dict[str, str]] = None,
                                      block_shuffle=False,
                                      allow_many_to_one=True,
                                      elim_dneg=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_mappings_from_formula([src_formula],
                                                  [tgt_formula],
                                                  add_complicated_arguments=add_complicated_arguments,
                                                  constraints=constraints,
                                                  block_shuffle=block_shuffle,
                                                  allow_many_to_one=allow_many_to_one):
        yield interprete_formula(src_formula, mapping, elim_dneg=elim_dneg), mapping


@profile
def generate_mappings_from_argument(src_argument: Argument,
                                    tgt_argument: Argument,
                                    add_complicated_arguments=False,
                                    constraints: Optional[Dict[str, str]] = None,
                                    block_shuffle=False,
                                    allow_many_to_one=True) -> Iterable[Dict[str, str]]:
    yield from generate_mappings_from_formula(
        src_argument.all_formulas,
        tgt_argument.all_formulas,
        add_complicated_arguments=add_complicated_arguments,
        constraints=constraints,
        block_shuffle=block_shuffle,
        allow_many_to_one=allow_many_to_one,
    )


@profile
def generate_mappings_from_formula(src_formulas: List[Formula],
                                   tgt_formulas: List[Formula],
                                   add_complicated_arguments=False,
                                   constraints: Optional[Dict[str, str]] = None,
                                   block_shuffle=False,
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
        complicated_formulas = [interprete_formula(formula, complication_mapping)
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
                                                                   block_shuffle=block_shuffle,
                                                                   allow_many_to_one=allow_many_to_one)


@profile
def generate_mappings_from_predicates_and_constants(src_predicates: List[str],
                                                    src_constants: List[str],
                                                    tgt_predicates: List[str],
                                                    tgt_constants: List[str],
                                                    constraints: Optional[Dict[str, str]] = None,
                                                    block_shuffle=False,
                                                    allow_many_to_one=True) -> Iterable[Dict[str, str]]:
    if len(src_predicates) == 0 or len(tgt_predicates) == 0:
        # identity mapping for formulas that do not have predicates.
        get_pred_mappings = lambda : [{}]
    else:
        get_pred_mappings = lambda: _generate_mappings(
            src_predicates,
            tgt_predicates,
            constraints=constraints,
            block_shuffle=block_shuffle,
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
            block_shuffle=block_shuffle,
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
                       block_shuffle=False,
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
                                                  block_shuffle=block_shuffle,
                                                  allow_many_to_one=allow_many_to_one):
            yield {
                src_obj: tgt_obj
                for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
            }
    # elif len(src_objs) == 0 and len(tgt_objs) == 0:
    #     yield {}
    # elif len(src_objs) == 0 and len(tgt_objs) > 0:
    #     yield {}
    # else:
    #     yield None
    else:
        raise ValueError()


@profile
def _make_permutations(objs: List[Any],
                       length: int,
                       src_idx=0,
                       constraints: Optional[Dict[int, Any]] = None,
                       block_shuffle=False,
                       allow_many_to_one=True) -> Iterable[List[Any]]:
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
            if allow_many_to_one:
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
                                           allow_many_to_one=allow_many_to_one):
                yield [head] + tail


def interprete_argument(arg: Argument,
                        mapping: Dict[str, str],
                        elim_dneg=False) -> Argument:
    interpreted_premises = [interprete_formula(formula, mapping, elim_dneg=elim_dneg)
                            for formula in arg.premises]
    interpreted_premise_ancestors = [interprete_formula(ancestor, mapping, elim_dneg=elim_dneg) if ancestor is not None else None
                                     for ancestor in arg.premise_ancestors]
    interpreted_conclusion = interprete_formula(arg.conclusion, mapping, elim_dneg=elim_dneg)
    return Argument(interpreted_premises,
                    interpreted_conclusion,
                    premise_ancestors=interpreted_premise_ancestors,
                    id=arg.id,
                    base_scheme_group=arg.base_scheme_group,
                    scheme_variant=arg.scheme_variant)


@profile
def interprete_formula(formula: Formula,
                       mapping: Dict[str, str],
                       elim_dneg=False) -> Formula:
    return _expand_op(
        Formula(
            _interprete_rep(formula.rep, mapping, elim_dneg=elim_dneg)
        )
    )


_expand_op_regexp = re.compile(f'\([^\)]*\)({"|".join([arg for arg in CONSTANTS + VARIABLES])})')


@profile
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
def _interprete_rep(rep: str,
                    mapping: Dict[str, str],
                    elim_dneg=False) -> str:
    interpreted_rep = rep

    if len(mapping) >= 1:
        pattern = re.compile("|".join(mapping.keys()))
        interpreted_rep = pattern.sub(lambda m: mapping[m.group(0)], rep)

    if elim_dneg:
        interpreted_rep = eliminate_double_negation(Formula(interpreted_rep)).rep

    return interpreted_rep


@profile
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
        this_interpreted = interprete_formula(this_formula, mapping, elim_dneg=elim_dneg)
        if this_interpreted.rep == that_formula.rep:
            return True
    return False


@profile
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
            for symbol in [AND, OR, IMPLICATION, NOT]]):
        return True

    return False


@profile
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
    for this_premise_ancestor in this_argument.premise_ancestors:
        if all(
            ((this_premise_ancestor is None) != (that_premise_ancestor is None))
            or (this_premise_ancestor is not None and _formula_can_not_be_identical_to(this_premise_ancestor, that_premise_ancestor))
                for that_premise_ancestor in that_argument.premise_ancestors):
            return False

    def is_conclusion_same(this_argument: Argument, that_argument: Argument) -> bool:
        return this_argument.conclusion.rep == that_argument.conclusion.rep

    def is_premises_same(this_argument: Argument, that_argument: Argument) -> bool:
        _is_premises_same = False
        for premise_indexes in permutations(range(len(that_argument.premises))):
            that_premises_permuted = [that_argument.premises[i] for i in premise_indexes]
            that_premise_ancestor_permuted = [that_argument.premise_ancestors[i] for i in premise_indexes]
        # for that_premises_permuted, that_premise_ancestor_permuted in permutations(zip(that_argument.premises, that_argument.premise_ancestors)):
            if all(this_premise.rep == that_premise.rep
                   or (this_premise_ancestor is None and that_premise_ancestor is None)
                   or (this_premise_ancestor is not None and that_premise_ancestor is not None and this_premise_ancestor.rep == that_premise_ancestor.rep)
                   for this_premise, this_premise_ancestor, that_premise, that_premise_ancestor, in zip(this_argument.premises, this_argument.premise_ancestors, that_premises_permuted, that_premise_ancestor_permuted)):
                _is_premises_same = True
                break
        return _is_premises_same

    # check the exact identification condition.
    for mapping in generate_mappings_from_argument(this_argument,
                                                   that_argument,
                                                   add_complicated_arguments=add_complicated_arguments,
                                                   allow_many_to_one=allow_many_to_oneg):
        this_argument_interpreted = interprete_argument(this_argument, mapping, elim_dneg=elim_dneg)

        if is_conclusion_same(this_argument_interpreted, that_argument)\
                and is_premises_same(this_argument_interpreted, that_argument):
            return True
        else:
            False

    # It is possible that no mappings are found (e.g. when no predicate and constants are in arguments)
    # but the arguments are the same from the beggining
    if is_conclusion_same(this_argument, that_argument)\
            and is_premises_same(this_argument, that_argument):
        return True

    return False


def generate_quantifier_arguments(
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

    quantified_variable = sorted(set(VARIABLES) - {v.rep for v in formula.variables})[0]
    de_quantified_constant = sorted(set(CONSTANTS) - {c.rep for c in formula.constants})[0]

    def generate_quantifier_mappings(constants: List[Formula]) -> Iterable[Dict]:
        if len(constants) == 0:
            yield {}
            return

        src_constant = constants[0]
        tgt_constant_reps = [quantified_variable] if quantify_all_at_once else [src_constant.rep, quantified_variable]
        for tgt_constant_rep in tgt_constant_reps:
            for mapping in generate_quantifier_mappings(constants[1:]):
                mapping[src_constant.rep] = tgt_constant_rep
                yield mapping

    for i, quantifier_mapping in enumerate(generate_quantifier_mappings(formula.constants)):
        if quantified_variable not in quantifier_mapping.values():
            continue
        de_quantified_mapping = {src: (de_quantified_constant if tgt == quantified_variable else src)
                                 for src, tgt in quantifier_mapping.items()}

        if argument_type == 'universal_quantifier_elim':
            quantified_formula = Formula(f'({quantified_variable}): ' + interprete_formula(formula, quantifier_mapping).rep)
            de_quantified_formula = interprete_formula(formula, de_quantified_mapping)
            argument_id = f'{id_prefix}.univ_quant_elim-{i}' if id_prefix is not None else f'univ_quant_elim-{i}'
            argument = Argument(
                [quantified_formula],
                de_quantified_formula,
                id = argument_id,
            )
        elif argument_type == 'existential_quantifier_intro':
            quantified_formula = Formula(f'(E{quantified_variable}): ' + interprete_formula(formula, quantifier_mapping).rep)
            de_quantified_formula = interprete_formula(formula, de_quantified_mapping)
            argument_id = f'{id_prefix}.exist_quant_intro-{i}' if id_prefix is not None else f'exist_quant_intro-{i}'
            argument = Argument(
                [de_quantified_formula],
                quantified_formula,
                id = argument_id,
            )
        else:
            raise ValueError()

        yield argument
