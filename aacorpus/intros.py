from typing import List, Optional
import random


def get_intros(propositions: List[str],
               possible_scheme_intros: List[str],
               possible_premise_intros: List[str],
               possible_conclusion_intros: List[str]) -> List[str]:
    scheme_intro = random.choice(possible_scheme_intros)

    num_arguments = len(propositions)
    premise_intros = random.choice(
        [p[:(num_arguments - 1)]
         for p in possible_premise_intros
         if len(p) > (num_arguments - 2)]
    )
    conclusion_intro = random.choice(possible_conclusion_intros)

    all_intros = [scheme_intro] + premise_intros + [conclusion_intro]

    def normalize(intro: str) -> Optional[str]:
        if intro == '':
            return None
        else:
            return intro[0].lower() + intro[1:]

    return [normalize(intro) for intro in all_intros]

