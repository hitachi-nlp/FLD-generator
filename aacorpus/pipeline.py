from typing import List
import random
import itertools
import re
from string import Template

from .common import Proposition
from .templates import (
    create_nl_propositions_with_FGH,
    substitute_FGH,
)
from .intros import get_intros
from .split import extend_split, split_argument


def create_names_and_proof(premises: List[Proposition], conclusion: List[Proposition]):
    sentences = {}

    for idx, premise in enumerate(premises):
        sentences[f'premise-{idx}'] = str(premise)

    distractors = []
    for idx, distractor in enumerate(distractors):
        sentences[f'distractor-{idx}'] = str(distractor)

    sentences['conclusion'] = str(conclusion)

    proofs = [
        [[f'premise-{idx}' for idx in range(len(premises))], 'conclusion'],
    ]
    return sentences, proofs


def pipeline(corpus_config,
             domain_id,
             scheme_id,
             depth: int = 1,
             permutate_premises=False,
             split_arg=False):
    if depth != 1:
        raise NotImplementedError()

    # STEP1 of Fugre.2
    domain_config = next(d for d in corpus_config['domains']
                         if d['id'] == domain_id)
    formal_scheme_config = next(a for a in corpus_config['formal_argument_schemes']
                                if a['id'] == scheme_id)

    # STEP2 of Fugre.2
    nl_propositions_with_FGH = create_nl_propositions_with_FGH(
        formal_scheme_config, domain_config, corpus_config
    )

    # STEP3 of Fugre.2
    nl_propositions = substitute_FGH(
        nl_propositions_with_FGH, formal_scheme_config, domain_config,
    )
    premises, conclusion = nl_propositions[:-1], nl_propositions[-1]

    # STEP4 & STEP5 of Fugre.2
    intros = get_intros(
        nl_propositions,
        domain_config['intros'],
        corpus_config['premise_intros'],
        corpus_config['conclusion_indicators'],
    )
    scheme_intro, premise_intros, conclusion_intro = intros[0], intros[1:-1], intros[-1]

    # permute
    if permutate_premises:
        indexes = random.choice(list(itertools.permutations(range(len(premises)))))
        premises = [premises[idx] for idx in indexes]
        premise_intros = [premise_intros[idx] for idx in indexes]

    named_propositions, proofs = create_names_and_proof(premises, conclusion)

    argument = {
        'intros': {
            'all': scheme_intro,
            'premise': premise_intros,
            'conclusion': conclusion_intro,
        },

        'sentences': named_propositions,
        'proofs': proofs,

        'scheme_id': scheme_id,
        'domain_id': domain_id,
        'base_scheme_group': formal_scheme_config['base_scheme_group'],
        'scheme_variant': formal_scheme_config['scheme_variant'],
        'permutate_premises': str(permutate_premises),
        'depth': depth,
    }

    # determine trailing sequence
    if split_arg:
        split_arg = {'split' : split_argument(str(conclusion), domain_config['relations'])}
        argument.update(split_arg)
        argument.update(extend_split(str(conclusion), argument['split']))

    return argument
