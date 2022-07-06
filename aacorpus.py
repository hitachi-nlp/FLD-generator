"""Module with Functions for Creating Articificial Argument Corpus"""
from typing import List, Tuple, Optional
import random
import itertools
import re
from string import Template


class Argument:

    def __init__(self,
                 type_: str,
                 claim: Optional[str] = None,
                 intro: Optional[str] = None):
        self._claim = claim
        self._intro = intro
        self._type = type_
        if type_ not in ['arg_intro', 'premise', 'conclusion']:
            raise ValueError()
        self._IA_reg = re.compile(' a ([aeiou])')

    @property
    def type(self):
        return self._type

    @property
    def claim(self) -> Optional[str]:
        if self._claim is None or re.match(r'^\s*$', self._claim):
            return None
        return self._lower(self._normalize(self._claim))

    @property
    def intro(self) -> Optional[str]:
        if self._intro is None or re.match(r'^\s*$', self._intro):
            return None
        return self._lower(self._normalize(self._intro))

    def _normalize(self, sent: str) -> str:
        return self._lower(self._adjust_indef(sent.strip(' ')))

    def _adjust_indef(self, sent: str) -> str:
        # a apple => an apple
        return self._IA_reg.sub(r' an \1', sent)

    def __repr__(self) -> str:
        if self.claim is None:
            return self.intro
        else:
            if self.intro is None:
                return self.claim
            else:
                return ' '.join([self.intro, self.claim])

    # def _upper(self, sent: str) -> str:
    #     return sent[0].upper() + sent[1:]

    def _lower(self, sent: str) -> str:
        return sent[0].lower() + sent[1:]


def create_nl_equivalent(formal_scheme, translations):
    """Generate a natural language scheme equivalent to a formal scheme, given the translations provided"""

    def translate_sscheme(sentence_scheme_pair):
        nls = random.choice(translations[sentence_scheme_pair[0]])
        return (nls, sentence_scheme_pair[1])

    return [translate_sscheme(s) for s in formal_scheme]


def create_argument_scheme(scheme) -> List[str]:
    """Substitute sentence-specific placeholders as detailed in the scheme and returns a formal argument scheme

    output is like: [
        'If someone is a ${F}, then they are a ${G}. ',
        '${a} is a ${F}. ',
        '${a} is a ${G}. '
    ]
    """

    def substitute_sentence(sentence_scheme_pair):
        sentence_scheme = sentence_scheme_pair[0]
        substitutions = sentence_scheme_pair[1]
        return Template(sentence_scheme).substitute(substitutions)

    return [substitute_sentence(s) for s in scheme]


def substitute_placeholders(scheme, predicate_placeholders, entity_placeholders, domain) -> List[str]:
    """Function that replaces placeholders with natural language term in an argument scheme

    output is like [
        'If someone is a descendant of Velociraptor, then they are a ancestor of Stegosaurus. ',
        'Archaeopteryx is a descendant of Velociraptor. ',
        'Archaeopteryx is a ancestor
    ]
    """
    names = get_names(domain, n=len(entity_placeholders))
    znames = list(zip(
        entity_placeholders,
        names
    ))
    zpredicates = list(zip(
        predicate_placeholders,
        get_predicates(domain, n=len(predicate_placeholders), exclude_names=names)
    ))
    subst = dict(znames + zpredicates)  # Merge dicts
    return [Template(s).substitute(subst) for s in scheme]


def get_predicates(domain, n=1, exclude_names=None):
    exclude_names = exclude_names or []
    # get n relations
    rel = random.choices(domain['relations'], k=n)
    # get n different object names
    names = random.sample(list(set(domain['objects']) - set(exclude_names)), n)
    # construct predictes
    return [Template(p[0]).substitute(name=p[1]) for p in zip(rel, names)]


def get_names(domain, n=1, exclude_names=None):
    """Two functions for collecting names and predicates from corpus data"""
    exclude_names = exclude_names or []
    return random.sample(list(set(domain['subjects']) - set(exclude_names)), n)


def add_intros(arguments: List[str],
               possible_arg_intros,
               possible_premise_intros,
               possible_conclusion_intros) -> List[Argument]:
    """Function that addas intros and intros

    output is like: [
        'Consider the following argument: ',
        '',
        'If someone is a descendant of Velociraptor, then they are a ancestor of Stegosaurus. ',
        'Moreover, ',
        'Archaeopteryx is a descendant of Velociraptor. ',
        'Thus, ',
        'Archaeopteryx is a ancestor of Stegosaurus.',
    ]
    """

    premises, conclusion = arguments[:-1], arguments[-1]

    num_arguments = len(arguments)
    premise_intros = random.choice(
        [p[:(num_arguments - 1)]
         for p in possible_premise_intros
         if len(p) > (num_arguments - 2)]
    )
    arg_intro = random.choice(possible_arg_intros)
    conclusion_intro = random.choice(possible_conclusion_intros)
    
    ret_argments = []

    ret_argments.append(Argument('arg_intro', intro=arg_intro,))
    for premise_intro, premise in zip(premise_intros, premises):
        ret_argments.append(Argument('premise', claim=premise, intro=premise_intro))
    ret_argments.append(Argument('conclusion', claim=conclusion.rstrip(), intro=conclusion_intro))
    return ret_argments


