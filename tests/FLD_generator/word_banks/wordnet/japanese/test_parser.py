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
            # print(f'    {morpheme.surface:<20}{morpheme.pos:<20}{morpheme.base:<20}{morpheme.misc.get("vocab_type", ""):<20}')
            print('   ' + str(morpheme))
            
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



    _test_parse(
        'あのぷにぷにが歩くしそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが赤いしそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが電撃だしそれが走る',
        parser_with_extra_vocab,
    )

    _test_parse(
        'あのぷにぷにが歩いてそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが赤くてそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが電撃でそれが走る',
        parser_with_extra_vocab,
    )

    _test_parse(
        'あのぷにぷにが歩かないしそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが赤くないしそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが電撃でないしそれが走る',
        parser_with_extra_vocab,
    )

    _test_parse(
        'あのぷにぷにが歩かなくてそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが赤くなくてそれが走る',
        parser_with_extra_vocab,
    )
    _test_parse(
        'あのぷにぷにが電撃でなくてそれが走る',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤ないし青が好き',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤ないし青が好き',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いか青い',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いかまたは青い',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いかもしくは青い',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いかあるいは青い',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いが青くない',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いがしかし青くない',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いけど青くない',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤いけれど青くない',
        parser_with_extra_vocab,
    )

    _test_parse(
        '彼が赤い一方で青くない',
        parser_with_extra_vocab,
    )

    _test_parse(
        'このみわみのLv.15はむず痒くないがそれは取り辛い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷにはモンスターで赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷにはモンスターであり赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷにはモンスターであって赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷには優しくて赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷにはスキーして、赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷには優しいか赤い',
        parser_with_extra_vocab,
    )

    _test_parse(
        'ぷにぷにはスキーするか、赤い',
        parser_with_extra_vocab,
    )


if __name__ == '__main__':
    test_parse()
