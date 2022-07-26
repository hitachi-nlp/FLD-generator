import json
from formal_logic import generate_tree, Formula, Argument, load_argument_config


def test_simple_generation():
    arguments = [
        # modus ponens
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('Fa')],
            Formula('Ga'),
            id='modus ponens',
        ),
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('(x): Gx -> Hx')],
            Formula('(x): Fx -> Hx'),
            id='syllogism',
        ),

    ]
    for _ in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(arguments, depth=5)
        if proof_tree is not None:
            print(proof_tree.format_str)


def test_generation():
    arguments_config_path = './configs/formal_logic/syllogistic_corpus-02.json'
    arguments = load_argument_config(arguments_config_path)

    for _ in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(arguments, depth=5)
        if proof_tree is not None:
            print(proof_tree.format_str)


if __name__ == '__main__':
    from logger_setup import setup as setup_logger
    setup_logger()

    # test_simple_generation()

    test_generation()
