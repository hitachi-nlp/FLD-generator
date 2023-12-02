import random
import re
from typing import Dict, Optional

from FLD_generator.translators.templated import TemplatedTranslator
from FLD_generator.translators.base import PredicatePhrase, ConstantPhrase


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
        rep = const.constant
        if const.left_modifier is not None:
            raise NotImplementedError()
        if const.right_modifier is not None:
            raise NotImplementedError()
        return rep

    def _make_predicate_phrase_str(self, pred: PredicatePhrase) -> str:
        rep = pred.predicate

        if pred.left_modifier is not None:
            raise NotImplementedError()

        if pred.object is not None and pred.right_modifier is not None:
            raise Exception('Can not determine the order of these phrases. We do not expect to pass this code, therefore, might be a bug.')

        if pred.object is not None:
            kaku = self._transl_to_kaku_cache.get(pred, random.choice(['を', 'に']))
            self._transl_to_kaku_cache[pred] = kaku
            rep = pred.object + kaku + rep

        if pred.right_modifier is not None:
            raise NotImplementedError()

        return rep

    def _postprocess_translation(self, translation: str, knowlege_type: Optional[str] = None) -> str:
        # translation = re.sub('だ ならば', ' ならば', translation)
        # translation = re.sub('だ し', ' ならば', translation)
        if self.insert_word_delimiters:
            return translation
        else:
            return re.sub(' ', '', translation)
