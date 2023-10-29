from pprint import pprint
import logging

from FLD_generator.knowledge_banks.dbpedia import (
    _load_statements,
    DBpedia,
)
from FLD_generator.knowledge_banks.statement import DeclareStatement, IfThenStatement
from logger_setup import setup as setup_logger

from shared import sample_mappings

_PATH = './res/knowledge_banks/DBpedia500/train1.txt'


def test_load_statements():
    for statement in _load_statements(_PATH, max_statements=10000):
        print('')

        if isinstance(statement, DeclareStatement):
            pprint(statement)
            print(f'type={str(statement.type)}')

        elif isinstance(statement, IfThenStatement):
            pprint(statement.if_statement)
            pprint(statement.then_statement)
            pprint(statement.relation)
            print(f'type={str(statement.type)}')

        else:
            raise Exception()


def test_bank():
    bank = DBpedia(_PATH)
    sample_mappings(bank, '{F}{a}', n_trial=1000)


if __name__ == '__main__':
    setup_logger(level=logging.INFO)

    # test_load_statements()
    test_bank()
