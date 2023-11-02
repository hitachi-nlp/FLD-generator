from typing import Optional, Iterable, List, Dict, Tuple
import re
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


_TRANSLATIONS: Dict[str, List[Tuple[str, POS]]] = {
    # you can list possible relations by: 
    # gawk '{print $3}' ./res/knowledge_banks/DBpedia500/train1.txt | sort | uniq -c | sort -n -r > ./res/knowledge_banks/DBpedia500/relations.train1.txt"

    # XXX: WHEN ADDING A TRANSLATION, ALSO ADD POSTPROCESSING in "postprocess_translation"

    'team': [
        ('belongs to', POS.VERB, False),
    ],
    'birthPlace': [
        ('was born in', POS.PAST_PARTICLE, False),
    ],
    'genre': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'recordLabel': [
        ('belongs to', POS.VERB, False),
    ],
    'starring': [
        ('starrs', POS.VERB, False),
        ('starred in', POS.VERB, True),
    ],
    'country': [
        ('is in', POS.ADJ, False),
    ],
    'producer': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'associatedMusicalArtist': [
        # relation is ambiguous
    ],
    'associatedBand': [
        # relation is ambiguous
    ],
    'deathPlace': [
        ('died in', POS.VERB, False),
    ],
    'type': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'isPartOf': [
        ('is part of', POS.NOUN, False),
    ],
    'occupation': [
        ('work as', POS.VERB, False),
        ('is', POS.NOUN, False),
    ],
    'writer': [
        ('is wrote by', POS.PAST_PARTICLE, False),
        ('wrote', POS.VERB, True),
    ],
    'timeZone': [
        # relation is too maniac
    ],
    'hometown': [
        ('was born in', POS.PAST_PARTICLE, False),
    ],
    'subsequentWork': [
        ('is previous work before', POS.NOUN, False),
        ('is next work after', POS.NOUN, True),
    ],
    'battle': [
        ('fought in', POS.VERB, False),
    ],
    'location': [
        ('is located in', POS.PAST_PARTICLE, False),
    ],
    'previousWork': [
        ('is next work after', POS.NOUN, False),
        ('is previous work before', POS.NOUN, True),
    ],
    'almaMater': [
        ('graduated from', POS.VERB, False),
    ],
    'format': [
        # relation is too maniac
    ],
    'successor': [
        ('is predecessor of', POS.NOUN, False),
        ('is successor of', POS.NOUN, True),
    ],
    'position': [
        ('work as', POS.VERB, False),
    ],
    'instrument': [
        ('is', POS.NOUN, False),
    ],
    'artist': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'formerTeam': [
        ('previously worked in', POS.VERB, False),
    ],
    'award': [
        ('was awarded', POS.PAST_PARTICLE, False),
    ],
    'managerClub': [
        ('manages', POS.VERB, False),
        ('is managed by', POS.PAST_PARTICLE, True),
    ],
    'recordedIn': [
        ('was recorded in', POS.PAST_PARTICLE, False),
    ],
    'director': [
        ('was directed by', POS.PAST_PARTICLE, False),
        ('is director of', POS.NOUN, True),
    ],
    'neighboringMunicipality': [
        ('is near to', POS.ADJ, False),
        ('is near to', POS.ADJ, True),
    ],
    'predecessor': [
        ('is successor of', POS.NOUN, False),
        ('is predecessor of', POS.NOUN, True),
    ],
    'distributor': [
        ('is distributed by', POS.PAST_PARTICLE, False),
        ('distributed', POS.VERB, False),
    ],
    'sisterStation': [
        ('is sister station of', POS.NOUN, False),
        ('is sister station of', POS.NOUN, True),
    ],
    'language': [
        ('is spoken in', POS.PAST_PARTICLE, True),
    ],
    'musicalArtist': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'party': [
        ('belongs to', POS.VERB, False),
    ],
    'musicalBand': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'musicComposer': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'nationality': [
        ('was born in', POS.PAST_PARTICLE, False),
    ],
    'album': [
        # ??
    ],
    'family': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'order': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'class': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'city': [
        ('is located in', POS.PAST_PARTICLE, False),
    ],
    'computingPlatform': [
        ('can be played on', POS.PAST_PARTICLE, False),
    ],
    'residence': [
        ('lived in', POS.VERB, False),
    ],
    'formerBandMember': [
        ('played in', POS.VERB, True),
    ],
    'product': [
        ('produces', POS.VERB, False),
    ],
    'commander': [
        ('commanded in', POS.VERB, True),
    ],
    'region': [
        ('lived in', POS.VERB, False),
    ],
    'religion': [
        ('believes in', POS.VERB, False),
    ],
    'influencedBy': [
        ('was influenced by', POS.PAST_PARTICLE, False),
    ],
    'race': [
        ('raced in', POS.VERB, False),
    ],
    'bandMember': [
        ('played in', POS.VERB, True),
    ],
    'cinematography': [
        ('was created by', POS.PAST_PARTICLE, False),
        ('created', POS.VERB, True),
    ],
    'state': [
        ('is located in', POS.PAST_PARTICLE, False),
    ],
    'industry': [
        ('operates in', POS.VERB, False),
    ],
    'guest': [
        ('took guest role in', POS.VERB, True),
    ],
    'phylum': [
        ('is', POS.NOUN, False),
        ('is kind of', POS.NOUN, False),
    ],
    'spouse': [
        ('got married to', POS.VERB, False),
        ('got married to', POS.VERB, True),
    ],
    'routeJunction': [
        ('is route to', POS.NOUN, False),
    ],
    'field': [
        ('specializes in', POS.VERB, False),
    ],
    'militaryBranch': [
        ('worked in', POS.VERB, False),
    ],
    'restingPlace': [
        ('died in', POS.VERB, False),
    ],
    # 'ground': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'league': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'editing': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'part': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'influenced': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'publisher': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'populationPlace': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'profession': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'network': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'company': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'affiliation': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'district': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'owner': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'series': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'keyPerson': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'parent': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'related': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'author': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'governmentType': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'headquarter': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'broadcastArea': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'president': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'voice': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'locationCountry': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'leaderName': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'creator': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'locationCity': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'composer': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'knownFor': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'assembly': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'place': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'primeMinister': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'owningCompany': [
    #     ('hoge', POS.VERB, False),
    # ],
    # 'literaryGenre': [
    #     ('hoge', POS.VERB, False),
    # ],
}


