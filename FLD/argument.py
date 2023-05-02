from typing import List, Optional, Dict, Tuple, List

from .formula import Formula, DERIVE


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula,
                 assumptions: Dict[Formula, Formula],
                 intermediate_constants: Optional[List[Formula]] = None,
                 id: Optional[str] = None,
                 base_scheme_group: Optional[str] = None,
                 scheme_variant: Optional[str] = None):
        self.premises = premises
        self.conclusion = conclusion
        self.assumptions = assumptions

        if intermediate_constants is not None:
            for constant in intermediate_constants:
                if constant.rep != constant.constants[0].rep:
                    raise ValueError(f'The intermediate formula {constant.rep} must be a single constant')
            self.intermediate_constants = intermediate_constants
        else:
            self.intermediate_constants = []

        self.id = id
        self.base_scheme_group = base_scheme_group
        self.scheme_variant = scheme_variant

    def __str__(self) -> str:
        return f'Argument(id="{self.id}", assumptions={str(self.assumptions)}, premises={str(self.premises)}, conclusion={str(self.conclusion)}, intermediate_constants={str(self.intermediate_constants)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises\
            + [self.assumptions[premise] for premise in self.premises
               if premise in self.assumptions]\
            + self.intermediate_constants\
            + [self.conclusion]

    @classmethod
    def from_json(cls, json_dict: Dict) -> 'Argument':
        assumption_reps = [cls._parse_premise(rep)[0] for rep in json_dict['premises']]
        premise_reps = [cls._parse_premise(rep)[1] for rep in json_dict['premises']]

        assumptions = [(Formula(rep) if rep is not None else None) for rep in assumption_reps]
        premises = [Formula(rep) for rep in premise_reps]
        intermediate_constants = [Formula(rep) for rep in json_dict.get('intermediate', [])]
        return Argument(
            premises,
            Formula(json_dict['conclusion']),
            {premise: assumption for premise, assumption in zip(premises, assumptions)
             if assumption is not None},
            intermediate_constants=intermediate_constants,
            id=json_dict['id'],
            base_scheme_group=json_dict.get('base_scheme_group', None),
            scheme_variant=json_dict.get('scheme_variant', None),
        )

    @classmethod
    def _parse_premise(self, rep: str) -> Tuple[Optional[str], str]:
        if rep.find(f' {DERIVE} ') >= 0:
            assumption, premise = rep.split(f' {DERIVE} ')
            return (assumption, premise)
        else:
            return None, rep

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'base_scheme_group': self.base_scheme_group,
            'scheme_variant': self.scheme_variant,
            'intermediate': [constant.rep for constant in self.intermediate_constants],
            'premises': [
                (premise.rep if premise not in self.assumptions else f'{self.assumptions[premise].rep} {DERIVE} {premise.rep}')
                for premise in self.premises
            ],
            'conclusion': self.conclusion.rep,
        }
