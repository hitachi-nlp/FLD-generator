from pprint import pprint
import logging

from FLD_generator.knowledge_banks.atomic import (
    _load_statements,
    AtomicKnowledgeBank,
)
from logger_setup import setup as setup_logger

from shared import sample_mappings

_PATH = './res/knowledge/commonsense-kg-completion/data/atomic/test.txt'


def test_load_statements():
    for statement in _load_statements(_PATH, max_statements=10000):
        print('')
        pprint(statement.if_statement)
        pprint(statement.then_statement)


def test_bank():
    bank = AtomicKnowledgeBank(_PATH, max_statements=1000)

    # sample_mappings(bank, '{A}{a} -> {B}{a}')
    # sample_mappings(bank, '{A}{a} -> {B}{b}')
    sample_mappings(bank, '(x): {A}x -> {B}x')



if __name__ == '__main__':
    setup_logger(level=logging.INFO)

    # test_load_statements()
    test_bank()
