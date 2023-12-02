from typing import Optional, Iterable, List, Dict, Any, Optional, Set, Tuple
from abc import abstractmethod, abstractproperty

from ordered_set import OrderedSet
from FLD_generator.word_banks.japanese import JapaneseWordBank, Morpheme, parse


class WordRandomOrdering:

    def __init__(self):
        pass

    def apply(self, text: str) -> str:
        morphemes = parse(text)
        return text_modified


def build_word_random_ordering() -> WordRandomOrdering:
    return WordRandomOrdering()
