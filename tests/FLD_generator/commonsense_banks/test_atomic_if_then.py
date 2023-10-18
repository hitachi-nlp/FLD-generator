from pprint import pprint
import logging
from typing import Dict, Tuple, List

from FLD_generator.formula import Formula
from FLD_generator.commonsense_banks.atomic_if_then import (
    load_atomic_if_then_statements,
    AtomicIfThenCommonsenseBank,
)
from FLD_generator.translators import TemplatedTranslator
from logger_setup import setup as setup_logger


def test_load_atomic_if_then_statements():
    path = './res/commonsense/commonsense-kg-completion/data/atomic/test.txt'
    for statement in load_atomic_if_then_statements(path, max_statements=1000):
        print('\n')
        pprint(statement.if_statement)
        pprint(statement.then_statement)
        pprint(statement.relation)
        pprint(statement.type)


def test_bank():
    path = './res/commonsense/commonsense-kg-completion/data/atomic/test.txt'
    bank = AtomicIfThenCommonsenseBank(path, max_statements=1000)

    def sample_mapping(formula_rep: str) -> Tuple[Dict[str, str], Dict[str, str], List[bool]]:
        return bank.sample_mapping([Formula(formula_rep)])

    def sample_mappings(formula_rep: str, n_trial=100):
        for i in range(n_trial):
            print('\n\n')
            print(f'================== {formula_rep} =====================')
            mapping, _, _ = sample_mapping(formula_rep)
            for key, val in mapping.items():
                print(f'{key}: {val}')

    sample_mappings('{A}{a} -> {B}{a}')
    sample_mappings('{A}{a} -> {B}{b}')
    sample_mappings('(x): {A}x -> {B}x')



if __name__ == '__main__':
    setup_logger(level=logging.INFO)

    test_load_atomic_if_then_statements()
    test_bank()
