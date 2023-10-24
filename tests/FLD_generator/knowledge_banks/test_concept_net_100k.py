from pprint import pprint
import logging

from FLD_generator.knowledge_banks.concept_net_100k import (
    _load_statements,
    ConceptNet100kKnowledgeBank,
)
from FLD_generator.knowledge_banks.statement import DeclareStatement, IfThenStatement
from logger_setup import setup as setup_logger

from shared import sample_mappings

_PATH = 'res/knowledge/commonsense-kg-completion/data/ConceptNet/train.txt'

def test_load_statements():
    for statement in _load_statements(_PATH, max_statements=10000):
        print('')

        if isinstance(statement, DeclareStatement):
            pprint(statement)

        elif isinstance(statement, IfThenStatement):
            pprint(statement.if_statement)
            pprint(statement.then_statement)

        else:
            raise Exception()


def test_bank():
    bank = ConceptNet100kKnowledgeBank(_PATH, max_statements=1000)
    sample_mappings(bank, '{F}{a}')



if __name__ == '__main__':
    setup_logger(level=logging.INFO)

    # test_load_statements()
    test_bank()
