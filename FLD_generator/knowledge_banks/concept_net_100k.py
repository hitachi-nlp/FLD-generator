from typing import Optional, Iterable, List
from enum import Enum
import logging
import random

from FLD_generator.word_banks.word_utils import WordUtil, POS
from .base import KnowledgeBankBase
from .statement import (
    Statement,
    StatementType,
    DeclareStatement,
    IfThenStatement,
    SomeoneX,
    SomeoneY,
    is_meaningful_stmt,
)
from .utils import (
    parse_verb,
    parse_subj,
)


logger = logging.getLogger(__name__)

_WORD_UTILS = WordUtil('eng')
_PersonX = 'PersonX'
_PersonY = 'PersonY'


class ConceptNet100kRelation(Enum):
    AtLocation = 'AtLocation'  # 28760
    CapableOf = 'CapableOf'  # 19788
    Causes = 'Causes'  # 9228
    CausesDesire = 'CausesDesire'  # 1940
    CreatedBy = 'CreatedBy'  # 298
    DefinedAs = 'DefinedAs'  # 5564
    DesireOf = 'DesireOf'  # 28
    Desires = 'Desires'  # 3484
    HasA = 'HasA'  # 7008
    HasFirstSubevent = 'HasFirstSubevent'  # 1922
    HasLastSubevent = 'HasLastSubevent'  # 1184
    HasPainCharacter = 'HasPainCharacter'  # 2
    HasPainIntensity = 'HasPainIntensity'  # 2
    HasPrerequisite = 'HasPrerequisite'  # 11122
    HasProperty = 'HasProperty'  # 15802
    HasSubevent = 'HasSubevent'  # 12926
    InheritsFrom = 'InheritsFrom'  # 112
    InstanceOf = 'InstanceOf'  # 138
    IsA = 'IsA'  # 29850
    LocatedNear = 'LocatedNear'  # 6
    LocationOfAction = 'LocationOfAction'  # 6
    MadeOf = 'MadeOf'  # 1154
    MotivatedByGoal = 'MotivatedByGoal'  # 5966
    NotCapableOf = 'NotCapableOf'  # 2086
    NotDesires = 'NotDesires'  # 3252
    NotHasA = 'NotHasA'  # 240
    NotHasProperty = 'NotHasProperty'  # 678
    NotIsA = 'NotIsA'  # 304
    NotMadeOf = 'NotMadeOf'  # 26
    PartOf = 'PartOf'  # 3378
    ReceivesAction = 'ReceivesAction'  # 6808
    RelatedTo = 'RelatedTo'  # 178
    SymbolOf = 'SymbolOf'  # 318
    UsedFor = 'UsedFor'  # 26442


