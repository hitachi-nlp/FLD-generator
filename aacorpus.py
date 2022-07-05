"""Module with Functions for Creating Articificial Argument Corpus"""
import random
import itertools
import re
from string import Template


def create_nl_equivalent(formal_scheme, translations):
    """
    this function generates a natural language scheme equivalent
    to a formal scheme, given the translations provided
    """

    def translate_sscheme(sentence_scheme_pair):
        nls = random.choice(translations[sentence_scheme_pair[0]])
        return (nls, sentence_scheme_pair[1])

    return [translate_sscheme(s) for s in formal_scheme]


def create_argument_scheme(scheme):
    """
    The following function substitutes sentence-specific placeholders
    as detailed in the scheme and returns a formal argument scheme
    """

    def substitute_sentence(sentence_scheme_pair):
        sentence_scheme = sentence_scheme_pair[0]
        substitutions = sentence_scheme_pair[1]
        return Template(sentence_scheme).substitute(substitutions)

    return [substitute_sentence(s) for s in scheme]


def get_names(domain, n=1, exclude_names=None):
    """Two functions for collecting names and predicates from corpus data"""
    exclude_names = exclude_names or []
    return random.sample(list(set(domain['subjects']) - set(exclude_names)), n)


def get_predicates(domain, n=1, exclude_names=None):
    exclude_names = exclude_names or []
    # get n relations
    rel = random.choices(domain['relations'], k=n)
    # get n different object names
    names = random.sample(list(set(domain['objects']) - set(exclude_names)), n)
    # construct predictes
    return [Template(p[0]).substitute(name=p[1]) for p in zip(rel, names)]


def substitute_placeholders(scheme, predicate_placeholders, entity_placeholders, domain):
    """Function that replaces placeholders with natural language term in an argument scheme"""
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


def nl_encase(pc_list, arg_intros, premise_intros, conclusion_indicators, permutate_premises=False):
    """Function that addas intros and indicators"""

    # randomly choose argument intro statement
    p_intros = random.choice(
        [p[:(len(pc_list) - 1)] for p in premise_intros if len(p) > (len(pc_list) - 2)]
    )
    # premises
    p_list = pc_list[:-1]
    # permutate premises
    if permutate_premises:
        p_list = random.choice(list(itertools.permutations(p_list)))
    # iterate premise-intro and premise
    l = list(itertools.chain(*zip(p_intros, p_list)))
    # preprend argument intro
    l.insert(0, random.choice(arg_intros))
    # append conclusion indicator
    l.append(random.choice(conclusion_indicators))
    # append conclusion
    conclusion = pc_list[-1]
    l.append(conclusion.rstrip())
    # return list of strings
    return l


def make_lower_case(argument_l, domain):
    """Tidy up"""
    # We assume that if some sentence is empty, then the next one starts with capital letter.
    requires_capital_letter = [
        (s[-2] in ['.', ':']) if len(s) > 1 else True for s in argument_l
    ]

    def check_and_change(sentence, i):
        if i < 1 or len(sentence) < 2:
            r = sentence
        elif requires_capital_letter[i - 1]:
            r = sentence
        elif sentence.partition(' ')[0] in domain['subjects']:
            r = sentence
        else:
            r = sentence[0].lower() + sentence[1:]
        return r

    modified_list = [check_and_change(argument_l[i], i) for i in range(len(argument_l))]
    return modified_list


def adjust_indef_article(stringlist):
    ia_reg = re.compile(' a ([aeiou])')
    return [ia_reg.sub(r' an \1', s) for s in stringlist]


def get_translations(corpus_config, domain):
    """get the correct fss transltaions from the corpus given the domain_id (persons / things)"""
    translations = corpus_config["fss+translations"]

    if domain["type"] == "persons":
        extra_translations = corpus_config["fss+translations_persons"]
    else:  # domain["type"]=="things"
        extra_translations = corpus_config["fss+translations_things"]

    def join(t1, t2):
        return [*t1, *t2]

    merged_translations = {key: join(translations[key], extra_translations[key]) for key in translations}
    return merged_translations


def split_argument(nl_argument, predicates):
    """cuts of and returns a trailing sequence of the argument for evaluation (completion)"""
    preds = [p.partition("$")[0] for p in predicates]
    preds = "(" + "| ".join(preds) + ")"
    reg = re.compile(preds)
    # split argument whereever a predicate occurs
    split = reg.split(nl_argument)
    rseq = "".join(split[-2:])
    if not rseq[0] == " ":
        rseq = " " + rseq
    return rseq


def extend_split(nl_argument, split):
    split_extended = split
    argument_trunk = nl_argument[0:-len(split_extended)]
    argument_trunk = argument_trunk.strip(" ")
    words = argument_trunk.split(" ")
    split_extended = " " + words[-1] + split_extended
    if words[-2] == "not":
        split_inversed = split_extended
        split_extended = " " + words[-2] + split_extended
    else:
        split_inversed = " not" + split_extended
    rdict = {"split_extended": split_extended, "split_inversed": split_inversed}
    return rdict


def pipeline_create_argument(corpus_config, domain_id, scheme_id, permutate_premises=False, argument_id='none', split_arg=False):

    # Get domain and formal argument scheme
    domain = next(d for d in corpus_config["domains"] if d['id'] == domain_id)
    formal_argument_scheme = next(a for a in corpus_config["formal_argument_schemes"] if a['id'] == scheme_id)

    # Create the informal argument scheme
    argument_scheme = create_argument_scheme(
        create_nl_equivalent(
            formal_argument_scheme['scheme'],
            get_translations(corpus_config, domain)
        )
    )

    # Substitute nl terms for placeholders
    bare_premise_conclusion_list = substitute_placeholders(
        argument_scheme,
        formal_argument_scheme['predicate-placeholders'],  # predicates
        formal_argument_scheme['entity-placeholders'],  # names
        domain  # domain
    )

    # Add intros and indicators
    encased_premise_conclusion_list = nl_encase(
        bare_premise_conclusion_list,
        domain['intros'],
        corpus_config["premise_intros"],
        corpus_config["conclusion_indicators"],
        permutate_premises=permutate_premises
    )

    # Adjust upper/lower cases
    final_premise_conclusion_structure = make_lower_case(
        encased_premise_conclusion_list,
        domain
    )

    # Adjust indefinite article
    final_premise_conclusion_structure = adjust_indef_article(final_premise_conclusion_structure)

    # Join premises, including conclusion indicator
    premises = "".join(final_premise_conclusion_structure[:-1])
    conclusion = final_premise_conclusion_structure[-1]

    # Remove trailing whitespace from premises and add initial whitespace to conclusion
    premises = premises.rstrip()
    conclusion = " " + conclusion

    # Join
    argument = {
        "id": argument_id,
        "premise": premises,
        "conclusion": conclusion,
        "scheme_id": scheme_id,
        "domain_id": domain_id,
        "base_scheme_group": formal_argument_scheme['base_scheme_group'],
        "scheme_variant": formal_argument_scheme['scheme_variant'],
        "permutate_premises": str(permutate_premises)
    }

    # determine trailing sequence
    if split_arg:
        split_arg = {"split" : split_argument(conclusion, domain['relations'])}
        argument.update(split_arg)
        argument.update(extend_split(conclusion, argument["split"]))

    return argument
