from typing import List, Dict, Tuple, Optional, Iterable
import re
from enum import Enum
import logging
import random

from FLD_generator.formula import Formula
from FLD_generator.word_banks.word_utils import POS
from FLD_generator.person_names import get_person_names
from FLD_generator.utils import RandomCycle
from FLD_generator.translators.base import (
    Phrase,
    PredicatePhrase,
    ConstantPhrase,
)
from .base import KnowledgeBankBase, Statement, IfThenStatement
from .utils import (
    is_simple_unary_implication_shared_const,
    is_simple_unary_implication_unshared_const,
    is_simple_universal_implication,
    get_if_then_constants,
    get_if_then_predicates,
    parse_verb,
    parse_subj,
)


logger = logging.getLogger(__name__)

_PersonX = 'PersonX'
_PersonY = 'PersonY'


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


def load_atomic_if_then_statements(path: str,
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
        e0_str = _normalize_person(e0_str.lower())
        e1_str = _normalize_person(e1_str.lower())
        if e1_str == 'none':
            continue
        if line.find('___') >= 0:
            continue

        relation = AtomicRelation(rel_str)

        e0_subj_str, e0_pred_str = e0_str.split(' ', 1)

        e0_subj, e0_subj_left_modif, e0_subj_right_modif = parse_subj(e0_subj_str)
        e0_verb, e0_verb_left_modif, e0_verb_right_modif = parse_verb(e0_pred_str)
        if e0_subj != _PersonX:
            raise NotImplementedError()
        if e0_verb is None:
            continue

        e1_words = e1_str.split(' ')

        e1_subj_str = e1_words[0] if e1_words[0] in [_PersonX, _PersonY] else None
        if e1_subj_str is None:
            if relation in [AtomicRelation.xEffect, AtomicRelation.xReact, AtomicRelation.xWant,
                            AtomicRelation.xAttr, AtomicRelation.xNeed, AtomicRelation.xIntent]:
                e1_subj_str = _PersonX
            elif relation in [AtomicRelation.oEffect, AtomicRelation.oReact, AtomicRelation.oWant]:
                if if_verb_right_modif is not None and if_verb_right_modif.find(_PersonY) >= 0:
                    e1_subj_str = _PersonY
                else:
                    e1_subj_str = 'others'
            else:
                raise Exception('Not expected')

        e1_pred_str = ' '.join(e1_words[1:]) if e1_words[0] in [_PersonX, _PersonY] else ' '.join(e1_words)
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
            e1_pred_str = (f'{e1_verb} to {e1_pred_str}' if not e1_pred_str.startswith('to')\
                           else f'{e1_verb} {e1_pred_str}')
        elif relation in [AtomicRelation.xReact, AtomicRelation.oReact]:
            e1_pred_str = f'feel {e1_pred_str}'
        elif relation in [AtomicRelation.xAttr]:
            e1_pred_str = f'is {e1_pred_str}'

        e1_subj, e1_subj_left_modif, e1_subj_right_modif = parse_subj(e1_subj_str)
        e1_verb, e1_verb_left_modif, e1_verb_right_modif = parse_verb(e1_pred_str)

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

        if then_verb is None:
            continue

        if_statement = Statement(
            subj=if_subj,
            subj_right_modif=if_subj_right_modif,
            subj_left_modif=if_subj_left_modif,
            verb=if_verb,
            verb_left_modif=if_verb_left_modif,
            verb_right_modif=if_verb_right_modif,
        )

        then_statement = Statement(
            subj=then_subj,
            subj_right_modif=then_subj_right_modif,
            subj_left_modif=then_subj_left_modif,
            verb=then_verb,
            verb_left_modif=then_verb_left_modif,
            verb_right_modif=then_verb_right_modif,
        )

        yield IfThenStatement(
            if_statement=if_statement,
            then_statement=then_statement,
            relation=relation,
        )


def _normalize_person(rep: str) -> str:
    rep = re.sub('[Pp]erson[-]*[Xx]', _PersonX, rep)
    rep = re.sub('[Pp]erson[-]*[Yy]', _PersonY, rep)
    return rep


class AtomicIfThenKnowledgeBank(KnowledgeBankBase):

    def __init__(self,
                 path: str,
                 shuffle=False,  # note that shuffl=True loads huge dataset once at first, which is slow.
                 max_statements: Optional[int] = None):

        self._path = path
        self._shuffle = shuffle
        self._max_statements = max_statements

        self._shared_subj_statements = RandomCycle(self._load_shared_subj_statements, shuffle=False)
        self._unshared_subj_statements = RandomCycle(self._load_unshared_subj_statements, shuffle=False)

        self._person_names: Iterable[str] = RandomCycle(get_person_names(country='US'))

    def _load_shared_subj_statements(self) -> Iterable[IfThenStatement]:
        for statement in load_atomic_if_then_statements(self._path,
                                                        max_statements=self._max_statements,
                                                        shuffle=self._shuffle):
            if self._is_meaningful(statement):
                continue
            if re.match('^x._x.', self._get_if_then_statement_type(statement)):
                # type is something like "xy_xy"
                yield statement

    def _load_unshared_subj_statements(self) -> Iterable[IfThenStatement]:
        for statement in load_atomic_if_then_statements(self._path,
                                                        max_statements=self._max_statements,
                                                        shuffle=self._shuffle):
            if self._is_meaningful(statement):
                continue
            if not re.match('^x._x.', self._get_if_then_statement_type(statement)):
                yield statement

    def _is_meaningful(self, if_then_statement: IfThenStatement) -> bool:
        return self._extract_PAS(if_then_statement.if_statement)[1][0] is not None\
            and self._extract_PAS(if_then_statement.then_statement)[1][0] is not None

    def _get_if_then_statement_type(self, statement: IfThenStatement) -> str:

        def have(rep: Optional[str], key: str) -> str:
            if rep is None:
                return False
            return rep.find(key) >= 0

        char0 = 'o'
        if have(statement.if_statement.subj, _PersonX):
            char0 = 'x'
        elif have(statement.if_statement.subj, _PersonY):
            char0 = 'y'

        char1 = 'o'
        if have(statement.if_statement.verb_right_modif, _PersonX):
            char1 = 'x'
        elif have(statement.if_statement.verb_right_modif, _PersonY):
            char1 = 'y'

        char2 = 'o'
        if have(statement.then_statement.subj, _PersonX):
            char2 = 'x'
        elif have(statement.then_statement.subj, _PersonY):
            char2 = 'y'

        char3 = 'o'
        if have(statement.then_statement.verb_right_modif, _PersonX):
            char3 = 'x'
        elif have(statement.then_statement.verb_right_modif, _PersonY):
            char3 = 'y'

        return f'{char0}{char1}_{char2}{char3}'

    def is_acceptable(self, formulas: List[Formula]) -> bool:
        return all(
            is_simple_unary_implication_shared_const(formula)
            or is_simple_unary_implication_unshared_const(formula)
            or is_simple_universal_implication(formula)
            for formula in formulas
        )

    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Tuple[Phrase, Optional[POS]]], List[bool]]:
        mapping: Dict[str, str] = {}
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

            person_x = next(self._person_names, 1)
            person_y = next(self._person_names, 1)
            
            (if_const_phrase, if_const_pos), (if_pred_phrase, if_pred_pos) = self._sample_phrases(
                if_then_statement.if_statement,
                person_x,
                person_y,
            )

            (then_const_phrase, then_const_pos), (then_pred_phrase, then_pred_pos) = self._sample_phrases(
                if_then_statement.then_statement,
                person_x,
                person_y,
            )

            if_pred_formula, then_pred_formula = get_if_then_predicates(formula)
            if_const_formula, then_const_formula = get_if_then_constants(formula)

            if is_simple_unary_implication_shared_const(formula):  # {A}{a} -> {B}{b}
                _new_mapping = {
                    if_const_formula.rep: (if_const_phrase, if_const_pos),
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            elif is_simple_unary_implication_unshared_const(formula):
                _new_mapping = {
                    if_const_formula.rep: (if_const_phrase, if_const_pos),
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_const_formula.rep: (then_const_phrase, then_const_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            elif is_simple_universal_implication(formula):
                _new_mapping = {
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            if all(new_key not in mapping for new_key in _new_mapping):
                # updating the already-mapped logical elements will break the knowledge statements
                mapping.update(_new_mapping)
                is_mapped.append(True)

        return mapping, is_mapped

    def _sample_phrases(self,
                        statement: Statement,
                        person_x: str,
                        person_y: str) -> Tuple[Tuple[ConstantPhrase, POS],
                                                Tuple[PredicatePhrase, POS]]:
        def replace_names(rep: Optional[str]) -> Optional[str]:
            if rep is None:
                return None
            return rep.replace(_PersonX, person_x).replace(_PersonY, person_y)

        (
            (subj, subj_left_modif, subj_right_modif, subj_pos),
            (pred, pred_left_modif, pred_right_modif, pred_pos),
        ) = self._extract_PAS(statement)

        subj = replace_names(subj)
        subj_left_modif = replace_names(subj_left_modif)
        subj_right_modif = replace_names(subj_right_modif)

        pred = replace_names(pred)
        pred_left_modif = replace_names(pred_left_modif)
        pred_right_modif = replace_names(pred_right_modif)

        const_phrase = ConstantPhrase(constant=subj,
                                      left_modifier=subj_left_modif,
                                      right_modifier=subj_right_modif)
        pred_phrase = PredicatePhrase(predicate=pred,
                                      right_modifier=pred_right_modif,
                                      left_modifier=pred_left_modif)
        return (const_phrase, subj_pos), (pred_phrase, pred_pos)

    def _extract_PAS(self, statement: Statement) -> Tuple[Tuple[Optional[str], Optional[str], Optional[str], POS]]:
        subj = statement.subj
        subj_left_modif = statement.subj_left_modif
        subj_right_modif = statement.subj_right_modif
        subj_pos = POS.NOUN

        verb = statement.verb
        pred_left_modif = statement.verb_left_modif
        verb_right_modif = statement.verb_right_modif

        if verb == 'is':
            if verb_right_modif is not None and len(verb_right_modif.split(' ')) == 1:
                # verb_right_modif is like "excited"
                pred = verb_right_modif.split(' ')[0]
                pred_right_modif = None
                pred_pos = POS.ADJ
            else:
                # verb_right_modif is like "extemely excited with the game"
                # we discard such item because is is a little bit difficult to extract the main predicate phrase
                pred = None
                pred_right_modif = None
                pred_pos = None
        else:
            pred = verb
            pred_right_modif = verb_right_modif
            pred_pos = POS.VERB

        return (
            (subj, subj_left_modif, subj_right_modif, subj_pos),
            (pred, pred_left_modif, pred_right_modif, pred_pos),
        )
