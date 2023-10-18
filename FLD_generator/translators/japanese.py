import random
import re
from typing import Dict

from .templated import TemplatedTranslator


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

    def _reset_pred_with_obj_mdf_transl(self) -> None:
        self._transl_to_kaku_cache = {}

    def _make_pred_with_obj_mdf_transl(self, translation: str) -> str:
        translation_updated = translation
        pred_O_obj_regexp = f'([^ ]*){self.OBJ_DELIMITER}([^ ]*)'
        for match in re.finditer(pred_O_obj_regexp, translation):
            pred_with_obj_mdf = translation[match.span()[0]:match.span()[1]]

            kaku = self._transl_to_kaku_cache.get(pred_with_obj_mdf, random.choice(['を', 'に']))
            self._transl_to_kaku_cache[pred_with_obj_mdf] = kaku

            pred_with_kaku = re.sub(pred_O_obj_regexp, f'\g<2>{kaku}\g<1>', pred_with_obj_mdf)
            translation_updated = re.sub(pred_O_obj_regexp, pred_with_kaku, translation_updated, 1)

        return translation_updated

    def _postprocess_translation(self, translation: str) -> str:
        # translation = re.sub('だ ならば', ' ならば', translation)
        # translation = re.sub('だ し', ' ならば', translation)
        if self.insert_word_delimiters:
            return translation
        else:
            return re.sub(' ', '', translation)
