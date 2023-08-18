from functools import lru_cache
from lemminflect import getLemma


@lru_cache(maxsize=1000000)
def get_lemma(word: str) -> str:
    # TODO: pos other than VERB
    return getLemma(word, upos='VERB')[0]
