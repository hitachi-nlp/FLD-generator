from typing import List, Dict, Tuple, Optional, Iterable
import re
from enum import Enum
import logging
import random

from pydantic import BaseModel
from tqdm import tqdm

from FLD_generator.formula import Formula
from FLD_generator.word_banks.word_utils import WordUtil, POS
from FLD_generator.person_names import get_person_names
from FLD_generator.utils import RandomCycle
from FLD_generator.translators.base import (
    Phrase,
    PredicatePhrase,
    ConstantPhrase,
)
from .base import CommonsenseBankBase
from .utils import (
    is_simple_unary_implication_shared_const,
    is_simple_unary_implication_unshared_const,
    is_simple_universal_implication,
    get_if_then_constants,
    get_if_then_predicates,
)


logger = logging.getLogger(__name__)

_WORD_UTILS = WordUtil('eng')
_PersonX = 'PersonX'
_PersonY = 'PersonY'


class AtomicStatement(BaseModel):
    subj: str
    verb: str
    verb_left_modif: Optional[str] = None
    verb_right_modif: Optional[str] = None


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


class AtomicIfThenStatement(BaseModel):

    if_statement: AtomicStatement
    then_statement: AtomicStatement
    relation: AtomicRelation

    @property
    def type(self) -> str:

        def have(rep: Optional[str], key: str) -> str:
            if rep is None:
                return False
            return rep.find(key) >= 0

        char0 = 'o'
        if have(self.if_statement.subj, _PersonX):
            char0 = 'x'
        elif have(self.if_statement.subj, _PersonY):
            char0 = 'y'

        char1 = 'o'
        if have(self.if_statement.verb_right_modif, _PersonX):
            char1 = 'x'
        elif have(self.if_statement.verb_right_modif, _PersonY):
            char1 = 'y'

        char2 = 'o'
        if have(self.then_statement.subj, _PersonX):
            char2 = 'x'
        elif have(self.then_statement.subj, _PersonY):
            char2 = 'y'

        char3 = 'o'
        if have(self.then_statement.verb_right_modif, _PersonX):
            char3 = 'x'
        elif have(self.then_statement.verb_right_modif, _PersonY):
            char3 = 'y'

        return f'{char0}{char1}_{char2}{char3}'


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
_E1_IS_IF_RELATIONS = [
]


