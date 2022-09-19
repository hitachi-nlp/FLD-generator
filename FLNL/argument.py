from typing import List, Optional, Dict, Tuple

from .formula import Formula, PROVE


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula,
                 premise_ancestors: Optional[List[Formula]] = None,
                 id: Optional[str] = None,
                 base_scheme_group: Optional[str] = None,
                 scheme_variant: Optional[str] = None):
        self.premises = premises
        self.conclusion = conclusion
        self.premise_ancestors = premise_ancestors or [None] * len(self.premises)
        if len(self.premise_ancestors) != len(self.premises):
            raise ValueError(f'len(self.premise_ancestors) {len(self.premise_ancestors)} != len(self.premises) {len(self.premises)}')

        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant

    def __str__(self) -> str:
        return f'Argument(id="{self.id}", premise_ancestors={str(self.premise_ancestors)}, premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises\
            + [self.conclusion]\
            + [premise_ancestor
               for premise_ancestor in self.premise_ancestors
               if premise_ancestor is not None]

    @classmethod
    def from_json(cls, json_dict: Dict) -> 'Argument':
        premise_reps = [cls._parse_premise(rep)[0] for rep in json_dict['premises']]
        premise_ancestor_reps = [cls._parse_premise(rep)[1] for rep in json_dict['premises']]
        return Argument(
            [Formula(premise_rep) for premise_rep in premise_reps],
            Formula(json_dict['conclusion']),
            premise_ancestors=[Formula(premise_ancestor_rep) if premise_ancestor_rep is not None else None
                               for premise_ancestor_rep in premise_ancestor_reps],
            id=json_dict['id'],
            base_scheme_group=json_dict.get('base_scheme_group', None),
            scheme_variant=json_dict.get('scheme_variant', None),
        )

    @classmethod
    def _parse_premise(self, rep: str) -> Tuple[str, Optional[str]]:
        if rep.find(f' {PROVE} ') >= 0:
            premise, ancestor = rep.split(f' {PROVE} ')
            return (premise, ancestor)
        else:
            return rep, None

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'premises': [
                f' {PROVE} '.join([ancestor.rep, premise.rep]) if ancestor is not None else premise.rep
                for premise, ancestor in zip(self.premises, self.premise_ancestors)
            ],
            'conclusion': self.conclusion.rep,
        }