def _load_statements(path: str,
                     max_statements: Optional[int] = None,
                     shuffle=False) -> Iterable[Statement]:
    logger.info('loading ConceptNet100k statements from file "%s"', path)

    if shuffle:
        lines = open(path).readlines()
        random.shuffle(lines)
    else:
        lines = open(path)

    for i_line, line in enumerate(lines):
        if max_statements is not None and i_line >= max_statements:
            break
        line = line.replace(' be ', ' is ')

        rel_str, e0_str, e1_str = line.rstrip('\n').split('\t')
        relation = ConceptNet100kRelation(rel_str)

        then_subj = None
        then_subj_right_modif = None
        then_subj_left_modif = None
        then_verb = None
        then_verb_left_modif = None
        then_verb_right_modif = None

        if relation == ConceptNet100kRelation.AtLocation:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'located at {e1_str}'

        elif relation == ConceptNet100kRelation.CapableOf:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, _, if_verb_right_modif = parse_verb(e1_str)
            if_verb_left_modif = 'can'

        elif relation == ConceptNet100kRelation.Causes:
            continue

        elif relation == ConceptNet100kRelation.CausesDesire:
            continue

        elif relation == ConceptNet100kRelation.CreatedBy:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'created by {e1_str}'

        elif relation == ConceptNet100kRelation.DefinedAs:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'defined as {e1_str}'

        elif relation == [ConceptNet100kRelation.DesireOf]:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb = 'want'
            if_verb_left_modif = None

            effect_poss = _WORD_UTILS.get_pos(e1_str.split(' ')[0])
            if len(effect_poss) == 0:
                continue

            if POS.VERB in effect_poss:
                if_verb_right_modif = f'to {e1_str}'
            else:
                if_verb_right_modif = e1_str

        elif relation == ConceptNet100kRelation.Desires:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'want', None, f'to {e1_str}'

        elif relation == ConceptNet100kRelation.HasA:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)

            if e1_str.startswith('effect of '):
                effect_str = e1_str.replace('effect of ', '')
                effect_poss = _WORD_UTILS.get_pos(effect_str.split(' ')[0])
                if len(effect_poss) == 0:
                    continue

                if POS.VERB in effect_poss:
                    # trade with china    effect of enrich their government
                    if_verb, if_verb_left_modif, if_verb_right_modif = parse_verb(effect_str)
                else:
                    if_verb = 'cause'
                    if_verb_left_modif = None
                    if_verb_right_modif = effect_str
            else:
                if_verb, if_verb_left_modif, if_verb_right_modif = 'have', None, e1_str

        elif relation == ConceptNet100kRelation.HasFirstSubevent:
            continue

        elif relation == ConceptNet100kRelation.HasLastSubevent:
            continue

        elif relation == ConceptNet100kRelation.HasPainCharacter:
            # is rare
            continue

        elif relation == ConceptNet100kRelation.HasPainIntensity:
            # is rare
            continue

        elif relation == ConceptNet100kRelation.HasPrerequisite:
            if_subj = SomeoneX
            if_subj_left_modif = None
            if_subj_right_modif = None
            if_verb, if_verb_left_modif, if_verb_right_modif = parse_verb(f'want to {e0_str}')

            then_subj = SomeoneX
            then_subj_left_modif = None
            then_subj_right_modif = None
            then_verb, then_verb_left_modif, then_verb_right_modif = parse_verb(f'have to {e1_str}')

        elif relation == ConceptNet100kRelation.HasProperty:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, e1_str

        elif relation == ConceptNet100kRelation.HasSubevent:
            continue

        elif relation == ConceptNet100kRelation.InheritsFrom:
            # examples seems to be low-quality
            continue

        elif relation == ConceptNet100kRelation.InstanceOf:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, e1_str

        elif relation == ConceptNet100kRelation.IsA:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, e1_str

        elif relation == ConceptNet100kRelation.LocatedNear:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'located near {e1_str}'

        elif relation == ConceptNet100kRelation.LocationOfAction:
            # rare case
            pass

        elif relation == ConceptNet100kRelation.MadeOf:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'made of {e1_str}'

        elif relation == ConceptNet100kRelation.MotivatedByGoal:
            # difficult to parse
            continue

        elif relation == ConceptNet100kRelation.NotCapableOf:
            continue

        elif relation == ConceptNet100kRelation.NotDesires:
            pass

        elif relation == ConceptNet100kRelation.NotHasA:
            continue

        elif relation == ConceptNet100kRelation.NotHasProperty:
            continue

        elif relation == ConceptNet100kRelation.NotIsA:
            continue

        elif relation == ConceptNet100kRelation.NotMadeOf:
            continue

        elif relation == ConceptNet100kRelation.PartOf:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif, if_verb_right_modif = 'is', None, f'part of {e1_str}'

        elif relation == ConceptNet100kRelation.ReceivesAction:
            # difficult to parse
            continue

        elif relation == ConceptNet100kRelation.RelatedTo:
            # relationship is too ambiguous
            continue

        elif relation == ConceptNet100kRelation.SymbolOf:
            # relationship is too ambiguous
            continue

        elif relation == ConceptNet100kRelation.UsedFor:
            if_subj, if_subj_left_modif, if_subj_right_modif = parse_subj(e0_str)
            if_verb, if_verb_left_modif = 'is', None

            effect_poss = _WORD_UTILS.get_pos(e1_str.split(' ')[0])
            if len(effect_poss) == 0:
                continue
            else:
                if POS.VERB in effect_poss:
                    if_verb_right_modif = f'used to {e1_str}'
                else:
                    if_verb_right_modif = f'used for {e1_str}'
        else:
            raise ValueError()

        if if_verb is None:
            continue

        if_statement = DeclareStatement(
            subj=if_subj,
            subj_right_modif=if_subj_right_modif,
            subj_left_modif=if_subj_left_modif,
            verb=if_verb,
            verb_left_modif=if_verb_left_modif,
            verb_right_modif=if_verb_right_modif,
        )

        if then_verb is None:
            statement = if_statement
            statement.relation = relation.value
        else:
            then_statement = DeclareStatement(
                subj=then_subj,
                subj_right_modif=then_subj_right_modif,
                subj_left_modif=then_subj_left_modif,
                verb=then_verb,
                verb_left_modif=then_verb_left_modif,
                verb_right_modif=then_verb_right_modif,
            )

            statement = IfThenStatement(
                if_statement=if_statement,
                then_statement=then_statement,
                relation=relation.value,
            )

        if not is_meaningful_stmt(statement):
            continue

        yield statement


class ConceptNet100kKnowledgeBank(KnowledgeBankBase):

    def __init__(self,
                 path: str,
                 shuffle=False,  # note that shuffl=True loads huge dataset once at first, which is slow.
                 max_statements: Optional[int] = None):
        self._path = path
        self._shuffle = shuffle
        self._max_statements = max_statements

        super().__init__()

    def _load_statements(self) -> Iterable[Statement]:
        return _load_statements(self._path, max_statements=self._max_statements, shuffle=self._shuffle)

    @property
    def _statement_types(self) -> List[StatementType]:
        return [
            StatementType.Fa,
        ]
