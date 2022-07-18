from typing import List, Dict
import random
from string import Template

from .common import Proposition


def create_nl_propositions_with_FGH(formal_scheme_config,
                                             domain_config,
                                             corpus_config) -> List[Proposition]:
    """
    output is like: [
        'If someone is a ${F}, then they are a ${G}. ',
        '${a} is a ${F}. ',
        '${a} is a ${G}. '
    ]
    """
    return [
        _create_nl_proposition_with_FGH(proposition,
                                                placeolder_substitutions,
                                                domain_config,
                                                corpus_config)
        for proposition, placeolder_substitutions in formal_scheme_config['scheme']
    ]


def _create_nl_proposition_with_FGH(proposition: str,
                                            placeolder_substitutions: Dict,
                                            domain_config,
                                            corpus_config) -> Proposition:
    """
    Args:
        proposition (str)              : e.g. "(x): ${A}x -> ${B}x"
        placeolder_substitutions (Dict): e.g. {"A": "${F}", "B": "${G}"}.
    Returns:
        str: e.g. 'If someone is a ${F}, then they are a ${G}. '
    """
    proposition_to_nl = _get_proposition_translations(corpus_config, domain_config)

    nl_proposition = random.choice(proposition_to_nl[proposition])
    nl_proposition_subtituted = Template(nl_proposition).substitute(placeolder_substitutions)
    return Proposition(nl_proposition_subtituted)


def _get_proposition_translations(corpus_config: Dict, domain: Dict) -> Dict[str, List[str]]:
    """
    Returns:
        Dict[str, List[str]]: something like:
        "(x): ${A}x -> ${B}x" : [
            "If someone is a ${A}, then they are a ${B}. ",
            (...)
        ],
    """
    translations = corpus_config['fss+translations']

    if domain['type'] == 'persons':
        extra_translations = corpus_config['fss+translations_persons']
    elif domain['type'] == 'things':
        extra_translations = corpus_config['fss+translations_things']
    else:
        raise ValueError()

    def join(t1, t2):
        return [*t1, *t2]

    merged_translations = {key: join(translations[key], extra_translations[key]) for key in translations}
    return merged_translations


def substitute_FGH(propositions: List[Proposition],
                            formal_scheme_config: Dict,
                            domain_config: Dict) -> List[Proposition]:
    """Substitute the subject and predicate placeholders.
    output is like [
        'If someone is a descendant of Velociraptor, then they are a ancestor of Stegosaurus. ',
        'Archaeopteryx is a descendant of Velociraptor. ',
        'Archaeopteryx is a ancestor
    ]
    """

    predicate_placeholders = formal_scheme_config['predicate-placeholders']
    entity_placeholders = formal_scheme_config['entity-placeholders']

    subjects = _get_subjects(domain_config, n=len(entity_placeholders))
    zsubjects = list(zip(entity_placeholders, subjects))
    zpredicates = list(zip(
        predicate_placeholders,
        _get_predicates(domain_config, n=len(predicate_placeholders), exclude_names=subjects)
    ))
    subst = dict(zsubjects + zpredicates)  # Merge dicts
    return [Proposition(Template(str(p)).substitute(subst))
            for p in propositions]


def _get_subjects(domain_config, n=1, exclude_names=None):
    exclude_names = exclude_names or []
    return random.sample(list(set(domain_config['subjects']) - set(exclude_names)), n)


def _get_predicates(domain_config, n=1, exclude_names=None):
    exclude_names = exclude_names or []

    rel = random.choices(domain_config['relations'], k=n)     # get n relations

    # get n different object names
    names = random.sample(list(set(domain_config['objects']) - set(exclude_names)), n)

    return [Template(p[0]).substitute(name=p[1]) for p in zip(rel, names)]
