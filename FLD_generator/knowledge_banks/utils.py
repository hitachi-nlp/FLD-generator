from typing import Tuple, List, Optional
import logging

from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.word_banks.english import BE_VERBS, MODAL_VERBS
from FLD_generator.word_banks import build_wordbank
from .statement import StatementType
from .formula import FormulaType

logger = logging.getLogger(__name__)
_WORD_UTILS = WordUtil('eng')
_WORD_BANK = build_wordbank('eng')


def _is_verb(word) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(word)


def _find_verb(words: List[str]) -> Optional[int]:
    for i_word, word in enumerate(words):
        if _is_verb(word):
            return i_word
    return None


def parse_subj(rep: Optional[str], might_be_gerund=False)\
        -> Tuple[Optional[str], Optional[str], Optional[str], Optional[POS]]:
    if rep is None:
        return None, None, None, None

    words = rep.split(' ')

    if len(words) >= 2:
        if might_be_gerund and POS.VERB in _WORD_UTILS.get_pos(words[0]):
            # "running at the park is brabra."
            if not words[0].endswith('ing'):
                gerunds = _WORD_BANK.change_word_form(words[0], POS.VERB, 'ing')
                if len(gerunds) >= 1:
                    subj = gerunds[0]
                else:
                    logger.warning('could not change the verb %s int "ing" form', words[0])
                    subj = words[0]
            else:
                subj = _WORD_UTILS.get_lemma(words[0])
            subj_left_modif = None
            subj_right_modif = ' '.join(words[1:]) or None

            # XXX gerund is a noun! This differs from "He is running at the park"
            subj_pos = POS.NOUN
        else:
            # "red dragon"
            subj = words[-1]
            subj_left_modif = ' '.join(words[:-1]) or None
            subj_right_modif = None
            subj_pos = POS.NOUN
    else:
        subj = words[0]
        subj_left_modif = None
        subj_right_modif = None
        subj_pos = POS.NOUN

    return subj, subj_left_modif, subj_right_modif, subj_pos


def parse_pred(rep: Optional[str], be_verb_shift=True, default_pos=POS.ADJ)\
        -> Tuple[Optional[str], Optional[str], Optional[str], Optional[POS]]:
    if rep is None:
        return None, None, None, None

    words = rep.split(' ')
    if words[0] in MODAL_VERBS:
        verb_idx = _find_verb(words[1:])
        if verb_idx is not None:
            verb_idx += 1
    else:
        verb_idx = _find_verb(words)

    if verb_idx is None:
        logger.info('Could\'nt find verb from words: %s. This can be due to the incomplete detection function. The statement will be skipped.', str(words))
        return None, None, None, None

    else:
        verb = words[verb_idx]

        if be_verb_shift and verb in BE_VERBS:
            next_to_be = words[verb_idx + 1]
            if POS.VERB in _WORD_UTILS.get_pos(next_to_be) and next_to_be.endswith('ing'):
                # "Someone is running at the park"
                pred = words[verb_idx + 1]
                pred_left_modif = None
                pred_right_modif = ' '.join(words[verb_idx + 1 + 1:]) or None
                pred_pos = POS.PRESENT

            elif POS.VERB in _WORD_UTILS.get_pos(next_to_be) and next_to_be.endswith('ed'):
                # "iron is used for cleaning"
                pred = words[verb_idx + 1]
                pred_left_modif = None
                pred_right_modif = ' '.join(words[verb_idx + 1 + 1:]) or None
                pred_pos = POS.PAST

            else:
                pred = words[-1]
                pred_left_modif = ' '.join(words[verb_idx + 1:-1]) or None
                pred_right_modif = None

                pred_poss = _WORD_UTILS.get_pos(pred)
                if POS.VERB in pred_poss and pred.endswith('ing'):
                    pred_pos = POS.PRESENT
                elif POS.VERB in pred_poss and pred.endswith('ed'):
                    pred_pos = POS.PAST
                elif POS.ADJ in pred_poss:     # "iron is sharp"
                    pred_pos = POS.ADJ
                elif POS.NOUN in pred_poss:  # "iron is a tool"
                    pred_pos = POS.NOUN
                else:
                    # raise ValueError(f'Could not determine the POS of a predicate "{pred}"')
                    logger.warning('Could not determine the POS of a predicate %s. Used the default POS=%s', pred, default_pos)
                    pred_pos = default_pos

        else:
            pred = words[verb_idx]
            pred_left_modif = ' '.join(words[:verb_idx]) or None
            pred_right_modif = ' '.join(words[verb_idx + 1:]) or None
            pred_pos = POS.VERB

        return (
            pred,
            pred_left_modif,
            pred_right_modif,
            pred_pos,
        )


def type_formula_to_statement(formula_type: FormulaType) -> StatementType:
    return StatementType(formula_type.value)


def type_statement_to_formula(statement_type: StatementType) -> FormulaType:
    return FormulaType(statement_type.value)
