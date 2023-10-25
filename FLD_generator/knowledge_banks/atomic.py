from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Iterable,
    Union,
)
import re
from enum import Enum
import logging
import random

from .base import KnowledgeBankBase
from .statement import (
    DeclareStatement,
    IfThenStatement,
    Statement,
    StatementType,
    SomeoneX,
    SomeoneY,
)
from .utils import (
    parse_verb,
    parse_subj,
)


logger = logging.getLogger(__name__)


class AtomicRelation(Enum):
    # "x" means PersonX
    xAttr = 'xAttr'
    xEffect = 'xEffect'
    xIntent = 'xIntent'
    xNeed = 'xNeed'
    xReact = 'xReact'
    xWant = 'xWant'

    # "o" means others, including but not limited to PersonY
    oEffect = 'oEffect'
    oReact = 'oReact'
    oWant = 'oWant'


_E0_IS_IF_RELATIONS = [
    AtomicRelation.xAttr,
    AtomicRelation.xNeed,
    AtomicRelation.xIntent,

    AtomicRelation.xEffect,
    AtomicRelation.xReact,
    AtomicRelation.xWant,

    AtomicRelation.oEffect,
    AtomicRelation.oReact,
    AtomicRelation.oWant,
]
_E1_IS_IF_RELATIONS = []


def _load_statements(path: str,
                     max_statements: Optional[int] = None,
                     shuffle=False) -> Iterable[IfThenStatement]:
    logger.info('loading ATOMIC statements from file "%s"', path)

    if shuffle:
        lines = open(path).readlines()
        random.shuffle(lines)
    else:
        lines = open(path)

    for i_line, line in enumerate(lines):
        if max_statements is not None and i_line >= max_statements:
            break
        e0_str, rel_str, e1_str = line.rstrip('\n').replace('-', ' ').split('\t')
        e0_str = _normalize_person_xy(e0_str.lower())
        e1_str = _normalize_person_xy(e1_str.lower())
        relation = AtomicRelation(rel_str)
        if e1_str == 'none':
            continue
        if line.find('___') >= 0:
            continue

        (
            (e0_subj, e0_subj_left_modif, e0_subj_right_modif),
            (e0_verb, e0_verb_left_modif, e0_verb_right_modif),
        ) = _parse_e0(e0_str, relation)

        is_personY_related = e0_verb_right_modif is not None and e0_verb_right_modif.find(SomeoneY) >= 0
        (
            (e1_subj, e1_subj_left_modif, e1_subj_right_modif),
            (e1_verb, e1_verb_left_modif, e1_verb_right_modif),
        ) = _parse_e1(e1_str, relation, is_personY_related=is_personY_related)

        if e0_subj != SomeoneX:
            raise NotImplementedError()

        if relation in _E0_IS_IF_RELATIONS:
            if_subj = e0_subj
            if_subj_left_modif = e0_subj_left_modif
            if_subj_right_modif = e0_subj_right_modif

            if_verb = e0_verb
            if_verb_left_modif = e0_verb_left_modif
            if_verb_right_modif = e0_verb_right_modif

            then_subj = e1_subj
            then_subj_left_modif = e1_subj_left_modif
            then_subj_right_modif = e1_subj_right_modif

            then_verb = e1_verb
            then_verb_left_modif = e1_verb_left_modif
            then_verb_right_modif = e1_verb_right_modif

        elif relation in _E1_IS_IF_RELATIONS:
            then_subj = e0_subj
            then_subj_left_modif = e0_subj_left_modif
            then_subj_right_modif = e0_subj_right_modif

            then_verb = e0_verb
            then_verb_left_modif = e0_verb_left_modif
            then_verb_right_modif = e0_verb_right_modif

            if_subj = e1_subj
            if_subj_left_modif = e1_subj_left_modif
            if_subj_right_modif = e1_subj_right_modif

            if_verb = e1_verb
            if_verb_left_modif = e1_verb_left_modif
            if_verb_right_modif = e1_verb_right_modif
        else:
            raise Exception()

        if if_verb is None or then_verb is None:
            continue

        if_statement = DeclareStatement(
            subj=if_subj,
            subj_right_modif=if_subj_right_modif,
            subj_left_modif=if_subj_left_modif,
            verb=if_verb,
            verb_left_modif=if_verb_left_modif,
            verb_right_modif=if_verb_right_modif,
        )

        then_statement = DeclareStatement(
            subj=then_subj,
            subj_right_modif=then_subj_right_modif,
            subj_left_modif=then_subj_left_modif,
            verb=then_verb,
            verb_left_modif=then_verb_left_modif,
            verb_right_modif=then_verb_right_modif,
        )

        if_then_statement = IfThenStatement(
            if_statement=if_statement,
            then_statement=then_statement,
            relation=relation.value,
        )

        yield if_then_statement


