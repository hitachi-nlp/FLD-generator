import random
import re
from typing import Dict

from .templated import TemplatedTranslator
from .base import PredicatePhrase, ConstantPhrase


class JapaneseTranslator(TemplatedTranslator):

    def __init__(self,
                 *args,
                 insert_word_delimiters=False,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_word_delimiters = insert_word_delimiters
        self._transl_to_kaku_cache: Dict[str, str] = {}

    def _postprocess_template(self, template: str) -> str:
        return template

    def _reset_predicate_phrase_assets(self) -> None:
        self._transl_to_kaku_cache = {}

    def _make_constant_phrase_str(self, const: ConstantPhrase) -> str:
        return const.constant

    def _make_predicate_phrase_str(self, pred: PredicatePhrase) -> str:
        rep = pred.predicate

        if pred.object is not None:
            kaku = self._transl_to_kaku_cache.get(pred, random.choice(['を', 'に']))
            self._transl_to_kaku_cache[pred] = kaku
            rep = pred.object + kaku + rep

        if pred.modifier is not None:
            raise NotImplementedError()

        return rep

    def _postprocess_translation(self, translation: str, is_knowledge_injected=False) -> str:
        # translation = re.sub('だ ならば', ' ならば', translation)
        # translation = re.sub('だ し', ' ならば', translation)
        if self.insert_word_delimiters:
            return translation
        else:
            return re.sub(' ', '', translation)
