import re
from typing import Dict, List, Any, Iterable
import copy

from string import Template
from .formula import Formula
from .utils import templatify, detemplatify


def generate_replacements(src_formula: Formula,
                          tgt_formula: Formula,
                          allow_negation=True) -> Iterable[Dict[str, str]]:
    src_predicates = [p.rep for p in src_formula.predicates]
    tgt_predicates = [p.rep for p in tgt_formula.predicates]
    if allow_negation:
        tgt_predicates += [Formula(f'¬{p.rep}').rep for p in tgt_formula.predicates]
    get_pred_replacements = lambda: _generate_replacements(
        src_predicates,
        tgt_predicates,
    )

    get_const_replacements = lambda: _generate_replacements(
        [c.rep for c in src_formula.constants],
        [c.rep for c in tgt_formula.constants],
    )

    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            replacements = copy.deepcopy(pred_replacements)
            replacements.update(const_replacements)

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
