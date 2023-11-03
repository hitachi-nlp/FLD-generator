from typing import List, Dict, Optional, Tuple, Union, Iterable
import random
from abc import abstractmethod, ABC
import logging
from copy import deepcopy
from collections import defaultdict, deque

from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.formula import Formula
from FLD_generator.word_banks import POS
from FLD_generator.translators.base import Phrase, PredicatePhrase, ConstantPhrase
from FLD_generator.utils import RandomCycle, weighted_sampling
from .formula import (
    FormulaType,
    get_type_fml,
    get_declare_constants_fml,
    get_declare_predicates_fml,
    get_if_then_constants_fml,
    get_if_then_predicates_fml,
)
from .statement import (
    get_phrases_stmt,
    Statement,
    DeclareStatement,
    IfThenStatement,
    StatementType,
    SomeoneX,
    SomeoneY,
    SomethingX,
    SomethingY,
)
from .utils import type_formula_to_statement, type_statement_to_formula

import line_profiling

logger = logging.getLogger(__name__)


class KnowledgeMappingFailure(FormalLogicExceptionBase):
    pass


class KnowledgeMappingImpossible(FormalLogicExceptionBase):
    pass


class DequeWithLimit:

    def __init__(self, limit=1000000):
        self._real = deque()
        self._limit = limit

    def append(self, *args, **kwargs):
        if len(self._real) > self._limit:
            self._real = deque()
        return self._real.append(*args, **kwargs)

    def popleft(self, *args, **kwargs):
        return self._real.popleft(*args, **kwargs)

    def __len__(self):
        return len(self._real)


