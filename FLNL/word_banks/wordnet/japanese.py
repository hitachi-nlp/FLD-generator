from typing import Optional, Iterable, List
import re
import logging

from FLNL.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm
from .base import WordNetWordBank

logger = logging.getLogger(__name__)


class JapaneseWordBank(WordNetWordBank):

    language = 'jpn'

    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        raise NotADirectoryError()

    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        raise NotADirectoryError()

    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        raise NotADirectoryError()

    def get_negnyms(self, word) -> List[str]:
        raise NotADirectoryError()
