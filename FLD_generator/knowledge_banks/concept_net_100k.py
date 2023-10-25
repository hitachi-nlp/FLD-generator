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
)
from .utils import (
    parse_pred,
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
        then_subj_pos = None

        then_pred = None
        then_pred_left_modif = None
        then_pred_right_modif = None
        then_pred_pos = None

        if relation in [ConceptNet100kRelation.AtLocation,
                        ConceptNet100kRelation.CreatedBy,
                        ConceptNet100kRelation.DefinedAs,
                        ConceptNet100kRelation.LocatedNear,
                        ConceptNet100kRelation.MadeOf,
                        ConceptNet100kRelation.PartOf,
                        ConceptNet100kRelation.UsedFor,
                        ConceptNet100kRelation.HasProperty,
                        ConceptNet100kRelation.InstanceOf,
                        ConceptNet100kRelation.IsA]:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)

            if relation == ConceptNet100kRelation.AtLocation:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'located', None, f'at {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.CreatedBy:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'created', None, f'by {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.DefinedAs:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'defined', None, f'as {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.LocatedNear:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'located', None, f'near {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.MadeOf:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'made', None, f'of {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.PartOf:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'part', None, f'of {e1_str}', POS.NOUN

            elif relation == ConceptNet100kRelation.UsedFor:
                effect_poss = _WORD_UTILS.get_pos(e1_str.split(' ')[0])
                if len(effect_poss) == 0:
                    continue

                if POS.VERB in effect_poss:
                    if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'used', None, f'to {e1_str}', POS.PAST
                else:
                    if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'used', None, f'for {e1_str}', POS.PAST

            elif relation == ConceptNet100kRelation.HasProperty:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_pred(e1_str)

            elif relation in [ConceptNet100kRelation.InstanceOf,
                              ConceptNet100kRelation.IsA]:
                e1_words = e1_str.split(' ')
                if_pred = e1_words[-1]
                if_pred_left_modif = ' '.join(e1_words[:-1]) or None
                if_pred_right_modif = None
                if_pred_pos = POS.NOUN

        elif relation == ConceptNet100kRelation.CapableOf:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)
            if_pred_left_modif = 'can'
            e1_words = e1_str.split(' ')
            if_pred = e1_words[0]
            if_pred_right_modif = ' '.join(e1_words[1:]) or None
            if_pred_pos = POS.VERB

        elif relation == ConceptNet100kRelation.Causes:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str, might_be_gerund=True)
            if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = None, None, None, None

            then_subj, then_subj_left_modif, then_subj_right_modif, then_subj_pos = parse_subj(e1_str, might_be_gerund=True)
            then_pred, then_subj_left_modif, then_pred_right_modif, then_pred_pos = None, None, None, None

        elif relation == ConceptNet100kRelation.Desires:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)
            if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_pred(f'want to {e1_str}')

        elif relation == ConceptNet100kRelation.HasA:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)

            if e1_str.startswith('effect of '):
                effect_str = e1_str.replace('effect of ', '')
                effect_poss = _WORD_UTILS.get_pos(effect_str.split(' ')[0])
                if len(effect_poss) == 0:
                    continue

                if POS.VERB in effect_poss:
                    # trade with china    effect of enrich their government
                    if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_pred(effect_str)
                else:
                    if_pred = None
                    if_pred_left_modif = None
                    if_pred_right_modif = None
                    if_pred_pos = None

                    then_subj, then_subj_right_modif = effect_str.split(' ', 1)
                    then_subj_left_modif = None
                    then_subj_pos = POS.NOUN

                    then_pred = None
                    then_pred_left_modif = None
                    then_pred_right_modif = None
                    then_pred_pos = None
            else:
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = 'have', None, e1_str, POS.VERB

        elif relation in [ConceptNet100kRelation.HasPrerequisite,
                          ConceptNet100kRelation.HasFirstSubevent,
                          ConceptNet100kRelation.HasLastSubevent,
                          ConceptNet100kRelation.HasSubevent]:

            if relation == ConceptNet100kRelation.HasPrerequisite:
                _e0_str = f'want to {e0_str}'
                _e1_str = f'have to {e1_str}'

            else:
                _e0_str = e0_str
                _e1_str = e1_str

            if_subj = SomeoneX
            if_subj_left_modif = None
            if_subj_right_modif = None
            if_subj_pos = POS.NOUN

            if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_pred(_e0_str)

            then_subj = SomeoneX
            then_subj_left_modif = None
            then_subj_right_modif = None
            then_subj_pos = POS.NOUN

            then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = parse_pred(_e1_str)

        elif relation == ConceptNet100kRelation.NotCapableOf:
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)
            if_pred_left_modif = 'cannot'
            e1_words = e1_str.split(' ')
            if_pred = e1_words[0]
            if_pred_right_modif = ' '.join(e1_words[1:]) or None
            if_pred_pos = POS.VERB

        elif relation == ConceptNet100kRelation.NotDesires:
            _e0_str = e0_str.replace('person', SomeoneX)
            if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_subj(e0_str)
            if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_pred(f'does not want to {e1_str}')

        elif relation == ConceptNet100kRelation.NotHasA:
            continue

        elif relation == ConceptNet100kRelation.NotHasProperty:
            continue

        elif relation == ConceptNet100kRelation.NotIsA:
            continue

        elif relation == ConceptNet100kRelation.NotMadeOf:
            continue

        elif relation == ConceptNet100kRelation.CausesDesire:  # rare
            continue
        elif relation == [ConceptNet100kRelation.DesireOf]:  # rare
            continue
        elif relation == ConceptNet100kRelation.HasPainCharacter:  # rare
            continue
        elif relation == ConceptNet100kRelation.HasPainIntensity:  # rare
            continue
        elif relation == ConceptNet100kRelation.InheritsFrom:  # examples are low-quality
            continue
        elif relation == ConceptNet100kRelation.LocationOfAction:  # rare
            continue
        elif relation == ConceptNet100kRelation.MotivatedByGoal:  # examples are difficult to parse
            continue
        elif relation == ConceptNet100kRelation.ReceivesAction:  # examples are difficult to parse
            continue
        elif relation == ConceptNet100kRelation.RelatedTo:  # relationship is too ambiguous
            continue
        elif relation == ConceptNet100kRelation.SymbolOf:  # relationship is too ambiguous
            continue
        else:
            raise ValueError()

        if_statement = DeclareStatement(
            subj=if_subj,
            subj_right_modif=if_subj_right_modif,
            subj_left_modif=if_subj_left_modif,
            subj_pos=if_subj_pos,

            pred=if_pred,
            pred_left_modif=if_pred_left_modif,
            pred_right_modif=if_pred_right_modif,
            pred_pos=if_pred_pos,
        )

        if then_subj is None:
            statement = if_statement
            statement.relation = relation.value
        else:
            then_statement = DeclareStatement(
                subj=then_subj,
                subj_right_modif=then_subj_right_modif,
                subj_left_modif=then_subj_left_modif,
                subj_pos=then_subj_pos,

                pred=then_pred,
                pred_left_modif=then_pred_left_modif,
                pred_right_modif=then_pred_right_modif,
                pred_pos=then_pred_pos,
            )

            statement = IfThenStatement(
                if_statement=if_statement,
                then_statement=then_statement,
                relation=relation.value,
            )

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

    def _load_statements(self, type_: StatementType) -> Iterable[Statement]:
        for stmt in _load_statements(self._path, max_statements=self._max_statements, shuffle=self._shuffle):
            if stmt.type != type_:
                continue
            yield stmt

    @property
    def _statement_types(self) -> List[StatementType]:
        return [
            StatementType.Fa,
            StatementType.F_G,
            StatementType.Fx_Gx,
        ]
