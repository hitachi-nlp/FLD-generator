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


def parse_as_subj(rep: Optional[str], might_be_gerund=False)\
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


def parse_as_pred(rep: Optional[str],
                  prioritize_pos: Optional[POS] = None,
                  be_verb_shift=True,
                  default_pos=POS.ADJ)\
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
        logger.info('Couldn\'t find verb from words: %s. The statement will be skipped.', str(words))
        return None, None, None, None

    else:
        verb = words[verb_idx]

        if be_verb_shift and verb in BE_VERBS:

            next_to_be = words[verb_idx + 1]

            if is_present_particle(next_to_be):
                # "Someone is running at the park"
                pred = words[verb_idx + 1]
                pred_left_modif = None
                pred_right_modif = ' '.join(words[verb_idx + 1 + 1:]) or None
                pred_pos = POS.PRESENT_PARTICLE

            elif is_past_particle_form(next_to_be):
                # "iron is used for cleaning"
                pred = words[verb_idx + 1]
                pred_left_modif = None
                pred_right_modif = ' '.join(words[verb_idx + 1 + 1:]) or None
                pred_pos = POS.PAST_PARTICLE

            else:

                rep_wo_be = ' '.join(words[verb_idx + 1:])
                found_pred = False
                for pred_position in ['leftmost', 'rightmost']:
                    _pred, _pred_left_modif, _pred_right_modif = parse(rep_wo_be, pred_position)

                    _pred_poss = _WORD_UTILS.get_pos(_pred)
                    if prioritize_pos is not None and prioritize_pos in _pred_poss:
                        hit = True
                        _pred_pos = prioritize_pos
                    elif POS.VERB in _pred_poss and _pred.endswith('ing'):
                        hit = True
                        _pred_pos = POS.PRESENT_PARTICLE
                    elif POS.VERB in _pred_poss and _pred.endswith('ed'):
                        hit = True
                        _pred_pos = POS.PAST_PARTICLE
                    elif POS.ADJ in _pred_poss:     # "iron is sharp"
                        hit = True
                        _pred_pos = POS.ADJ
                    elif POS.ADJ_SAT in _pred_poss:     # "iron is ignorant"
                        hit = True
                        _pred_pos = POS.ADJ_SAT
                    elif POS.NOUN in _pred_poss:  # "iron is a tool"
                        hit = True
                        _pred_pos = POS.NOUN
                    else:
                        hit = False

                    if hit:
                        pred, pred_left_modif, pred_right_modif, pred_pos = _pred, _pred_left_modif, _pred_right_modif, _pred_pos
                        found_pred = True
                        break

                if not found_pred:
                    pred, pred_left_modif, pred_right_modif = parse(rep_wo_be, 'leftmost')
                    pred_pos = default_pos
                    logger.info('Could not find predicate from "%s" as no word matched a pre-defined POS. Will use default "%s"(POS=%s) as the predicate.',
                                rep,
                                pred,
                                str(pred_pos))

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


def is_present_particle(word: str) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(word) and word.endswith('ing')


def is_past_particle_form(next_to_be: str) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(next_to_be)\
        and (next_to_be.endswith('ed') or next_to_be in ['born', 'spoken', 'wrote'])


def parse(rep: str, main_word_position: str) -> Tuple[str, Optional[str], Optional[str]]:
    words = rep.split(' ')
    if main_word_position == 'leftmost':
        main_word = words[0]
        left_modifier = None
        right_modifier = ' '.join(words[1:]) or None
    elif main_word_position == 'rightmost':
        main_word = words[-1]
        left_modifier = ' '.join(words[:-1]) or None
        right_modifier = None
    else:
        raise ValueError(f'Unknown position = {main_word_position}')
    return main_word, left_modifier, right_modifier




def type_formula_to_statement(formula_type: FormulaType) -> StatementType:
    return StatementType(formula_type.value)


def type_statement_to_formula(statement_type: StatementType) -> FormulaType:
    return FormulaType(statement_type.value)
