from typing import Tuple, List, Optional
import logging

from FLD_generator.word_banks.word_utils import WordUtil, POS
from .statement import StatementType
from .formula import FormulaType

logger = logging.getLogger(__name__)
_WORD_UTILS = WordUtil('eng')


def _is_verb(word) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(word)


def _find_verb(words: List[str]) -> Optional[int]:
    for i_word, word in enumerate(words):
        if _is_verb(word):
            return i_word
    return None


def parse_verb(rep: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if rep is None:
        return None, None, None

    words = rep.split(' ')
    verb_idx = _find_verb(words)
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
        subj_left_modif = ' '.join(words[:-1]) or None
        subj_right_modif = None
    else:
        subj = words[0]
        subj_left_modif = None
        subj_right_modif = None
    return subj, subj_left_modif, subj_right_modif


def type_formula_to_statement(formula_type: FormulaType) -> StatementType:
    return StatementType(formula_type.value)


def type_statement_to_formula(statement_type: StatementType) -> FormulaType:
    return FormulaType(statement_type.value)
