from typing import Optional
from functools import lru_cache
from lemminflect import getLemma


@lru_cache(maxsize=1000000)
def get_lemma(word: str) -> Optional[str]:
    # TODO: pos other than VERB

     #lemmmas = getLemma(word, upos='VERB', lemmatize_oov=True)
     #return lemmmas[0]

    lemmmas = getLemma(word, upos='VERB', lemmatize_oov=False)
    if len(lemmmas) > 0:
        return lemmmas[0]
    else:
        return None