# @profile
def _load_statements(path: str,
                     max_statements: Optional[int] = None,
                     shuffle=False) -> Iterable[Statement]:
    logger.info('loading DBpedia statements from file "%s"', path)

    if shuffle:
        lines = open(path).readlines()
        random.shuffle(lines)
    else:
        lines = open(path)

    lines = down_sample_streaming(lines,
                                  lambda line: line.rstrip('\n').split('\t')[2],
                                  distrib='sqrt',
                                  min_sampling_prob=0.1,
                                  burn_in=1000)

    for i_line, line in enumerate(lines):
        if max_statements is not None and i_line >= max_statements:
            break
        line = _normalize(line)

        e0_str, e1_str, rel_str = line.rstrip('\n').split('\t')
        if rel_str not in _TRANSLATIONS:
            continue

        negated = False
        pred_translations = _TRANSLATIONS[rel_str]
        if len(pred_translations) == 0:
            continue

        pred_translation, pred_required_pos, is_reverse = random.choice(pred_translations)

        if is_reverse:
            subj_str = e1_str
            pred_str = e0_str
        else:
            subj_str = e0_str
            pred_str = e1_str

        # subj, subj_left_modif, subj_right_modif = parse(subj_str, 'rightmost')
        # subj_pos = POS.NOUN
        subj, subj_left_modif, subj_right_modif, subj_pos = parse_as_subj(subj_str)

        pred_translation_with_modif = f'{pred_translation} {pred_str}' if pred_translation else pred_str
        pred, pred_left_modif, pred_right_modif, pred_pos = parse_as_pred(pred_translation_with_modif, prioritize_pos=pred_required_pos)

        try:
            statement = DeclareStatement(
                subj=subj,
                subj_right_modif=subj_right_modif,
                subj_left_modif=subj_left_modif,
                subj_pos=subj_pos,

                pred=pred,
                pred_left_modif=pred_left_modif,
                pred_right_modif=pred_right_modif,
                pred_pos=pred_pos,
                negated=negated,
                relation=rel_str,
            )
        except Exception as e:
            logger.warning('failed to parse line "%s"', line)
            continue

        logger.info('load a statement from DBpedia')
        yield statement


def _normalize(line: str) -> str:
    line = line.replace('_', ' ')
    line = line.replace('The', 'the')
    line = re.sub(r'\([^\)]*\)', '', line)
    return line


class DBpedia(KnowledgeBankBase):

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
            StatementType.Fa,
            # StatementType.nFa,
            # StatementType.Fx_Gx,
            # StatementType.Fx_nGx,
        ]

    def postprocess_translation(self, translation: str) -> str:
        org = translation
        translation = translation\
            .replace('is born in', 'was born in')\
            .replace('dies in', 'died in')\
            .replace('starrs in', 'starred in')\
            .replace('is created by', 'was created by')\
            .replace('writes', 'wrote')\
            .replace('fights in', 'fought in')\
            .replace('graduates from', 'graduated from')\
            .replace('previously works in', 'previously worked in')\
            .replace('is awarded', 'was awarded')\
            .replace('is recorded in', 'was recorded in')\
            .replace('is directed by', 'was directed by')\
            .replace('distributes', 'distributed')\
            .replace('lives in', 'lived in')\
            .replace('plays in', 'played in')\
            .replace('is influenced by', 'was influenced by')\
            .replace('races in', 'raced in')\
            .replace('takes guest role in', 'took guest role in')\
            .replace('gets married', 'got married')\
            .replace('works in', 'worked in')
        # if org != translation:
        #     logger.critical('"%s" -> "%s"', org, translation)
        return translation
