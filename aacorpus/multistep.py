import re
from typing import Dict, List, Container, Optional, Any, Iterable, Set
from pprint import pprint
from itertools import combinations_with_replacement

from pydantic import BaseModel


class Formula:

    def __init__(self, formula_str: str):
        # formula_str is like "(x): (${F}x v ${H}x) -> ${G}x"
        self._formula_str = formula_str

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
    def predicates(self) -> Set['Formula']:
        m_iter = re.finditer(r'\${[^}]*}', self._formula_str)
        return set([Formula(m.group()) for m in m_iter
                    if m.group().isupper()])

    @property
    def constants(self) -> Set['Formula']:
        m_iter = re.finditer(r'\${[^}]*}', self._formula_str)
        return set([Formula(m.group()) for m in m_iter
                    if m.group().islower()])

    @property
    def variables(self) -> Set['Formula']:
        variables = []

        # "(x)"
        m_iter = re.finditer(r'\([xyz]*\)', self._formula_str)
        variables += ([Formula(m.group()[1]) for m in m_iter])

        # "(Ex)"
        m_iter = re.finditer(r'\(E[xyz]*\)', self._formula_str)
        variables += ([Formula(m.group()[2]) for m in m_iter])

        return set(variables)


class Scheme(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    id: str
    base_scheme_group: str
    scheme_variant: str
    formulas: List[Formula]
    template_mappings: List[Dict]
    predicate_placeholders: List[str]
    entity_placeholders: List[str]

    @classmethod
    def from_json(cls, json_dict) -> 'Scheme':
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

    def to_json(self) -> Dict:
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


def generate_mappings(src_objs: List[Any],
                      tgt_objs: List[Any]) -> Iterable[Dict[Any, Any]]:
    for chosen_tgt_objs in combinations_with_replacement(tgt_objs, len(src_objs)):
        yield {
            src_obj: tgt_obj
            for src_obj, tgt_obj in zip(src_objs, chosen_tgt_objs)
        }


def main():
    scheme_config = {
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
            "G"
        ],
        "entity-placeholders": [
            "a"
        ]
    }

    scheme = Scheme.from_json(scheme_config)

    for formula in scheme.formulas:
        print('')
        print(f'-- {str(formula)} --')
        print('premise:', formula.premise)
        print('conclusion:', formula.conclusion)
        print('predicates:', formula.predicates)
        print('constants:', formula.constants)
        print('variables:', formula.variables)


if __name__ == '__main__':
    main()
