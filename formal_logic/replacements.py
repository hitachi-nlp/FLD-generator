import re
import random
from typing import Dict, List, Any, Iterable, Tuple, Optional
import copy

from string import Template
from .formula import Formula, templatify, detemplatify
from .argument import Argument


def generate_replaced_formulas(src_formula: Formula,
                               tgt_formula: Formula,
                               allow_negation=True,
                               constraints: Optional[Dict[str, str]] = None,
                               shuffle=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula([src_formula],
                                                              [tgt_formula],
                                                              allow_negation=allow_negation,
                                                              constraints=constraints,
                                                              shuffle=shuffle):
        yield replace_formula(src_formula, mapping), mapping


def generate_replaced_arguments(src_arg: Argument,
                                tgt_arg: Argument,
                                allow_negation=True,
                                constraints: Optional[Dict[str, str]] = None,
                                shuffle=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula(src_arg.premises + [src_arg.conclusion],
                                                              tgt_arg.premises + [tgt_arg.conclusion],
                                                              allow_negation=allow_negation,
                                                              constraints=constraints,
                                                              shuffle=shuffle):
        yield replace_argument(src_arg, mapping), mapping


def generate_replacement_mappings_from_formula(src_formulas: List[Formula],
                                               tgt_formulas: List[Formula],
                                               allow_negation=True,
                                               constraints: Optional[Dict[str, str]] = None,
                                               shuffle=False) -> Iterable[Dict[str, str]]:
    src_predicates = list(set([p.rep for src_formula in src_formulas for p in src_formula.predicates]))
    tgt_predicates = list(set([p.rep for tgt_formula in tgt_formulas for p in tgt_formula.predicates]))

    src_constants = list(set([c.rep for src_formula in src_formulas for c in src_formula.constants]))
    tgt_constants = list(set([c.rep for tgt_formula in tgt_formulas for c in tgt_formula.constants]))
    yield from generate_replacement_mappings_from_terms(src_predicates, src_constants,
                                                        tgt_predicates, tgt_constants,
                                                        allow_negation=allow_negation,
                                                        constraints=constraints,
                                                        shuffle=shuffle)


def generate_replacement_mappings_from_terms(src_predicates: List[str],
                                             src_constants: List[str],
                                             tgt_predicates: List[str],
                                             tgt_constants: List[str],
                                             allow_negation=True,
                                             constraints: Optional[Dict[str, str]] = None,
                                             shuffle=False) -> Iterable[Dict[str, str]]:
    if allow_negation:
        tgt_predicates += [f'¬{p}' for p in tgt_predicates]

    get_pred_replacements = lambda: generate_replacement_mappings(
        src_predicates,
        tgt_predicates,
        constraints=constraints,
        shuffle=shuffle,
    )

    get_const_replacements = lambda: generate_replacement_mappings(
        src_constants,
        tgt_constants,
        constraints=constraints,
        shuffle=shuffle,
    )

    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            if pred_replacements is None or const_replacements is None:
                continue
            replacements = copy.deepcopy(pred_replacements)
            replacements.update(const_replacements)

            yield replacements


def generate_replacement_mappings(src_objs: List[Any],
                                  tgt_objs: List[Any],
                                  constraints: Optional[Dict[Any, Any]] = None,
                                  shuffle=False) -> Iterable[Optional[Dict[Any, Any]]]:
    if len(set(src_objs)) != len(src_objs):
        raise ValueError()
    if len(set(tgt_objs)) != len(tgt_objs):
        raise ValueError()

    if shuffle:
        src_objs = random.sample(src_objs, len(src_objs))
        tgt_objs = random.sample(tgt_objs, len(tgt_objs))

    if len(src_objs) > 0 and len(tgt_objs) > 0:
        if constraints is not None:
            idx_constraints = {src_objs.index(key): val
                               for key, val in constraints.items()
                               if key in src_objs}
        else:
            idx_constraints = None
        for chosen_tgt_objs in _permutations_with_replacement(tgt_objs,
                                                              len(src_objs),
                                                              constraints=idx_constraints):
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


def _permutations_with_replacement(objs: List[Any],
                                   length: int,
                                   idx=0,
                                   constraints: Optional[Dict[int, Any]] = None) -> Iterable[List[Any]]:
    if length < 1:
        return

    if length == 1:
        if constraints is not None and idx in constraints:
            yield [constraints[idx]]
        else:
            for obj in objs:
                yield [obj]
    else:
        if constraints is not None and idx in constraints:
            heads = [constraints[idx]]
        else:
            heads = objs
        for head in heads:
            for tail in _permutations_with_replacement(objs,
                                                       length - 1,
                                                       idx=idx + 1,
                                                       constraints=constraints):
                yield [head] + tail


def replace_formula(formula: Formula, replacements: Dict[str, str]) -> Formula:
    return Formula(Template(templatify(formula.rep)).substitute(replacements))


def replace_argument(arg: Argument, replacements: Dict[str, str]) -> Argument:
    replaced_premises = [replace_formula(formula, replacements)
                         for formula in arg.premises]
    replaced_conclusion = replace_formula(arg.conclusion, replacements)
    return Argument(replaced_premises,
                    replaced_conclusion,
                    id=arg.id,
                    base_scheme_group=arg.base_scheme_group,
                    scheme_variant=arg.scheme_variant)


def replace_rep(rep: str, replacements: Dict[str, str]) -> str:
    return Template(templatify(rep)).substitute(replacements)