class KnowledgeBankBase(ABC):

    def __init__(self):
        self._statement_cycle = RandomCycle(
            self._load_statements,
            shuffle=False,  # shuffle should be managed by "self._load_statements()"
        )
        self._statement_cache: Dict[str, Dict[str, DequeWithLimit]] = defaultdict(
            lambda : defaultdict(lambda : DequeWithLimit())
        )

    @abstractmethod
    def _load_statements(self) -> Iterable[Statement]:
        pass

    def _next_statement(self,
                        type_: StatementType,
                        relation: Optional[str] = None) -> Statement:
        if relation is None:
            nonzero_caches = [cache for cache in self._statement_cache[type_].values()
                              if len(cache) > 0]
        else:
            nonzero_caches = ([self._statement_cache[type_][relation]]
                               if len(self._statement_cache[type_][relation]) > 0
                               else [])
        if len(nonzero_caches) > 0:
            cache = nonzero_caches[weighted_sampling([len(_cache) for _cache in nonzero_caches])]
            # logger.critical('load from cache')
            return cache.popleft()

        while True:
            statement = next(self._statement_cycle)
            if statement.type == type_\
                    and (relation is None or statement.relation == relation):
                return statement
            else:
                cache = self._statement_cache[statement.type][statement.relation]
                cache.append(statement)

    def is_formula_accepatable(self, formula: Formula) -> bool:
        return get_type_fml(formula, allow_others=True) in self._formula_types

    @property
    def _formula_types(self) -> List[FormulaType]:
        return list({
            type_statement_to_formula(stmt_type)
            for stmt_type in self._statement_types
        })

    @abstractmethod
    def _statement_types(self) -> List[StatementType]:
        pass

    @profile
    def sample_mapping(self,
                       formula: Formula,
                       collapse=False) -> Dict[str, Tuple[Phrase, Optional[POS]]]:
        _mapping, _statement = self._sample_positive_mapping(
            formula,
            refer_statememt=None,
        )
        if _mapping is None:
            return None

        if collapse:
            _other_mapping, _other_statement = self._sample_positive_mapping(
                formula,
                refer_statememt=_statement,
            )
            collapse_key = random.choice(list(_mapping.keys()))
            _mapping[collapse_key] = _other_mapping[collapse_key]

        return _mapping

    @profile
    def _sample_positive_mapping(self,
                                 formula: Formula,
                                 refer_statememt: Optional[Statement] = None)\
            -> Tuple[Dict[str, Tuple[str, POS]], Statement]:
        fml_type = get_type_fml(formula)
        stmt_type = type_formula_to_statement(fml_type)
        if stmt_type not in self._statement_types:
            return None, None

        if refer_statememt is not None:
            if refer_statememt.type != stmt_type:
                raise ValueError(f'refer_statememt type {refer_statememt.type} != stmt_type {stmt_type}')
            assert refer_statememt.type == stmt_type
            statement = self._next_statement(refer_statememt.type,
                                             relation=refer_statememt.relation)
        else:
            statement = self._next_statement(stmt_type)

        if isinstance(statement, DeclareStatement):
            (const_phrase, const_pos), (pred_phrase, pred_pos) = get_phrases_stmt(
                statement,
            )

            const_formula = get_declare_constants_fml(formula)
            pred_formula = get_declare_predicates_fml(formula)

            if fml_type in [FormulaType.F, FormulaType.nF]:
                raise NotImplementedError()

            elif fml_type in [FormulaType.Fa, FormulaType.nFa]:
                _new_mapping = {
                    const_formula.rep: (const_phrase, const_pos),
                    pred_formula.rep: (pred_phrase, pred_pos),
                }

            elif fml_type in [FormulaType.Fx, FormulaType.nFx]:
                _new_mapping = {
                    pred_formula.rep: (pred_phrase, pred_pos),
                }

            else:
                raise NotImplementedError()

        elif isinstance(statement, IfThenStatement):
            (if_const_phrase, if_const_pos), (if_pred_phrase, if_pred_pos) = get_phrases_stmt(
                statement.if_statement,
            )
            (then_const_phrase, then_const_pos), (then_pred_phrase, then_pred_pos) = get_phrases_stmt(
                statement.then_statement,
            )

            if_pred_formula, then_pred_formula = get_if_then_predicates_fml(formula)
            if_const_formula, then_const_formula = get_if_then_constants_fml(formula)

            if fml_type in [FormulaType.F_G,
                            FormulaType.nF_G,
                            FormulaType.F_nG,
                            FormulaType.nF_nG]:
                _new_mapping = {
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            elif fml_type in [FormulaType.Fa_Ga,
                              FormulaType.nFa_Ga,
                              FormulaType.Fa_nGa,
                              FormulaType.nFa_nGa]:
                _new_mapping = {
                    if_const_formula.rep: (if_const_phrase, if_const_pos),
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            elif fml_type in [FormulaType.Fa_Gb,
                              FormulaType.nFa_Gb,
                              FormulaType.Fa_nGb,
                              FormulaType.nFa_nGb]:
                _new_mapping = {
                    if_const_formula.rep: (if_const_phrase, if_const_pos),
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_const_formula.rep: (then_const_phrase, then_const_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

            elif fml_type in [FormulaType.Fx_Gx,
                              FormulaType.nFx_Gx,
                              FormulaType.Fx_nGx,
                              FormulaType.nFx_nGx]:

                def maybe_replace(rep: Optional[str], src: str, dst: str) -> Optional[str]:
                    if rep is None:
                        return None
                    return rep.replace(src, dst)

                def maybe_replace_pronoun(rep: Optional[str]) -> Optional[str]:
                    rep = maybe_replace(rep, SomeoneX, 'the one')
                    rep = maybe_replace(rep, SomeoneY, 'the other')
                    rep = maybe_replace(rep, SomethingX, 'the thing')
                    rep = maybe_replace(rep, SomethingY, 'the other thing')
                    return rep

                def rename_someone_pronoun(phrase: PredicatePhrase):
                    return PredicatePhrase(
                        predicate = phrase.predicate,
                        left_modifier = maybe_replace_pronoun(phrase.left_modifier),
                        right_modifier = maybe_replace_pronoun(phrase.right_modifier),
                        object = maybe_replace_pronoun(phrase.object),
                    )

                if_pred_phrase = rename_someone_pronoun(if_pred_phrase)
                then_pred_phrase = rename_someone_pronoun(then_pred_phrase)

                _new_mapping = {
                    if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                    then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                }

        else:
            raise ValueError()

        return _new_mapping, statement

    @abstractmethod
    def postprocess_translation(self, translation: str) -> str:
        pass
