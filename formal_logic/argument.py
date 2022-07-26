from typing import List, Optional, Dict
import json

from .formula import Formula


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula,
                 id: Optional[str] = None,
                 base_scheme_group: Optional[str] = None,
                 scheme_variant: Optional[str] = None):
        self.premises = premises
        self.conclusion = conclusion

        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant

    def __str__(self) -> str:
        return f'Argument(id="{self.id}", premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises + [self.conclusion]

    @classmethod
    def from_json(cls, json_dict: Dict) -> 'Argument':
        return Argument(
            [Formula(premise_rep) for premise_rep in json_dict['premises']],
            Formula(json_dict['conclusion']),
            id=json_dict['id'],
            base_scheme_group=json_dict['base_scheme_group'],
            scheme_variant=json_dict['scheme_variant'],
        )

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'premises': [premise.rep for premise in self.premises],
            'conclusion': self.conclusion.rep,
        }


def load_config(path: str) -> List[Argument]:
    return [Argument.from_json(obj) for obj in json.load(open(path, 'r'))]
