from typing import Dict, Tuple, List

from FLD_generator.knowledge_banks.base import KnowledgeBankBase
from FLD_generator.formula import Formula


def sample_mapping(bank: KnowledgeBankBase,
                   formula_rep: str,
                   collapse=False) -> Tuple[Dict[str, str], Dict[str, str], List[bool]]:
    return bank.sample_mapping(Formula(formula_rep), collapse=collapse)

def sample_mappings(bank: KnowledgeBankBase,
                    formula_rep: str,
                    n_trial=100):
    for collapse in [False, True]:
        for i in range(n_trial):
            print('\n\n')
            print(f'================== {formula_rep}    collapse={collapse} =====================')
            mapping = sample_mapping(bank, formula_rep, collapse=collapse)
            for key, (word, pos) in mapping.items():
                print(f'{key}: {word}    {pos}')