def load_atomic_if_then_statements(path: str, max_statements: Optional[int] = None) -> Iterable[AtomicIfThenStatement]:

    def _find_verb(words: List[str]) -> Optional[int]:
        for i_word, word in enumerate(words):
            if _is_verb(word):
                return i_word
        return None

    def _split_by_verb(pred_words: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        verb_idx = _find_verb(pred_words)
        if verb_idx is None:
            logger.info('Could\'nt find verb from words: %s. This can be due to the incomplete detection function. The statement will be skipped.', str(pred_words))
            return None, None, None
        else:
            return (
                ' '.join(pred_words[:verb_idx]) or None,
                pred_words[verb_idx],
                ' '.join(pred_words[verb_idx + 1:]) or None,
            )

    logger.info('loading ATOMIC statements from file "%s"', path)

    for i_line, line in tqdm(enumerate(open(path)), total=max_statements):
        if max_statements is not None and i_line >= max_statements:
            break
        e0_str, rel_str, e1_str = line.rstrip('\n').split('\t')
        e0_str = _normalize_person(e0_str.lower())
        e1_str = _normalize_person(e1_str.lower())
        if e1_str == 'none':
            continue
        if line.find('___') >= 0:
            continue

        relation = AtomicRelation(rel_str)

        e0_subj, *e0_pred_words = e0_str.split('-')
        if e0_subj != _PersonX:
            raise NotImplementedError()

        e0_verb_left_modif, e0_verb, e0_verb_right_modif = _split_by_verb(e0_pred_words)
        if e0_verb is None:
            continue

        e1_words = e1_str.split('-')
        e1_subj = e1_words[0] if e1_words[0] in [_PersonX, _PersonY] else None
        e1_pred_words = e1_words[1:] if e1_words[0] in [_PersonX, _PersonY] else e1_words

        if relation in _E0_IS_IF_RELATIONS:
            if_subj = e0_subj
            if_verb = e0_verb
            if_verb_left_modif = e0_verb_left_modif
            if_verb_right_modif = e0_verb_right_modif

            # decide subject by "x" or "o"
            if relation in [AtomicRelation.xEffect, AtomicRelation.xReact, AtomicRelation.xWant,
                            AtomicRelation.xAttr, AtomicRelation.xNeed, AtomicRelation.xIntent]:
                then_subj = _PersonX

            elif relation in [AtomicRelation.oEffect, AtomicRelation.oReact, AtomicRelation.oWant]:
                if e1_subj is not None:
                    then_subj = e1_subj
                else:
                    if if_verb_right_modif is not None and if_verb_right_modif.find(_PersonY) >= 0:
                        then_subj = _PersonY
                    else:
                        then_subj = 'others'
            else:
                raise Exception()

            # decide pred
            if relation in [AtomicRelation.xEffect, AtomicRelation.oEffect]:
                then_verb_left_modif, then_verb, then_verb_right_modif = _split_by_verb(e1_pred_words)

            elif relation in [AtomicRelation.xReact, AtomicRelation.oReact]:
                then_verb = 'feel'
                then_verb_left_modif = None
                then_verb_right_modif = ' '.join(e1_pred_words) or None

            elif relation in [AtomicRelation.xWant, AtomicRelation.oWant,
                              AtomicRelation.xNeed, AtomicRelation.xIntent]:
                if relation in [AtomicRelation.xWant, AtomicRelation.oWant]:
                    then_verb = 'want'
                elif relation in [AtomicRelation.xNeed]:
                    then_verb = 'need'
                elif relation in [AtomicRelation.xIntent]:
                    then_verb = 'intend'
                else:
                    raise Exception()

                then_verb_left_modif = None
                e1_to_pred_words = (['to'] + e1_pred_words if len(e1_pred_words) > 0 and e1_pred_words[0] != 'to'\
                                    else e1_pred_words)
                then_verb_right_modif = ' '.join(e1_to_pred_words) or None

            elif relation in [AtomicRelation.xAttr]:
                then_verb = 'is'
                then_verb_left_modif = None
                then_verb_right_modif = ' '.join(e1_pred_words) or None


            else:
                raise Exception()

        elif relation in _E1_IS_IF_RELATIONS:

            then_subj = e0_subj
            then_verb = e0_verb
            then_verb_left_modif = e0_verb_left_modif
            then_verb_right_modif = e0_verb_right_modif

            if_subj = _PersonX

            if relation in []:
                # if relation == AtomicRelation.xIntent:
                #     if_verb = 'intend'
                # else:
                #     raise Exception()
                if_verb_left_modif = None
                e1_to_pred_words = (['to'] + e1_pred_words if len(e1_pred_words) > 0 and e1_pred_words[0] != 'to'\
                                    else e1_pred_words)
                if_verb_right_modif = ' '.join(e1_to_pred_words) or None

            else:
                raise Exception()

        else:
            raise Exception()

        if then_verb is None:
            continue

        if_statement = AtomicStatement(
            subj=if_subj,
            verb=if_verb,
            verb_left_modif=if_verb_left_modif,
            verb_right_modif=if_verb_right_modif,
        )

        then_statement = AtomicStatement(
            subj=then_subj,
            verb=then_verb,
            verb_left_modif=then_verb_left_modif,
            verb_right_modif=then_verb_right_modif,
        )

        yield AtomicIfThenStatement(
            if_statement=if_statement,
            then_statement=then_statement,
            relation=relation,
        )


def _normalize_person(rep: str) -> str:
    rep = re.sub('[Pp]erson[-]*[Xx]', _PersonX, rep)
    rep = re.sub('[Pp]erson[-]*[Yy]', _PersonY, rep)
    return rep


def _is_verb(word) -> bool:
    return POS.VERB in _WORD_UTILS.get_pos(word)


class AtomicIfThenCommonsenseBank(CommonsenseBankBase):

    def __init__(self,
                 path: str,
                 max_statements: Optional[int] = None):
        self._shared_subj_statements: Iterable[AtomicIfThenStatement] = []
        self._unshared_subj_statements: Iterable[AtomicIfThenStatement] = []

        for statement in load_atomic_if_then_statements(path, max_statements=max_statements):
            if self._extract_PAS(statement.if_statement)[1] is None\
                    or self._extract_PAS(statement.then_statement)[1] is None:
                continue
            if re.match('^x._x.', statement.type):
                # type is something like "xy_xy"
                self._shared_subj_statements.append(statement)
            else:
                self._unshared_subj_statements.append(statement)
        self._shared_subj_statements = RandomCycle(self._shared_subj_statements)
        self._unshared_subj_statements = RandomCycle(self._unshared_subj_statements)

        self._person_names: Iterable[str] = RandomCycle(get_person_names(country='US'))

    def is_acceptable(self, formulas: List[Formula]) -> bool:
        return all(
            is_simple_unary_implication_shared_const(formula)
            or is_simple_unary_implication_unshared_const(formula)
            or is_simple_universal_implication(formula)
            for formula in formulas
        )

    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Phrase], Dict[str, POS], List[bool]]:
        mapping: Dict[str, str] = {}
        pos_mapping: Dict[str, str] = {}
        is_mapped: List[bool] = []

        for formula in formulas:

            """
            {A}{a} -> {B}{a}    : x*_x*
            {A}{a} -> {B}{b}    : x*_**
            (x): {A}x -> {B}x   : x*_x*
            """

            if is_simple_unary_implication_shared_const(formula):
                if_then_statement = next(self._shared_subj_statements)
            elif is_simple_unary_implication_unshared_const(formula):
                if_then_statement = next(self._unshared_subj_statements)
            elif is_simple_universal_implication(formula):
                if_then_statement = next(self._shared_subj_statements)
            else:
                is_mapped.append(False)
                continue

            person_x_sample = next(self._person_names, 1)
            person_y_sample = next(self._person_names, 1)

            def replace_names(rep: Optional[str]) -> Optional[str]:
                if rep is None:
                    return None
                return rep.replace(_PersonX, person_x_sample).replace(_PersonY, person_y_sample)

            if_subj_sample, if_pred_sample, if_pred_right_modif_sample, if_pred_pos = self._extract_PAS(if_then_statement.if_statement)
            if_subj_sample = replace_names(if_subj_sample)
            if_pred_right_modif_sample = replace_names(if_pred_right_modif_sample)

            then_subj_sample, then_pred_sample, then_pred_right_modif_sample, then_pred_pos = self._extract_PAS(if_then_statement.then_statement)
            then_subj_sample = replace_names(then_subj_sample)
            then_pred_right_modif_sample = replace_names(then_pred_right_modif_sample)

            if_pred, then_pred = get_if_then_predicates(formula)

            def maybe_modif(pred: str, right_modif: Optional[str]) -> str:
                # return pair_pred_with_obj_mdf(pred, None, right_modif)
                return PredicatePhrase(predicate=pred, object=None, modifier=right_modif)

            if is_simple_unary_implication_shared_const(formula):  # {A}{a} -> {B}{b}
                if_const, then_const = get_if_then_constants(formula)

                _new_mapping = {
                    if_const.rep: ConstantPhrase(constant=if_subj_sample),
                    if_pred.rep: PredicatePhrase(predicate=if_pred_sample, modifier=if_pred_right_modif_sample),
                    then_pred.rep: PredicatePhrase(predicate=then_pred_sample, modifier=then_pred_right_modif_sample),
                }
                _new_pos_mapping = {
                    if_const.rep: POS.NOUN,
                    if_pred.rep: if_pred_pos,
                    then_pred.rep: then_pred_pos,
                }

            elif is_simple_unary_implication_unshared_const(formula):
                if_const, then_const = get_if_then_constants(formula)

                _new_mapping = {
                    if_const.rep: ConstantPhrase(constant=if_subj_sample),
                    if_pred.rep: PredicatePhrase(predicate=if_pred_sample, modifier=if_pred_right_modif_sample),
                    then_const.rep: ConstantPhrase(constant=then_subj_sample),
                    then_pred.rep: PredicatePhrase(predicate=then_pred_sample, modifier=then_pred_right_modif_sample),
                }
                _new_pos_mapping = {
                    if_const.rep: POS.NOUN,
                    if_pred.rep: if_pred_pos,
                    then_const.rep: POS.NOUN,
                    then_pred.rep: then_pred_pos,
                }

            elif is_simple_universal_implication(formula):
                _new_mapping = {
                    if_pred.rep: PredicatePhrase(predicate=if_pred_sample, modifier=if_pred_right_modif_sample),
                    then_pred.rep: PredicatePhrase(predicate=then_pred_sample, modifier=then_pred_right_modif_sample),
                }
                _new_pos_mapping = {
                    if_pred.rep: if_pred_pos,
                    then_pred.rep: then_pred_pos,
                }

            if all(new_key not in mapping for new_key in _new_mapping):
                # updating the already-mapped logical elements will break the commonsense statements
                mapping.update(_new_mapping)
                pos_mapping.update(_new_pos_mapping)
                is_mapped.append(True)

        return mapping, pos_mapping, is_mapped

    def _extract_PAS(self, statement: AtomicStatement) -> Tuple[Optional[str], Optional[str], Optional[str], POS]:
        subj = statement.subj
        verb = statement.verb
        verb_modif = statement.verb_right_modif

        if verb == 'is':
            if verb_modif is not None and len(verb_modif.split(' ')) == 1:
                # verb_modif is like "excited"
                pred = verb_modif.split(' ')[0]
                pred_modif = None
                pred_pos = POS.ADJ
            else:
                # verb_modif is like "extemely excited with the game"
                # we discard such item because is is a little bit difficult to extract the main predicate phrase
                pred = None
                pred_modif = None
                pred_pos = None
        else:
            pred = verb
            pred_modif = verb_modif
            pred_pos = POS.VERB

        return subj, pred, pred_modif, pred_pos
