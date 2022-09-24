from typing import List, Optional, Dict, Tuple

from .formula import Formula, PROVE


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula,
                 premise_descendants: Optional[List[Formula]] = None,
                 id: Optional[str] = None,
                 base_scheme_group: Optional[str] = None,
                 scheme_variant: Optional[str] = None):
        self.premises = premises
        self.conclusion = conclusion
        self.premise_descendants = premise_descendants or [None] * len(self.premises)
        if len(self.premise_descendants) != len(self.premises):
            raise ValueError(f'len(self.premise_descendants) {len(self.premise_descendants)} != len(self.premises) {len(self.premises)}')

        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant

    def __str__(self) -> str:
        return f'Argument(id="{self.id}", premise_descendants={str(self.premise_descendants)}, premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises\
            + [self.conclusion]\
            + [premise_descendant
               for premise_descendant in self.premise_descendants
               if premise_descendant is not None]

    @classmethod
    def from_json(cls, json_dict: Dict) -> 'Argument':
        premise_reps = [cls._parse_premise(rep)[0] for rep in json_dict['premises']]
        premise_descendant_reps = [cls._parse_premise(rep)[1] for rep in json_dict['premises']]
        return Argument(
            [Formula(premise_rep) for premise_rep in premise_reps],
            Formula(json_dict['conclusion']),
            premise_descendants=[Formula(premise_descendant_rep) if premise_descendant_rep is not None else None
                               for premise_descendant_rep in premise_descendant_reps],
            id=json_dict['id'],
            base_scheme_group=json_dict.get('base_scheme_group', None),
            scheme_variant=json_dict.get('scheme_variant', None),
        )

    @classmethod
    def _parse_premise(self, rep: str) -> Tuple[str, Optional[str]]:
        if rep.find(f' {PROVE} ') >= 0:
            premise, descendant = rep.split(f' {PROVE} ')
            return (premise, descendant)
        else:
            return rep, None

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'premises': [
                f' {PROVE} '.join([descendant.rep, premise.rep]) if descendant is not None else premise.rep
                for premise, descendant in zip(self.premises, self.premise_descendants)
            ],
            'conclusion': self.conclusion.rep,
        }
