from typing import Optional
from .mock_if_then import MockIfThenKnowledgeBank
from .atomic_if_then import AtomicIfThenKnowledgeBank


def build(type_: str,
          atomic_filepath: str,
          max_statements: Optional[int] = None):
    if type_ == 'mock_if_then':
        return MockIfThenKnowledgeBank()
    elif type_ == 'atomic_if_then':
        return AtomicIfThenKnowledgeBank(atomic_filepath,
                                           max_statements=max_statements)
    else:
        raise ValueError()
