from typing import Optional, Iterable
from abc import ABC, abstractmethod


class WordBank(ABC):

    @abstractmethod
    def get_words(self, pos: Optional[str] = None) -> Iterable[str]:
        pass

    @abstractmethod
    def to_present_continuous(self, verb: str) -> Optional[str]:
        pass

    @abstractmethod
    def can_be_intransitive_verb(self, verb: str) -> bool:
        pass
