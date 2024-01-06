import random
import re
from typing import Dict, Optional

from FLD_generator.word_banks.base import WordBank, UserWord
from FLD_generator.translators.templated import TemplatedTranslator
from FLD_generator.translators.base import PredicatePhrase, ConstantPhrase
from .postprocessor import build_postprocessor


class JapaneseTranslator(TemplatedTranslator):

    KAKU_LIST = ['を', 'に']

    def __init__(self,
                 config_json: Dict[str, Dict],
                 word_bank: WordBank,
                 *args,
                 insert_word_delimiters=False,
                 extra_vocab: Optional[Dict[str, UserWord]] = None,
                 **kwargs):
        super().__init__(config_json, word_bank, *args, **kwargs)
        self.insert_word_delimiters = insert_word_delimiters
        self._transl_to_kaku_cache: Dict[str, str] = {}
        self._postprocessor = build_postprocessor(word_bank, extra_vocab=extra_vocab)

    def _postprocess_template(self, template: str) -> str:
        return template

    def _reset_assets(self) -> None:
        self._transl_to_kaku_cache = {}
        self._postprocessor.reset_assets()

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
            kaku = self._transl_to_kaku_cache.get(pred, random.choice(self.KAKU_LIST))
            self._transl_to_kaku_cache[pred] = kaku
            rep = pred.object + kaku + rep

        if pred.right_modifier is not None:
            raise NotImplementedError()

        return rep

    def _postprocess_translation(self, translation: str) -> str:
        if self.insert_word_delimiters:
            raise NotImplementedError()

        translation = re.sub(' ', '', translation)
        translation = self._postprocessor.apply(translation)
        return translation
