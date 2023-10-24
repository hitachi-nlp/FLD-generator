import re
from typing import Tuple, Optional, Iterable
import logging
from enum import Enum
from abc import abstractproperty

from pydantic import BaseModel

from FLD_generator.utils import RandomCycle
from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.translators.base import ConstantPhrase, PredicatePhrase

logger = logging.getLogger(__name__)
_WORD_UTILS = WordUtil('eng')


SomeoneX = 'SomeoneX'
SomeoneY = 'SomeoneY'


class StatementType(Enum):
    Fa = 'Fa'

    Fa_Ga = 'Fa_Ga'
    Fa_Gb = 'Fa_Gb'

    Fx_Gb = 'Fx_Gb'
    Fx_Gx = 'Fx_Gx'
    Fx_Gy = 'Fx_Gy'


class Statement:

    @abstractproperty
    def type(self) -> StatementType:
        pass


class DeclareStatement(BaseModel):
    subj_left_modif: Optional[str] = None
    subj: str
    subj_right_modif: Optional[str] = None

    verb_left_modif: Optional[str] = None
    verb: str
    verb_right_modif: Optional[str] = None

    relation: Optional[str] = None

    @property
    def type(self) -> StatementType:
        return _get_statement_type(self)


class IfThenStatement(BaseModel):
    if_statement: DeclareStatement
    then_statement: DeclareStatement

    relation: Optional[str] = None

    @property
    def type(self) -> StatementType:
        return _get_statement_type(self)


def _get_statement_type(statement: Statement) -> str:

    def have(rep: Optional[str], key: str) -> str:
        if rep is None:
            return False
        return rep.find(key) >= 0

    if isinstance(statement, DeclareStatement):
        if have(statement.subj, SomeoneX):
            subj0 = 'x'
        elif have(statement.subj, SomeoneY):
            subj0 = 'y'
        else:
            subj0 = 'a'

        # if have(statement.verb_right_modif, SomeoneX):
        #     modif0 = 'x'
        # elif have(statement.verb_right_modif, SomeoneY):
        #     modif0 = 'y'
        # else:
        #     modif0 = 'm1'

        # return f'{subj0}_v_{modif0}'

        rep = f'F{subj0}'

    elif isinstance(statement, IfThenStatement):
        if have(statement.if_statement.subj, SomeoneX):
            subj0 = 'x'
        elif have(statement.if_statement.subj, SomeoneY):
            subj0 = 'y'
        else:
            subj0 = 'a'

        # if have(statement.if_statement.verb_right_modif, SomeoneX):
        #     modif0 = 'x'
        # elif have(statement.if_statement.verb_right_modif, SomeoneY):
        #     modif0 = 'y'
        # else:
        #     modif0 = 'm1'

        if have(statement.then_statement.subj, SomeoneX):
            subj1 = 'x'
        elif have(statement.then_statement.subj, SomeoneY):
            subj1 = 'y'
        else:
            if statement.then_statement.subj == statement.if_statement.subj:
                subj1 = 'a'
            else:
                subj1 = 'b'

        # if have(statement.then_statement.verb_right_modif, SomeoneX):
        #     modif1 = 'x'
        # elif have(statement.then_statement.verb_right_modif, SomeoneY):
        #     modif1 = 'y'
        # else:
        #     if statement.then_statement.verb_right_modif == statement.if_statement.verb_right_modif:
        #         subj1 = 'm1'
        #     else:
        #         subj1 = 'm2'

        # return f'if__{subj0}_v_{modif0}__then__{subj1}_v_{modif1}'

        rep = f'F{subj0}_G{subj1}'

    return StatementType(rep)


def is_meaningful_stmt(statement: Statement) -> bool:
    if isinstance(statement, DeclareStatement):
        (_, _), (pred_phrase, _) = get_phrases_stmt(statement)
        return pred_phrase.predicate is not None
    else:
        (_, _), (if_pred_phrase, _) = get_phrases_stmt(statement.if_statement)
        (_, _), (then_pred_phrase, _) = get_phrases_stmt(statement.then_statement)
        return if_pred_phrase.predicate is not None and then_pred_phrase.predicate is not None


def make_random_cycle_statement_loader(base_iter: Iterable[Statement],
                                       is_ok_filter_fn = lambda _: True) -> Iterable[Statement]:
    return RandomCycle(
        (statement for statement in base_iter if is_ok_filter_fn(statement)),
        shuffle=False,
    )


def get_PAS_stmt(statement: DeclareStatement) -> Tuple[Tuple[Optional[str], Optional[str], Optional[str], POS]]:
    subj = statement.subj
    subj_left_modif = statement.subj_left_modif
    subj_right_modif = statement.subj_right_modif
    subj_pos = POS.NOUN

    verb = statement.verb
    pred_left_modif = statement.verb_left_modif
    verb_right_modif = statement.verb_right_modif

    if verb == 'is':
        # if verb_right_modif is not None and len(verb_right_modif.split(' ')) == 1:
        #     # verb_right_modif is like "excited"
        #     pred = verb_right_modif.split(' ')[0]
        #     pred_right_modif = None
        #     pred_pos = POS.ADJ
        # else:
        #     # verb_right_modif is like "extemely excited with the game"
        #     # we discard such item because is is a little bit difficult to extract the main predicate phrase
        #     pred = None
        #     pred_right_modif = None
        #     pred_pos = None

        pred = 'is'
        pred_right_modif = verb_right_modif
        pred_left_modif = None

        # pos have many candidates: "cat is a mamal",  "iron is used for clearning",  "someone is kind"
        pred_pos = POS.OTHERS
    else:
        pred = verb
        pred_right_modif = verb_right_modif
        pred_pos = POS.VERB

    return (
        (subj, subj_left_modif, subj_right_modif, subj_pos),
        (pred, pred_left_modif, pred_right_modif, pred_pos),
    )


def get_phrases_stmt(statement: DeclareStatement) -> Tuple[Tuple[ConstantPhrase, POS],
                                                           Tuple[PredicatePhrase, POS]]:
    (
        (subj, subj_left_modif, subj_right_modif, subj_pos),
        (pred, pred_left_modif, pred_right_modif, pred_pos),
    ) = get_PAS_stmt(statement)

    const_phrase = ConstantPhrase(constant=subj,
                                  left_modifier=subj_left_modif,
                                  right_modifier=subj_right_modif)
    pred_phrase = PredicatePhrase(predicate=pred,
                                  right_modifier=pred_right_modif,
                                  left_modifier=pred_left_modif)
    return (const_phrase, subj_pos), (pred_phrase, pred_pos)