def get_translations(corpus_config, domain):
    """get the correct fss transltaions from the corpus given the domain_id (persons / things)"""
    translations = corpus_config['fss+translations']

    if domain['type'] == 'persons':
        extra_translations = corpus_config['fss+translations_persons']
    else:  # domain['type']=='things'
        extra_translations = corpus_config['fss+translations_things']

    def join(t1, t2):
        return [*t1, *t2]

    merged_translations = {key: join(translations[key], extra_translations[key]) for key in translations}
    return merged_translations


def split_argument(nl_argument, predicates):
    """cuts of and returns a trailing sequence of the argument for evaluation (completion)"""
    preds = [p.partition('$')[0] for p in predicates]
    preds = '(' + '| '.join(preds) + ')'
    reg = re.compile(preds)
    # split argument whereever a predicate occurs
    split = reg.split(nl_argument)
    rseq = ''.join(split[-2:])
    # if not rseq[0] == ' ':
    #     rseq = ' ' + rseq
    return rseq.lstrip(' ')


def extend_split(nl_argument, split: str):
    split_extended = split
    argument_trunk = nl_argument[0:-len(split_extended)]
    argument_trunk = argument_trunk.strip(' ')
    words = argument_trunk.split(' ')
    split_extended = ' '.join([words[-1], split_extended])
    if words[-2] == 'not':
        split_inversed = split_extended
        split_extended = ' '.join(words[-2] + split_extended)
    else:
        split_inversed = ' '.join(['not', split_extended])
    return {
        'split_extended': split_extended,
        'split_inversed': split_inversed
    }


def gather_arguments(premises, conclusion):
    sentences = {}

    for idx, premise in enumerate(premises):
        sentences[f'premise-{idx}'] = premise.claim

    distractors = []
    for idx, distractor in enumerate(distractors):
        sentences[f'distractor-{idx}'] = distractor.claim

    sentences['conclusion'] = conclusion.claim

    proofs = [
        [[f'premise-{idx}' for idx in range(len(premises))], 'conclusion'],
    ]
    return sentences, proofs


def pipeline_create_argument(corpus_config, domain_id, scheme_id,
                             depth: int = 1,
                             permutate_premises=False, argument_id='none', split_arg=False,
                             add_proof=False):
    if depth != 1:
        raise NotImplementedError()

    # STEP1: Get domain and formal argument scheme
    domain = next(d for d in corpus_config['domains'] if d['id'] == domain_id)
    formal_argument_scheme = next(a for a in corpus_config['formal_argument_schemes'] if a['id'] == scheme_id)

    # STEP2: Create the informal argument scheme
    argument_scheme = create_argument_scheme(
        create_nl_equivalent(
            formal_argument_scheme['scheme'],
            get_translations(corpus_config, domain)
        )
    )

    # STEP3: Substitute nl terms for placeholders
    bare_arguments = substitute_placeholders(
        argument_scheme,
        formal_argument_scheme['predicate-placeholders'],  # predicates
        formal_argument_scheme['entity-placeholders'],  # names
        domain  # domain
    )
    if add_proof:
        for i_premise, sent in enumerate(bare_arguments[:-1]):
            bare_arguments[i_premise] = f'[premise]{sent}'

    # STEP4 & STEP5: Add intros
    arguments_with_intros = add_intros(
        bare_arguments,
        domain['intros'],
        corpus_config['premise_intros'],
        corpus_config['conclusion_indicators'],
    )
    all_intro, premises, conclusion = arguments_with_intros[0], arguments_with_intros[1:-1], arguments_with_intros[-1]
    if permutate_premises:
        premises = list(random.choice(list(itertools.permutations(premises))))

    intros = {
        'all': all_intro.intro,
        'premise': [premise.intro for premise in premises],
        'conclusion': conclusion.intro,
    }
    sentences, proofs = gather_arguments(premises, conclusion)

    argument = {
        'id': argument_id,

        'intros': intros,
        'sentences': sentences,
        'proofs': proofs,

        'scheme_id': scheme_id,
        'domain_id': domain_id,
        'base_scheme_group': formal_argument_scheme['base_scheme_group'],
        'scheme_variant': formal_argument_scheme['scheme_variant'],
        'permutate_premises': str(permutate_premises),
        'depth': depth,
    }

    # determine trailing sequence
    if split_arg:
        split_arg = {'split' : split_argument(str(conclusion), domain['relations'])}
        argument.update(split_arg)
        argument.update(extend_split(str(conclusion), argument['split']))

    return argument
