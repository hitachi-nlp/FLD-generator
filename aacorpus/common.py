import re


class Proposition:

    def __init__(self, claim: str):
        self._claim = claim
        self._an_reg = re.compile(' a ([aeiou])')

    def _normalize(self, sent: str) -> str:
        return self._lower(self._adjust_indef(sent.strip(' ')))

    def _adjust_indef(self, sent: str) -> str:
        # a apple => an apple
        return self._an_reg.sub(r' an \1', sent)

    def __repr__(self) -> str:
        return self._lower(self._normalize(self._claim))

    def _lower(self, sent: str) -> str:
        return sent[0].lower() + sent[1:]

