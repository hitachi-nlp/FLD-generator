from typing import List, Optional, Dict, Tuple

from .formula import Formula, DERIVE


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula,
                 assumptions: Dict[Formula, Formula],
                 id: Optional[str] = None,
                 base_scheme_group: Optional[str] = None,
                 scheme_variant: Optional[str] = None):
        self.premises = premises
        self.conclusion = conclusion
        self.assumptions = assumptions

        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant

    def __str__(self) -> str:
        return f'Argument(id="{self.id}", assumptions={str(self.assumptions)}, premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises\
            + [self.assumptions[premise] for premise in self.premises
               if premise in self.assumptions]\
            + [self.conclusion]

    @classmethod
    def from_json(cls, json_dict: Dict) -> 'Argument':
        premise_reps = [cls._parse_premise(rep)[0] for rep in json_dict['premises']]
        assumption_reps = [cls._parse_premise(rep)[1] for rep in json_dict['premises']]

        premises = [Formula(rep) for rep in premise_reps]
        assumptions = [(Formula(rep) if rep is not None else None) for rep in assumption_reps]
        return Argument(
            premises,
            Formula(json_dict['conclusion']),
            {premise: assumption for premise, assumption in zip(premises, assumptions)
             if assumption is not None},
            id=json_dict['id'],
            base_scheme_group=json_dict.get('base_scheme_group', None),
            scheme_variant=json_dict.get('scheme_variant', None),
        )

    @classmethod
    def _parse_premise(self, rep: str) -> Tuple[str, Optional[str]]:
        if rep.find(f' {DERIVE} ') >= 0:
            assumption, premise = rep.split(f' {DERIVE} ')
            return (premise, assumption)
        else:
            return rep, None

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'premises': [
                (premise.rep if premise not in self.assumptions else f'{premise.rep} {DERIVE} {self.assumptions[premise].rep}')
                for premise in self.premises
            ],
            'conclusion': self.conclusion.rep,
        }
