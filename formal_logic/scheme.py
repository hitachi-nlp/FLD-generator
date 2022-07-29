from typing import Dict, List

from formal_logic import Formula


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
