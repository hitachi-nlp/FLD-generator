import re
from typing import Tuple, Optional, Iterable, List
import logging
from enum import Enum
from abc import abstractproperty

from pydantic import BaseModel

from FLD_generator.utils import RandomCycle
from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.word_banks.english import BE_VERBS
from FLD_generator.translators.base import ConstantPhrase, PredicatePhrase

logger = logging.getLogger(__name__)
_WORD_UTILS = WordUtil('eng')


SomeoneX = 'SOMEONE_X'
SomeoneY = 'SOMEONE_Y'
SomethingX = 'SOMETHING_X'
SomethingY = 'SOMETHING_Y'



class StatementType(Enum):
    F = 'F'
    nF = 'nF'

    Fa = 'Fa'
    nFa = 'nFa'

    Fx = 'Fx'
    nFx = 'nFx'

    F_G = 'F_G'
    nF_G = 'nF_G'
    F_nG = 'F_nG'

    Fa_Ga = 'Fa_Ga'
    nFa_Ga = 'nFa_Ga'
    Fa_nGa = 'Fa_nGa'
    nFa_nGa = 'nFa_nGa'

    Fa_Gb = 'Fa_Gb'
    nFa_Gb = 'nFa_Gb'
    Fa_nGb = 'Fa_nGb'
    nFa_nGb = 'nFa_nGb'

    Fx_Gb = 'Fx_Gb'
    nFx_Gb = 'nFx_Gb'
    Fx_nGb = 'Fx_nGb'
    nFx_nGb = 'nFx_nGb'

    Fx_Gx = 'Fx_Gx'
    nFx_Gx = 'nFx_Gx'
    Fx_nGx = 'Fx_nGx'
    nFx_nGx = 'nFx_nGx'

    Fx_Gy = 'Fx_Gy'
    nFx_Gy = 'nFx_Gy'
    Fx_nGy = 'Fx_nGy'
    nFx_nGy = 'nFx_nGy'

    INCOMPLETE = 'INCOMPLETE'


class Statement:

    @abstractproperty
    def type(self) -> StatementType:
        pass


class DeclareStatement(BaseModel):
    subj_left_modif: Optional[str] = None
    subj: str
    subj_right_modif: Optional[str] = None
    subj_pos: POS

    pred_left_modif: Optional[str] = None
    pred: Optional[str] = None
    pred_right_modif: Optional[str] = None
    pred_pos: Optional[POS] = None

    negated: bool
    relation: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pred in BE_VERBS:
            raise ValueError(f'A predicate must not be a be-verb, but be a modifier of that be-verb: {str(self)}')

    @property
    def type(self) -> StatementType:
        return _get_statement_type(self)


class IfThenStatement(BaseModel):
    if_statement: DeclareStatement
    then_statement: DeclareStatement

    negated: bool
    relation: Optional[str] = None

    @property
    def type(self) -> StatementType:
        return _get_statement_type(self)


def make_random_cycle_statement_loader(base_iter: Iterable[Statement],
                                       is_ok_filter_fn = lambda _: True) -> Iterable[Statement]:
    return RandomCycle(
        (statement for statement in base_iter if is_ok_filter_fn(statement)),
        shuffle=False,
    )


