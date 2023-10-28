from typing import Optional
from .mock import MockIfThenKnowledgeBank
from .atomic import AtomicKnowledgeBank
from .concept_net_100k import ConceptNet100kKnowledgeBank
from .dbpedia import DBpedia



def build(type_: str,
          filepath: str,
          max_statements: Optional[int] = None,
          no_shuffle=False):
    if type_ == 'mock':
        raise NotImplementedError('Not maintained')
        # return MockIfThenKnowledgeBank()
    elif type_ == 'atomic':
        return AtomicKnowledgeBank(filepath,
                                   max_statements=max_statements,
                                   shuffle=not no_shuffle)
    elif type_ == 'concept_net_100k':
        return ConceptNet100kKnowledgeBank(filepath,
                                           max_statements=max_statements,
                                           shuffle=not no_shuffle)
    elif type_ == 'dbpedia':
        return DBpedia(filepath,
                       max_statements=max_statements,
                       shuffle=not no_shuffle)

    else:
        raise ValueError()
