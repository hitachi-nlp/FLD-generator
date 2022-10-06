from FLNL.argument import Argument
from pprint import pprint


def test_argument():
    argument_jsons = [
        {
            "id": "implecation_intro.pred_only",
            "premises": [
                "{A} ⊢ {B}"
            ],
            "conclusion": "{A} -> {B}"
        },
        {
            "id": "or_elim.pred_only",
            "premises": [
                "{A} ⊢ {C}",
                "{B} ⊢ {C}",
                "({A} v {B})"
            ],
            "conclusion": "{C}"
        }
    ]

    for argument_json in argument_jsons:
        print('\n==========================')
        pprint(argument_json)

        argument = Argument.from_json(argument_json)
        print(argument)

        argument_dump_load = Argument.from_json(argument.to_json())
        print(argument_dump_load)


if __name__ == '__main__':
    test_argument()
