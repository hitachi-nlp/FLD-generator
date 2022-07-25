import re
from typing import Dict, List, Any, Iterable, Tuple, Optional
import copy

from string import Template
from .formula import Formula, Argument
from .formula import templatify, detemplatify


def generate_replaced_formulas(src_formula: Formula,
                               tgt_formula: Formula,
                               allow_negation=True) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula([src_formula],
                                                              [tgt_formula],
                                                              allow_negation=allow_negation):
        yield replace_formula(src_formula, mapping), mapping


def generate_replaced_arguments(src_arg: Argument,
                                tgt_arg: Argument,
                                allow_negation=True) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula(src_arg.premises + [src_arg.conclusion],
                                                              tgt_arg.premises + [tgt_arg.conclusion],
                                                              allow_negation=allow_negation):
        yield replace_argument(src_arg, mapping), mapping


def replace_formula(formula: Formula, replacements: Dict[str, str]) -> Formula:
    return Formula(Template(templatify(formula.rep)).substitute(replacements))


def replace_argument(arg: Argument, replacements: Dict[str, str]) -> Argument:
    replaced_premises = [replace_formula(formula, replacements)
                         for formula in arg.premises]
    replaced_conclusion = replace_formula(arg.conclusion, replacements)
    return Argument(replaced_premises, replaced_conclusion)


def replace_rep(rep: str, replacements: Dict[str, str]) -> str:
    return Template(templatify(rep)).substitute(replacements)


def generate_replacement_mappings_from_formula(src_formulas: List[Formula],
                                               tgt_formulas: List[Formula],
                                               allow_negation=True) -> Iterable[Dict[str, str]]:
    src_predicates = list(set([p.rep for src_formula in src_formulas for p in src_formula.predicates]))
    tgt_predicates = list(set([p.rep for tgt_formula in tgt_formulas for p in tgt_formula.predicates]))

    src_constants = list(set([c.rep for src_formula in src_formulas for c in src_formula.constants]))
    tgt_constants = list(set([c.rep for tgt_formula in tgt_formulas for c in tgt_formula.constants]))
    yield from generate_replacement_mappings_from_terms(src_predicates, src_constants,
                                                        tgt_predicates, tgt_constants,
                                                        allow_negation=allow_negation)


def generate_replacement_mappings_from_terms(src_predicates: List[str],
                                             src_constants: List[str],
                                             tgt_predicates: List[str],
                                             tgt_constants: List[str],
                                             allow_negation=True) -> Iterable[Dict[str, str]]:
    if allow_negation:
        tgt_predicates += [f'¬{p}' for p in tgt_predicates]

    get_pred_replacements = lambda: generate_replacement_mappings(
        src_predicates,
        tgt_predicates,
    )

    get_const_replacements = lambda: generate_replacement_mappings(
        src_constants,
        tgt_constants,
    )

    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            if pred_replacements is None or const_replacements is None:
                continue
            replacements = copy.deepcopy(pred_replacements)
            replacements.update(const_replacements)

            yield replacements


def generate_replacement_mappings(src_objs: List[Any],
                                  tgt_objs: List[Any]) -> Iterable[Optional[Dict[Any, Any]]]:
    if len(set(src_objs)) != len(src_objs):
        raise ValueError()
    if len(set(tgt_objs)) != len(tgt_objs):
        raise ValueError()

    if len(src_objs) > 0 and len(tgt_objs) > 0:
        for chosen_tgt_objs in _permutations_with_replacement(tgt_objs, len(src_objs)):
            yield {
                src_obj: tgt_obj
                for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
            }
    elif len(src_objs) == 0 and len(tgt_objs) == 0:
        yield {}
    else:
        yield None


def _permutations_with_replacement(objs: List[Any], length: int) -> Iterable[List[Any]]:
    if length < 1:
        return

    if length == 1:
        for obj in objs:
            yield [obj]
    else:
        for i_head in range(len(objs)):
            for tail in _permutations_with_replacement(objs, length - 1):
                yield [objs[i_head]] + tail
