import re
from typing import Dict, List, Any, Iterable
import copy

from string import Template
from .formula import Formula
from .utils import templatify, detemplatify


def generate_replacements(formula: Formula, other_formula: Formula) -> Iterable[Dict[str, str]]:
    get_pred_replacements = lambda: _generate_replacements(
        [p.rep for p in formula.predicates],
        [p.rep for p in other_formula.predicates],
    )

    get_const_replacements = lambda: _generate_replacements(
        [c.rep for c in formula.constants],
        [c.rep for c in other_formula.constants],
    )

    # done_formula_reps = set()
    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            replacements = copy.deepcopy(pred_replacements)
            replacements.update(const_replacements)

            # replaced_formula_rep = replace(formula, replacements).rep
            # if replaced_formula_rep in done_formula_reps:
            #     continue

            # done_formula_reps.add(replaced_formula_rep)
            yield replacements


def _generate_replacements(src_objs: List[Any],
                           tgt_objs: List[Any]) -> Iterable[Dict[Any, Any]]:
    if len(set(src_objs)) != len(src_objs):
        raise ValueError()
    if len(set(tgt_objs)) != len(tgt_objs):
        raise ValueError()
    for chosen_tgt_objs in _permutations_with_replacement(tgt_objs, len(src_objs)):
        yield {
            src_obj: tgt_obj
            for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
        }


def _permutations_with_replacement(objs: List[Any], length: int) -> Iterable[List[Any]]:
    if length < 1:
        raise ValueError()

    if length == 1:
        for obj in objs:
            yield [obj]
    else:
        for i_head in range(len(objs)):
            for tail in _permutations_with_replacement(objs, length - 1):
                yield [objs[i_head]] + tail


def replace(formula: Formula, replacements: Dict[str, str]) -> Formula:
    template_replacements = {
        detemplatify(src): templatify(tgt) for src, tgt in replacements.items()
    }
    replaced = Template(formula.rep).substitute(template_replacements)
    return Formula(replaced)
