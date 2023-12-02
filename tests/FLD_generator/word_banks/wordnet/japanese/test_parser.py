from pprint import pprint
from FLD_generator.word_banks.japanese import parse


def test_parse():
    pprint(parse('静岡県で降った大雨の影響で、始発から通常運転を再開した東海道新幹線は再び運転を見合わせ、各地の駅は新幹線を待つ乗客らでごったがえした。'))


if __name__ == '__main__':
    test_parse()
