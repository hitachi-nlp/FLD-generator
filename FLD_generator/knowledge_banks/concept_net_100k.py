from typing import Optional, Iterable, List
from enum import Enum
import logging
import random

from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.utils import down_sample_streaming
from .base import KnowledgeBankBase
from .statement import (
    Statement,
    StatementType,
    DeclareStatement,
    IfThenStatement,
    SomeoneX,
    SomeoneY,
    SomethingX,
    SomethingY,
)
from .utils import (
    parse_as_pred,
    parse_as_subj,
    parse,
)

import line_profiling


logger = logging.getLogger(__name__)

_WORD_UTILS = WordUtil('eng')


class ConceptNet100kRelation(Enum):
    #   14925 IsA
    #   14380 AtLocation
    #   13221 UsedFor
    #    9894 CapableOf
    #    7901 HasProperty
    #    6463 HasSubevent
    #    5561 HasPrerequisite
    #    4614 Causes
    #    3504 HasA
    #    3404 ReceivesAction
    #    2983 MotivatedByGoal
    #    2782 DefinedAs
    #    1742 Desires
    #    1689 PartOf
    #    1626 NotDesires
    #    1043 NotCapableOf
    #     970 CausesDesire
    #     961 HasFirstSubevent
    #     592 HasLastSubevent
    #     577 MadeOf
    #     339 NotHasProperty
    #     159 SymbolOf
    #     152 NotIsA
    #     149 CreatedBy
    #     120 NotHasA
    #      89 RelatedTo
    #      69 InstanceOf
    #      56 InheritsFrom
    #      14 DesireOf
    #      13 NotMadeOf
    #       3 LocationOfAction
    #       3 LocatedNear
    #       1 HasPainIntensity
    #       1 HasPainCharacter

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


_Fx_Gx_relations = [
    ConceptNet100kRelation.AtLocation,
    ConceptNet100kRelation.CreatedBy,
    ConceptNet100kRelation.DefinedAs,
    ConceptNet100kRelation.LocatedNear,
    ConceptNet100kRelation.MadeOf,
    ConceptNet100kRelation.NotMadeOf,
    ConceptNet100kRelation.PartOf,
    ConceptNet100kRelation.UsedFor,
    ConceptNet100kRelation.HasProperty,
    ConceptNet100kRelation.NotHasProperty,
    ConceptNet100kRelation.InstanceOf,
    ConceptNet100kRelation.IsA,
    ConceptNet100kRelation.NotIsA,

    ConceptNet100kRelation.CapableOf,
    ConceptNet100kRelation.NotCapableOf,
    ConceptNet100kRelation.Desires,
    ConceptNet100kRelation.NotDesires,
    ConceptNet100kRelation.HasPrerequisite,
    ConceptNet100kRelation.HasFirstSubevent,
    ConceptNet100kRelation.HasLastSubevent,
    ConceptNet100kRelation.HasSubevent,
]