def _get_statement_type(statement: Statement) -> str:

    def have(rep: Optional[str], keys: List[str]) -> str:
        if rep is None:
            return False
        return any(rep.find(key) >= 0 for key in keys)

    if isinstance(statement, DeclareStatement):
        if statement.subj is None:
            rep = 'INCOMPLETE'

        if statement.pred is None:
            rep = 'F'
        else:
            if have(statement.subj, [SomeoneX, SomethingX]):
                subj0 = 'x'
            elif have(statement.subj, [SomeoneY, SomethingY]):
                subj0 = 'y'
            else:
                subj0 = 'a'

            rep = f'F{subj0}'

        if statement.negated:
            rep = rep.replace('F', 'nF')

    elif isinstance(statement, IfThenStatement):
        if statement.if_statement.subj is None or statement.then_statement.subj is None:
            rep = 'INCOMPLETE'

        if statement.if_statement.pred is None and statement.then_statement.pred is None:
            rep = 'F_G'
        else:
            if have(statement.if_statement.subj, [SomeoneX, SomethingX]):
                subj0 = 'x'
            elif have(statement.if_statement.subj, [SomeoneY, SomethingY]):
                subj0 = 'y'
            else:
                subj0 = 'a'

            if have(statement.then_statement.subj, [SomeoneX, SomethingX]):
                subj1 = 'x'
            elif have(statement.then_statement.subj, [SomeoneY, SomethingY]):
                subj1 = 'y'
            else:
                if statement.then_statement.subj == statement.if_statement.subj:
                    subj1 = 'a'
                else:
                    subj1 = 'b'

            rep = f'F{subj0}_G{subj1}'

        if statement.if_statement.negated:
            rep = rep.replace('F', 'nF')
        elif statement.then_statement.negated:
            rep = rep.replace('G', 'nG')
        elif statement.negated:
            raise NotImplementedError()

    return StatementType(rep)


def get_phrases_stmt(statement: DeclareStatement) -> Tuple[Tuple[Optional[ConstantPhrase], Optional[POS]],
                                                           Tuple[PredicatePhrase, POS]]:
    (
        (subj, subj_left_modif, subj_right_modif, subj_pos),
        (pred, pred_left_modif, pred_right_modif, pred_pos),
    ) = (
        (statement.subj, statement.subj_left_modif, statement.subj_right_modif, statement.subj_pos),
        (statement.pred, statement.pred_left_modif, statement.pred_right_modif, statement.pred_pos),
    )

    if pred is not None:
        const_phrase = ConstantPhrase(constant=subj,
                                      left_modifier=subj_left_modif,
                                      right_modifier=subj_right_modif)
        const_pos = subj_pos
        pred_phrase = PredicatePhrase(predicate=pred,
                                      right_modifier=pred_right_modif,
                                      left_modifier=pred_left_modif)
        pred_pos = pred_pos
    else:
        const_phrase = None
        const_pos = None
        pred_phrase = PredicatePhrase(predicate=subj,
                                      right_modifier=subj_right_modif,
                                      left_modifier=subj_left_modif)
        pred_pos = subj_pos

    return (const_phrase, const_pos), (pred_phrase, pred_pos)


# def _get_PAS_stmt(statement: DeclareStatement) -> Tuple[Tuple[Optional[str], Optional[str], Optional[str], POS]]:
#     subj = statement.subj
#     subj_left_modif = statement.subj_left_modif
#     subj_right_modif = statement.subj_right_modif
#     subj_pos = statement.subj_pos
# 
#     # if POS.VERB in _WORD_UTILS.get_pos(subj) and subj_right_modif is not None:
#     #     # "running at the park"
#     #     subj_pos = POS.VERB
#     # else:
#     #     subj_pos = POS.NOUN
# 
#     if statement.pred in BE_VERBS:
#         raise Exception('We do not expect to pass here, might be a bug.')
#         # if statement.pred_right_modif is None:
#         #     raise Exception('Something might by wrong')
# 
#         # if statement.pred_right_modif.find(' ') >= 0:
#         #     pred, pred_right_modif = statement.pred_right_modif.split(' ', 1)
#         # else:
#         #     pred, pred_right_modif = pred_right_modif, None
# 
#         # pred_left_modif = None
# 
#         # # pos have many candidates: "cat is a mamal",  "iron is used for clearning",  "someone is kind"
#         # pred_pos = POS.OTHERS
#     else:
#         pred = statement.pred
#         pred_left_modif = statement.pred_left_modif
#         pred_right_modif = statement.pred_right_modif
#         # pred_pos = POS.VERB
#         pred_pos = statement.pred_pos
# 
#     return (
#         (subj, subj_left_modif, subj_right_modif, subj_pos),
#         (pred, pred_left_modif, pred_right_modif, pred_pos),
#     )
