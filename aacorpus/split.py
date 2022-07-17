import re


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


