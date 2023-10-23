import re
from typing import Tuple, List, Optional
import logging

from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.formula import Formula

logger = logging.getLogger(__name__)
_WORD_UTILS = WordUtil('eng')


def is_simple_unary_implication_shared_const(formula: Formula) -> bool:
    """ {A}{a} -> {B}{a} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 1 and len(preds) == 2


def is_simple_unary_implication_unshared_const(formula: Formula) -> bool:
    """ {A}{a} -> {B}{b} """

    if not re.match(r'^{[^}]*}{[^}]*} -> {[^}]*}{[^}]*}$', formula.rep):
        return False

    consts = formula.constants
    preds = formula.predicates
    return len(consts) == 2 and len(preds) == 2


def is_simple_universal_implication(formula: Formula) -> bool:
    """ (x): {A}x -> {B}x """

    if not re.match(r'^\(x\): {[^}]*}x -> {[^}]*}x$', formula.rep):
        return False

    preds = formula.predicates
    return len(preds) == 2


def get_if_then_constants(formula: Formula) -> Tuple[Optional[Formula], Optional[Formula]]:
    consts = formula.constants

    if len(consts) == 0:
        return None, None

    elif len(consts) == 1:
        return consts[0], consts[0]

    elif len(consts) == 2:
        const_if = (
            consts[0]
            if formula.rep.find(consts[0].rep) < formula.rep.find(consts[1].rep)
            else consts[1]
        )
        const_then = consts[0] if const_if == consts[1] else consts[1]

        return const_if, const_then

    else:
        raise ValueError()


def get_if_then_predicates(formula: Formula) -> Tuple[Formula, Formula]:
    preds = formula.unary_predicates

    if len(preds) == 1:
        return preds[0], preds[0]

    elif len(preds) == 2:
        pred_if = (
            preds[0]
            if formula.rep.find(preds[0].rep) < formula.rep.find(preds[1].rep)
            else preds[1]
        )
        pred_then = preds[0] if pred_if == preds[1] else preds[1]

        return pred_if, pred_then

    else:
        raise ValueError()


def is_verb(word) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(word)


def find_verb(words: List[str]) -> Optional[int]:
    for i_word, word in enumerate(words):
        if is_verb(word):
            return i_word
    return None


def parse_verb(rep: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if rep is None:
        return None, None, None

    words = rep.split(' ')
    verb_idx = find_verb(words)
    if verb_idx is None:
        logger.info('Could\'nt find verb from words: %s. This can be due to the incomplete detection function. The statement will be skipped.', str(words))
        return None, None, None
    else:
        return (
            words[verb_idx],
            ' '.join(words[:verb_idx]) or None,
            ' '.join(words[verb_idx + 1:]) or None,
        )


def parse_subj(rep: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if rep is None:
        return None, None, None
    words = rep.split(' ')
    if len(words) >= 2:
        subj = words[-1]
        subj_left_modif = words[:-1]
        subj_right_modif = None
    else:
        subj = words[0]
        subj_left_modif = None
        subj_right_modif = None
    return subj, subj_left_modif, subj_right_modif
