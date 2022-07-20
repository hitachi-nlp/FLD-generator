import re
from typing import Dict, List, Container, Optional, Any, Iterable, Set
from pprint import pprint
from itertools import combinations_with_replacement
import copy

from string import Template


class Formula:

    def __init__(self, formula_str: str):
        # formula_str is like "(x): (${F}x v ${H}x) -> ${G}x"
        self._formula_str = formula_str

    @property
    def rep(self) -> str:
        return self._formula_str

    def __str__(self) -> str:
        # only for printing
        return f'Formula("{self._formula_str}")'

    def __repr__(self) -> str:
        # only for printing
        return f'Formula("{self._formula_str}")'

    @property
    def premise(self) -> Optional['Formula']:
        if self._formula_str.find('->') < 0:
            return None
        return Formula(' -> '.join(self._formula_str.split(' -> ')[:-1]))

    @property
    def conclusion(self) -> Optional['Formula']:
        if self._formula_str.find('->') < 0:
            return None
        return Formula(self._formula_str.split(' -> ')[-1])

    @property
    def predicates(self) -> List['Formula']:
        matches = re.finditer(r'\${[^}]*}', self._formula_str)
        unique_preds = set(
            [m.group() for m in matches
             if m.group().isupper()]
        )
        return [Formula(rep)
                for rep in sorted(unique_preds)]

    @property
    def constants(self) -> List['Formula']:
        matches = re.finditer(r'\${[^}]*}', self._formula_str)
        unique_constants = set([m.group() for m in matches
                                if m.group().islower()])

        return [Formula(rep)
                for rep in sorted(unique_constants)]

    @property
    def variables(self) -> List['Formula']:
        unique_variables = set()

        # "(x)"
        matches = re.finditer(r'\([xyz]*\)', self._formula_str)
        unique_variables = unique_variables.union(
            set([m.group()[1] for m in matches])
        )

        # "(Ex)"
        matches = re.finditer(r'\(E[xyz]*\)', self._formula_str)
        unique_variables = unique_variables.union(
            set([m.group()[2] for m in matches])
        )

        return [Formula(rep)
                for rep in sorted(unique_variables)]


class Scheme:

    def __init__(
        self,
        id: str,
        base_scheme_group: str,
        scheme_variant: str,
        formulas: List[Formula],
        template_mappings: List[Dict],
        predicate_placeholders: List[str],
        entity_placeholders: List[str],
    ):
        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant
        self.formulas = formulas
        self.template_mappings = template_mappings
        self.predicate_placeholders = predicate_placeholders
        self.entity_placeholders = entity_placeholders

    @classmethod
    def parse_obj(cls, json_dict) -> 'Scheme':
        json_dict['predicate_placeholders'] = json_dict['predicate-placeholders']
        json_dict.pop('predicate-placeholders', None)

        json_dict['entity_placeholders'] = json_dict['entity-placeholders']
        json_dict.pop('entity-placeholders', None)

        json_dict['formulas'] = [
            Formula(formula_str)
            for formula_str, _ in json_dict['scheme']
        ]
        json_dict['template_mappings'] = [
            mapping
            for _, mapping in json_dict['scheme']
        ]
        json_dict.pop('scheme', None)

        return cls(**json_dict)

    def dict(self) -> Dict:
        json_dict = {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'predicate-placeholders': self.predicate_placeholders,
            'entity-placeholders': self.entity_placeholders,
        }
        json_dict['scheme'] = [
            [formula.rep, mapping]
            for formula, mapping in zip(self.formulas, self.template_mappings)
        ]
        return json_dict


def templatify(rep: str) -> str:
    if rep.startswith('${'):
        return rep
    else:
        return '${' + rep + '}'


def detemplatify(rep: str) -> str:
    if rep.startswith('${'):
        return rep[2:-1]
    else:
        return rep


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
    for chosen_tgt_objs in permutations_with_replacement(tgt_objs, len(src_objs)):
        yield {
            src_obj: tgt_obj
            for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
        }


def permutations_with_replacement(objs: List[Any], length: int) -> Iterable[List[Any]]:
    if length < 1:
        raise ValueError()

    if length == 1:
        for obj in objs:
            yield [obj]
    else:
        for i_head in range(len(objs)):
            for tail in permutations_with_replacement(objs, length - 1):
                yield [objs[i_head]] + tail


def replace(formula: Formula, replacements: Dict[str, str]) -> Formula:
    template_replacements = {
        detemplatify(src): templatify(tgt) for src, tgt in replacements.items()
    }
    replaced = Template(formula.rep).substitute(template_replacements)
    return Formula(replaced)


def main():
    mb_scheme_config = {
        "id": "mb0",
        "base_scheme_group": "Modus barbara",
        "scheme_variant": "base_scheme",
        "scheme": [
            [
                "(x): ${F}x -> ${G}x",
                {
                    "F": "A",
                    "G": "B"
                }
            ],
            [
                "${F}${a}",
                {
                    "F": "A",
                    "a": "a"
                }
            ],
            [
                "${G}${a}",
                {
                    "G": "A",
                    "a": "a"
                }
            ]
        ],
        "predicate-placeholders": [
            "F",
            "G",
        ],
        "entity-placeholders": [
            "a",
        ]
    }

    # mb_scheme = Scheme.parse_obj(mb_scheme_config)

    # for formula in mb_scheme.formulas:
    #     print('')
    #     print(f'-- {str(formula)} --')
    #     print('premise:', formula.premise)
    #     print('conclusion:', formula.conclusion)
    #     print('predicates:', formula.predicates)
    #     print('constants:', formula.constants)
    #     print('variables:', formula.variables)

    formula = Formula('(x): ${F}x ${G}${a} ${G}${b} -> ${H}x')
    other_formula = Formula('(y): ${F}y ${I}${a} ${J}${b} -> ${K}y')

    print('-------------------- placeholders --------------------')
    print('formula                          :', formula)
    print('formula placeholders             :', formula.predicates + formula.constants)

    print('other_formula                    :', other_formula)
    print('other_formula placeholders       :', other_formula.predicates + other_formula.constants)

    print('-------------------- replacements --------------------')
    for replacements in generate_replacements(formula, other_formula):
        print('')
        print('replacements     :', replacements)
        print('replaced formula :', replace(formula, replacements))

    assert(len(formula.predicates) == 3)
    assert(len(formula.constants) == 2)

    assert(len(other_formula.predicates) == 4)
    assert(len(other_formula.constants) == 2)

    assert(len(list(generate_replacements(formula, other_formula))) == 4**3 * 2**2)


if __name__ == '__main__':
    main()