# @profile
def _load_statements(path: str,
                     max_statements: Optional[int] = None,
                     shuffle=False) -> Iterable[Statement]:
    logger.info('loading ConceptNet100k statements from file "%s"', path)

    if shuffle:
        lines = open(path).readlines()
        random.shuffle(lines)
    else:
        lines = open(path)

    lines = down_sample_streaming(lines,
                                  lambda line: line.rstrip('\n').split('\t')[0],
                                  distrib='sqrt',
                                  min_sampling_prob=0.1,
                                  burn_in=1000)

    for i_line, line in enumerate(lines):
        if max_statements is not None and i_line >= max_statements:
            break
        line = _normalize(line)

        rel_str, e0_str, e1_str = line.rstrip('\n').split('\t')
        negated = False
        relation = ConceptNet100kRelation(rel_str)

        if relation in _Fx_Gx_relations:

            if_subj = SomethingX
            if_subj_left_modif = None
            if_subj_right_modif = None
            if_subj_pos = POS.NOUN

            then_subj = SomethingX
            then_subj_left_modif = None
            then_subj_right_modif = None
            then_subj_pos = POS.NOUN

            if relation in [ConceptNet100kRelation.AtLocation,
                            ConceptNet100kRelation.CreatedBy,
                            ConceptNet100kRelation.DefinedAs,
                            ConceptNet100kRelation.LocatedNear,
                            ConceptNet100kRelation.MadeOf,
                            ConceptNet100kRelation.NotMadeOf,
                            ConceptNet100kRelation.PartOf,
                            ConceptNet100kRelation.UsedFor,
                            ConceptNet100kRelation.HasProperty,
                            ConceptNet100kRelation.NotHasProperty,
                            ConceptNet100kRelation.InstanceOf,
                            ConceptNet100kRelation.IsA,
                            ConceptNet100kRelation.NotIsA]:

                if_pred, if_pred_left_modif, if_pred_right_modif = parse(e0_str, 'rightmost')
                if_pred_pos = POS.NOUN

                if relation == ConceptNet100kRelation.AtLocation:
                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'located', None, f'at {e1_str}', POS.PAST_PARTICLE

                elif relation == ConceptNet100kRelation.CreatedBy:
                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'created', None, f'by {e1_str}', POS.PAST_PARTICLE

                elif relation == ConceptNet100kRelation.DefinedAs:
                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'defined', None, f'as {e1_str}', POS.PAST_PARTICLE

                elif relation == ConceptNet100kRelation.LocatedNear:
                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'located', None, f'near {e1_str}', POS.PAST_PARTICLE

                elif relation in [ConceptNet100kRelation.MadeOf,
                                  ConceptNet100kRelation.NotMadeOf]:
                    if relation == ConceptNet100kRelation.NotMadeOf:
                        negated = True

                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'made', None, f'of {e1_str}', POS.PAST_PARTICLE

                elif relation == ConceptNet100kRelation.PartOf:
                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'part', None, f'of {e1_str}', POS.NOUN

                elif relation == ConceptNet100kRelation.UsedFor:
                    effect_poss = _WORD_UTILS.get_pos(e1_str.split(' ')[0])
                    if len(effect_poss) == 0:
                        continue

                    if POS.VERB in effect_poss:
                        then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'used', None, f'to {e1_str}', POS.PAST_PARTICLE
                    else:
                        then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'used', None, f'for {e1_str}', POS.PAST_PARTICLE

                elif relation in [ConceptNet100kRelation.HasProperty,
                                  ConceptNet100kRelation.NotHasProperty]:
                    if relation == ConceptNet100kRelation.NotHasProperty:
                        negated = True

                    if POS.VERB in _WORD_UTILS.get_pos(e1_str.split(' ')[0]):
                        then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = parse_as_pred(f'{e1_str}')
                    else:
                        then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = parse_as_pred(f'is {e1_str}')

                elif relation in [ConceptNet100kRelation.InstanceOf,
                                  ConceptNet100kRelation.IsA,
                                  ConceptNet100kRelation.NotIsA]:
                    if relation == ConceptNet100kRelation.NotIsA:
                        negated = True

                    then_pred, then_pred_left_modif, then_pred_right_modif = parse(e1_str, 'rightmost')
                    then_pred_pos = POS.NOUN

                else:
                    raise ValueError()

            elif relation in [ConceptNet100kRelation.CapableOf,
                              ConceptNet100kRelation.NotCapableOf]:
                if relation == ConceptNet100kRelation.NotCapableOf:
                    negated = True

                if_pred, if_pred_left_modif, if_pred_right_modif = parse(e0_str, 'rightmost')
                if_pred_pos = POS.NOUN

                then_pred, _, then_pred_right_modif = parse(e1_str, 'leftmost')
                then_pred_left_modif = 'can'
                then_pred_pos = POS.VERB

            elif relation in [ConceptNet100kRelation.Desires,
                              ConceptNet100kRelation.NotDesires]:
                if relation == ConceptNet100kRelation.NotDesires:
                    negated = True

                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_as_subj(e0_str)
                then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = parse_as_pred(f'want to {e1_str}')

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

                # the seems to be human
                if_subj = SomeoneX
                then_subj = SomeoneX

                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_as_pred(_e0_str)
                then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = parse_as_pred(_e1_str)

            else:
                raise ValueError(relation)

        else:
            if_subj = None
            if_subj_left_modif = None
            if_subj_right_modif = None
            if_subj_pos = None

            if_pred = None
            if_pred_left_modif = None
            if_pred_right_modif = None
            if_pred_pos = None

            then_subj = None
            then_subj_left_modif = None
            then_subj_right_modif = None
            then_subj_pos = None

            then_pred = None
            then_pred_left_modif = None
            then_pred_right_modif = None
            then_pred_pos = None

            if relation in [ConceptNet100kRelation.HasA,
                            ConceptNet100kRelation.NotHasA]:
                if relation == ConceptNet100kRelation.NotHasA:
                    negated = True

                if e1_str.startswith('effect of '):
                    effect_str = e1_str.replace('effect of ', '')
                    effect_poss = _WORD_UTILS.get_pos(effect_str.split(' ')[0])
                    if len(effect_poss) == 0:
                        continue

                    if POS.VERB in effect_poss:
                        # trade with china    effect of enrich their government
                        if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_as_subj(e0_str)
                        if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_as_pred(effect_str)

                    else:
                        if_subj, if_subj_left_modif, if_subj_right_modif = parse(e0_str, 'leftmost')
                        if_subj_pos = POS.NOUN

                        then_subj, then_subj_left_modif, then_subj_right_modif = parse(effect_str, 'leftmost')
                        then_subj_pos = POS.NOUN
                else:
                    if_subj = SomethingX
                    if_subj_left_modif = None
                    if_subj_right_modif = None
                    if_subj_pos = POS.NOUN

                    if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = parse_as_subj(e0_str)

                    then_subj = SomethingX
                    then_subj_left_modif = None
                    then_subj_right_modif = None
                    then_subj_pos = POS.NOUN

                    then_pred, then_pred_left_modif, then_pred_right_modif, then_pred_pos = 'have', None, e1_str, POS.VERB

            elif relation == ConceptNet100kRelation.Causes:
                if_subj, if_subj_left_modif, if_subj_right_modif, if_subj_pos = parse_as_subj(e0_str, might_be_gerund=True)
                if_pred, if_pred_left_modif, if_pred_right_modif, if_pred_pos = None, None, None, None

                then_subj, then_subj_left_modif, then_subj_right_modif, then_subj_pos = parse_as_subj(e1_str, might_be_gerund=True)
                then_pred, then_subj_left_modif, then_pred_right_modif, then_pred_pos = None, None, None, None

            elif relation == ConceptNet100kRelation.CausesDesire:  # rare
                continue
            elif relation == ConceptNet100kRelation.DesireOf:  # rare
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
                raise ValueError(str(relation))

        try:
            if_statement = DeclareStatement(
                subj=if_subj,
                subj_right_modif=if_subj_right_modif,
                subj_left_modif=if_subj_left_modif,
                subj_pos=if_subj_pos,

                pred=if_pred,
                pred_left_modif=if_pred_left_modif,
                pred_right_modif=if_pred_right_modif,
                pred_pos=if_pred_pos,
                negated=False,
            )
        except Exception as e:
            logger.warning('failed to parse line "%s"', line)
            continue
            

        if then_subj is None:
            statement = if_statement
            statement.negated = negated
            statement.relation = relation.value
        else:
            try:
                then_statement = DeclareStatement(
                    subj=then_subj,
                    subj_right_modif=then_subj_right_modif,
                    subj_left_modif=then_subj_left_modif,
                    subj_pos=then_subj_pos,

                    pred=then_pred,
                    pred_left_modif=then_pred_left_modif,
                    pred_right_modif=then_pred_right_modif,
                    pred_pos=then_pred_pos,
                    negated=negated,
                )
            except Exception as e:
                logger.warning('failed to parse line "%s"', line)
                continue


            statement = IfThenStatement(
                if_statement=if_statement,
                then_statement=then_statement,
                relation=relation.value,
                negated=False,
            )

        logger.info('load a statement from ConceptNet100k')
        yield statement


def _normalize(line: str) -> str:
    line = line.replace(' be ', ' is ')
    return line


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
        for stmt in _load_statements(self._path, max_statements=self._max_statements, shuffle=self._shuffle):
            yield stmt

    @property
    def _statement_types(self) -> List[StatementType]:
        return [
            # 82 type=StatementType.Fa
            # 4624 type=StatementType.F_G
            # 84027 type=StatementType.Fx_Gx
            # 3293 type=StatementType.Fx_nGx

            StatementType.F_G,
            StatementType.Fx_Gx,
            StatementType.Fx_nGx,
        ]

    def postprocess_translation(self, translation: str) -> str:
        return translation
