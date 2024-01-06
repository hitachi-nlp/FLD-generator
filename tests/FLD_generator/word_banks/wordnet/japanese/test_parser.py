from pprint import pprint

from FLD_generator.word_banks.base import UserWord, POS
from FLD_generator.word_banks.japanese import MorphemeParser


def test_parse():

    def _test_parse(text: str, parser: MorphemeParser):
        print('\n\n================================ testing parse ================================')
        print('')
        print(f'Input: {text}')
        print('\nOutput:')
        morphemes = parser.parse(text)
        for morpheme in morphemes:
            print(f'    {morpheme.surface:<20}{morpheme.pos:<20}{morpheme.base:<20}{morpheme.misc.get("vocab_type", ""):<20}')
            
    # parser = MorphemeParser()
    # pprint(parser.parse('静岡県で降った大雨の影響で、始発から通常運転を再開した東海道新幹線は再び運転を見合わせ、各地の駅は新幹線を待つ乗客らでごったがえした。'))
    # _test_parse(
    #     '静岡県で降った大雨の影響で、始発から通常運転を再開した東海道新幹線は再び運転を見合わせ、各地の駅は新幹線を待つ乗客らでごったがえした。',
    #     parser,
    # )

    parser_with_extra_vocab = MorphemeParser(
        extra_vocab=[
            UserWord(lemma='ぷにぷに', pos=POS.NOUN),
            UserWord(lemma='ぴよぴよ', pos=POS.NOUN),
            UserWord(lemma='固体燃料', pos=POS.NOUN),

            UserWord(lemma='歩く', pos=POS.VERB),
            UserWord(lemma='走る', pos=POS.VERB),
            UserWord(lemma='ぷにる', pos=POS.VERB),

            UserWord(lemma='ぺにょい', pos=POS.ADJ),
            UserWord(lemma='ぷにょい', pos=POS.ADJ),
            UserWord(lemma='赤い', pos=POS.ADJ),
        ]
    )

    _test_parse(
        'あのぷにぷにはぴよぴよだし固体燃料だ',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷには歩くし走るしぷにる',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにはぺにょいしぷにょいし赤い',
        parser_with_extra_vocab,
    )


if __name__ == '__main__':
    test_parse()
