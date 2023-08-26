import random
import re

from .templated import TemplatedTranslator


class JapaneseTranslator(TemplatedTranslator):

    def __init__(self,
                 *args,
                 insert_word_delimiters=False,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_word_delimiters = insert_word_delimiters

    def _postprocess_template(self, template: str) -> str:
        return template

    def _make_pred_with_obj_transl(self, translation: str) -> str:
        # TODO: implemente the logic for randomly choosing 格, such as が,を,に．
        kaku = 'を'
        return re.sub(r'([^ ]*)__O__([^ ]*)', f'\g<2>{kaku}\g<1>', translation)

    def _postprocess_translation(self, translation: str) -> str:
        # translation = re.sub('だ ならば', ' ならば', translation)
        # translation = re.sub('だ し', ' ならば', translation)
        if self.insert_word_delimiters:
            return translation
        else:
            return re.sub(' ', '', translation)
