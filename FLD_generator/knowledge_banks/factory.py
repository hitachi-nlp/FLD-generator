from typing import Optional
from .mock import MockIfThenKnowledgeBank
from .atomic import AtomicKnowledgeBank


def build(type_: str,
          atomic_filepath: str,
          max_statements: Optional[int] = None,
          no_shuffle=False):
    if type_ == 'mock_if_then':
        raise NotImplementedError('Not maintained')
        # return MockIfThenKnowledgeBank()
    elif type_ == 'atomic_if_then':
        return AtomicKnowledgeBank(atomic_filepath,
                                         max_statements=max_statements,
                                         shuffle=not no_shuffle)
    else:
        raise ValueError()