def _normalize_person_xy(rep: str) -> str:
    rep = re.sub('[Pp]erson[-]*[Xx]', SomeoneX, rep)
    rep = re.sub('[Pp]erson[-]*[Yy]', SomeoneY, rep)
    return rep


def _parse_e0(e0_str: str, relation: AtomicRelation) -> Tuple[
    Tuple[Optional[str], Optional[str], Optional[str]],
    Tuple[Optional[str], Optional[str], Optional[str]],
]:
    e0_subj_str, e0_pred_str = e0_str.split(' ', 1)
    return parse_subj(e0_subj_str), parse_verb(e0_pred_str)


def _parse_e1(e1_str: str,
              relation: AtomicRelation,
              is_personY_related=False) -> Tuple[
    Tuple[Optional[str], Optional[str], Optional[str]],
    Tuple[Optional[str], Optional[str], Optional[str]],
]:
    e1_words = e1_str.split(' ')

    e1_subj_str = e1_words[0] if e1_words[0] in [SomeoneX, SomeoneY] else None
    if e1_subj_str is None:
        if relation in [AtomicRelation.xEffect, AtomicRelation.xReact, AtomicRelation.xWant,
                        AtomicRelation.xAttr, AtomicRelation.xNeed, AtomicRelation.xIntent]:
            e1_subj_str = SomeoneX
        elif relation in [AtomicRelation.oEffect, AtomicRelation.oReact, AtomicRelation.oWant]:
            if is_personY_related:
                e1_subj_str = SomeoneY
            else:
                e1_subj_str = 'others'
        else:
            raise Exception('Not expected')

    e1_pred_str = ' '.join(e1_words[1:]) if e1_words[0] in [SomeoneX, SomeoneY] else ' '.join(e1_words)
    if relation in [AtomicRelation.xWant, AtomicRelation.oWant,
                    AtomicRelation.xNeed, AtomicRelation.xIntent]:
        if relation in [AtomicRelation.xWant, AtomicRelation.oWant]:
            e1_verb = 'want'
        elif relation in [AtomicRelation.xNeed]:
            e1_verb = 'need'
        elif relation in [AtomicRelation.xIntent]:
            e1_verb = 'intend'
        else:
            raise ValueError()
        e1_pred_str = (f'{e1_verb} to {e1_pred_str}' if not e1_pred_str.startswith('to')
                       else f'{e1_verb} {e1_pred_str}')
    elif relation in [AtomicRelation.xReact, AtomicRelation.oReact]:
        e1_pred_str = f'feel {e1_pred_str}'
    elif relation in [AtomicRelation.xAttr]:
        e1_pred_str = f'is {e1_pred_str}'

    return parse_subj(e1_subj_str), parse_verb(e1_pred_str)


class AtomicKnowledgeBank(KnowledgeBankBase):

    def __init__(self,
                 path: str,
                 shuffle=False,  # note that shuffl=True loads huge dataset once at first, which is slow.
                 max_statements: Optional[int] = None):
        self._path = path
        self._shuffle = shuffle
        self._max_statements = max_statements

        super().__init__()

    def _load_statements(self, type_: StatementType) -> Iterable[Statement]:
        for stmt in _load_statements(self._path, max_statements=self._max_statements, shuffle=self._shuffle):
            if stmt.type != type_:
                continue
            yield stmt

    @property
    def _statement_types(self) -> List[StatementType]:
        return [
            # StatementType.Fa_Ga,
            # StatementType.Fa_Gb,
            StatementType.Fx_Gx,
        ]
