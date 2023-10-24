from typing import List, Dict, Tuple
import re

from FLD_generator.formula import Formula
from FLD_generator.word_banks import POS
from FLD_generator.translators.base import (
    Phrase,
    PredicatePhrase,
    ConstantPhrase,
)
from .base import KnowledgeBankBase
from .formula import (
    get_if_then_constants_fml,
    get_if_then_predicates_fml,
)



class MockIfThenKnowledgeBank(KnowledgeBankBase):

    def __init__(self):
        raise NotImplementedError('Not mainteined.')

    def is_acceptable(self, formulas: List[Formula]) -> bool:
        return all(_is_Fa_Gb_fml(formula)
                   for formula in formulas)

    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Phrase], Dict[str, POS], List[bool]]:
        mapping: Dict[str, str] = {}
        pos_mapping: Dict[str, str] = {}
        is_mapped: List[bool] =[]

        for formula in formulas:
            if not _is_Fa_Gb_fml(formula):
                is_mapped.append(False)
                continue

            if_const, then_const = get_if_then_constants_fml(formula)
            if_pred, then_pred = get_if_then_predicates_fml(formula)

            _new_mapping = {
                if_const.rep: ConstantPhrase(constant='John'),
                if_pred.rep: PredicatePhrase(predicate='human'),

                then_const.rep: ConstantPhrase(constant='John'),
                then_pred.rep: PredicatePhrase(predicate='die'),
            }
            _new_pos_mapping = {
                if_const.rep: POS.NOUN,
                if_pred.rep: POS.ADJ,

                then_const.rep: POS.NOUN,
                then_pred.rep: POS.VERB,
            }

            if all(new_key not in mapping for new_key in _new_mapping):
                # updating the already-mapped logical elements will break the knowledge statements
                mapping.update(_new_mapping)
                pos_mapping.update(_new_pos_mapping)
                is_mapped.append(True)
            else:
                is_mapped.append(False)

        return mapping, pos_mapping, is_mapped
