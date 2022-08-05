import re
import random
from typing import Dict, List, Any, Iterable, Tuple, Optional
import copy

from .formula import Formula, NOT, OR, AND, PREDICATES
from .argument import Argument


def generate_complicated_arguments(src_arg: Argument,
                                   elim_dneg=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_complication_mappings_from_formula(src_arg.premises + [src_arg.conclusion]):
        yield replace_argument(src_arg, mapping, elim_dneg=elim_dneg), mapping


def generate_complicated_formulas(src_formula: Formula,
                                  elim_dneg=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_complication_mappings_from_formula([src_formula]):
        yield replace_formula(src_formula, mapping, elim_dneg=elim_dneg), mapping


def generate_complication_mappings_from_formula(formulas: List[Formula]) -> Iterable[Dict[str, str]]:
    predicates = sorted(set([p.rep for formula in formulas for p in formula.predicates]))
    constants = sorted(set([p.rep for formula in formulas for p in formula.constants]))

    identity_mapping = {pred: pred for pred in predicates}
    identity_mapping.update({const: const for const in constants})
    # yield identity_mapping

    unknown_predicates = list(set(PREDICATES) - set(predicates))
    unk_pred0 = unknown_predicates[0]
    unk_pred1 = unknown_predicates[1]

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
        for predicates_with_not in not_enhance(predicates):
            mapping = copy.deepcopy(identity_mapping)
            for predicate_with_not in predicates_with_not:
                original_predicate = predicate_with_not.lstrip(f'{NOT}')
                mapping[original_predicate] = predicate_with_not
            yield mapping

    for mapping in generate_not_enhanced_mappings(predicates):
        yield mapping

    for expand_op in [OR, AND]:
        for i_predicate_to_expand, predicate_to_expand in enumerate(predicates):
            unk_extended_predicates = [unk_pred0, unk_pred1]\
                + predicates[:i_predicate_to_expand]\
                + predicates[i_predicate_to_expand + 1:]

            for not_enhanced_mapping in generate_not_enhanced_mappings(unk_extended_predicates):
                mapping = copy.deepcopy(not_enhanced_mapping)
                mapping[predicate_to_expand] = f'({not_enhanced_mapping[unk_pred0]} {expand_op} {not_enhanced_mapping[unk_pred1]})'
                yield mapping


def generate_replaced_arguments(src_arg: Argument,
                                tgt_arg: Argument,
                                allow_complication=False,
                                constraints: Optional[Dict[str, str]] = None,
                                block_shuffle=False,
                                elim_dneg=False) -> Iterable[Tuple[Argument, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula(src_arg.premises + [src_arg.conclusion],
                                                              tgt_arg.premises + [tgt_arg.conclusion],
                                                              allow_complication=allow_complication,
                                                              constraints=constraints,
                                                              block_shuffle=block_shuffle):
        yield replace_argument(src_arg, mapping, elim_dneg=elim_dneg), mapping


def generate_replaced_formulas(src_formula: Formula,
                               tgt_formula: Formula,
                               allow_complication=False,
                               constraints: Optional[Dict[str, str]] = None,
                               block_shuffle=False,
                               elim_dneg=False) -> Iterable[Tuple[Formula, Dict[str, str]]]:
    for mapping in generate_replacement_mappings_from_formula([src_formula],
                                                              [tgt_formula],
                                                              allow_complication=allow_complication,
                                                              constraints=constraints,
                                                              block_shuffle=block_shuffle):
        yield replace_formula(src_formula, mapping, elim_dneg=elim_dneg), mapping


def generate_replacement_mappings_from_formula(src_formulas: List[Formula],
                                               tgt_formulas: List[Formula],
                                               allow_complication=False,
                                               constraints: Optional[Dict[str, str]] = None,
                                               block_shuffle=False) -> Iterable[Dict[str, str]]:
    if allow_complication:
        complication_mappings = generate_complication_mappings_from_formula(src_formulas)
    else:
        complication_mappings = [
            {p.rep: p.rep for formula in src_formulas for p in formula.predicates}  # identity mapping
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
                                                            block_shuffle=block_shuffle)


def generate_replacement_mappings_from_terms(src_predicates: List[str],
                                             src_constants: List[str],
                                             tgt_predicates: List[str],
                                             tgt_constants: List[str],
                                             constraints: Optional[Dict[str, str]] = None,
                                             block_shuffle=False) -> Iterable[Dict[str, str]]:
    get_pred_replacements = lambda: _generate_replacement_mappings(
        src_predicates,
        tgt_predicates,
        constraints=constraints,
        block_shuffle=block_shuffle,
    )

    get_const_replacements = lambda: _generate_replacement_mappings(
        src_constants,
        tgt_constants,
        constraints=constraints,
        block_shuffle=block_shuffle,
    )

    for pred_replacements in get_pred_replacements():
        for const_replacements in get_const_replacements():
            if pred_replacements is None or const_replacements is None:
                continue
            replacements = copy.deepcopy(pred_replacements)
            replacements.update(const_replacements)

            yield replacements


def _generate_replacement_mappings(src_objs: List[Any],
                                   tgt_objs: List[Any],
                                   constraints: Optional[Dict[Any, Any]] = None,
                                   block_shuffle=False) -> Iterable[Optional[Dict[Any, Any]]]:
    if len(set(src_objs)) != len(src_objs):
        raise ValueError()
    if len(set(tgt_objs)) != len(tgt_objs):
        raise ValueError()

    # if block_shuffle:
    #     src_objs = random.sample(src_objs, len(src_objs))
    #     tgt_objs = random.sample(tgt_objs, len(tgt_objs))

    if len(src_objs) > 0 and len(tgt_objs) > 0:
        if constraints is not None:
            idx_constraints = {src_objs.index(key): val
                               for key, val in constraints.items()
                               if key in src_objs}
        else:
            idx_constraints = None
        for chosen_tgt_objs in _permutations_with_replacement(tgt_objs,
                                                              len(src_objs),
                                                              constraints=idx_constraints,
                                                              block_shuffle=block_shuffle):
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
                                   src_idx=0,
                                   constraints: Optional[Dict[int, Any]] = None,
                                   block_shuffle=False) -> Iterable[List[Any]]:
    """

    block_shuffle=Trueであって，完全にblock_shuffleできるわけではない．
    for head in heads: のループにおいて，headごとにブロック化しているため．
    しかし，ここをblock_shuffleしようとすると，generatorではなくlistを作る必要があり，速度が落ちる．
    """
    if length < 1:
        return
    if block_shuffle:
        objs = random.sample(objs, len(objs))

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
            for tail in _permutations_with_replacement(objs,
                                                       length - 1,
                                                       src_idx=src_idx + 1,
                                                       constraints=constraints,
                                                       block_shuffle=block_shuffle):
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
    return Formula(replace_rep(formula.rep, replacements, elim_dneg=elim_dneg))


def replace_rep(rep: str,
                replacements: Dict[str, str],
                elim_dneg=False) -> str:
    replaced = rep

    if len(replacements) >= 1:
        pattern = re.compile("|".join(replacements.keys()))
        replaced = pattern.sub(lambda m: replacements[m.group(0)], rep)

    if elim_dneg:
        replaced = re.sub(f'{NOT}{NOT}', '', replaced)

    return replaced


def is_formula_identical(this: Formula,
                         that: Formula,
                         allow_complication=False,
                         elim_dneg=False) -> bool:
    return any([
        this.rep == that_replaced.rep
        for that_replaced, _ in generate_replaced_formulas(that,
                                                           this,
                                                           allow_complication=allow_complication,
                                                           elim_dneg=elim_dneg)
    ])


def is_argument_identical(this: Argument,
                          that: Argument,
                          allow_complication=False,
                          elim_dneg=False) -> bool:
    raise NotImplementedError()
