from typing import Optional
from .mock_if_then import MockIfThenCommonsenseBank
from .atomic_if_then import AtomicIfThenCommonsenseBank


def build(type_: str,
          atomic_filepath: str,
          max_statements: Optional[int] = None):
    if type_ == 'mock_if_then':
        return MockIfThenCommonsenseBank()
    elif type_ == 'atomic_if_then':
        return AtomicIfThenCommonsenseBank(atomic_filepath,
                                           max_statements=max_statements)
    else:
        raise ValueError()
