from typing import List, Dict, Optional, Tuple, Union, Iterable
from abc import abstractmethod, ABC
import logging

from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.formula import Formula
from FLD_generator.word_banks import POS
from FLD_generator.translators.base import Phrase, PredicatePhrase, ConstantPhrase
from FLD_generator.utils import RandomCycle
from .formula import (
    FormulaType,
    get_type_fml,
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
)
from .utils import type_formula_to_statement, type_statement_to_formula

logger = logging.getLogger(__name__)


class KnowledgeMappingFailure(FormalLogicExceptionBase):
    pass


class KnowledgeMappingImpossible(FormalLogicExceptionBase):
    pass


class KnowledgeBankBase(ABC):

    def __init__(self):
        self._statements: Dict[str, Iterable[Statement]] = {
            type_: RandomCycle(
                self._load_statements(type_),
                shuffle=False,  # shuffle should be managed by "self._load_statements()"
            )
            for type_ in self._statement_types
        }

    @abstractmethod
    def _load_statements(self, type_: StatementType) -> Iterable[Statement]:
        pass

    def is_acceptable(self, formulas: List[Formula]) -> bool:
        return all(
            get_type_fml(formula) in self._formula_types
            for formula in formulas
        )

    @property
    def _formula_types(self) -> List[FormulaType]:
        return list({
            type_statement_to_formula(stmt_type)
            for stmt_type in self._statement_types
        })
            
    @abstractmethod
    def _statement_types(self) -> List[StatementType]:
        pass

    def sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Tuple[Phrase, Optional[POS]]], List[bool]]:
        if not self.is_acceptable(formulas):
            raise KnowledgeMappingImpossible()
        return self._sample_mapping(formulas)

    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Tuple[Phrase, Optional[POS]]], List[bool]]:
        mapping: Dict[str, str] = {}
        is_mapped: List[bool] = []

        for formula in formulas:
            fml_type = get_type_fml(formula)
            stmt_type = type_formula_to_statement(fml_type)
            if stmt_type not in self._statement_types:
                is_mapped.append(False)
                continue

            statement = next(self._statements[stmt_type])

            if isinstance(statement, DeclareStatement):
                (const_phrase, const_pos), (pred_phrase, pred_pos) = get_phrases_stmt(
                    statement,
                )

                if fml_type == FormulaType.F:
                    raise NotImplementedError()

                elif fml_type == FormulaType.Fa:
                    const_formula = formula.constants[0]
                    pred_formula = formula.predicates[0]

                    _new_mapping = {
                        const_formula.rep: (const_phrase, const_pos),
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

                if fml_type == FormulaType.F_G:
                    _new_mapping = {
                        if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                        then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                    }

                elif fml_type == FormulaType.Fa_Ga:
                    _new_mapping = {
                        if_const_formula.rep: (if_const_phrase, if_const_pos),
                        if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                        then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                    }

                elif fml_type == FormulaType.Fa_Gb:
                    _new_mapping = {
                        if_const_formula.rep: (if_const_phrase, if_const_pos),
                        if_pred_formula.rep: (if_pred_phrase, if_pred_pos),
                        then_const_formula.rep: (then_const_phrase, then_const_pos),
                        then_pred_formula.rep: (then_pred_phrase, then_pred_pos),
                    }

                elif fml_type == FormulaType.Fx_Gx:

                    def maybe_replace(rep: Optional[str], src: str, dst: str) -> Optional[str]:
                        if rep is None:
                            return None
                        return rep.replace(src, dst)

                    def maybe_replace_pronoun(rep: Optional[str]) -> Optional[str]:
                        return maybe_replace(maybe_replace(rep, SomeoneX, 'the one'), SomeoneY, 'the other')

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

            if all(new_key not in mapping for new_key in _new_mapping):
                # updating the already-mapped logical elements will break the knowledge statements
                mapping.update(_new_mapping)
                is_mapped.append(True)

        return mapping, is_mapped
