from formal_logic import generate_tree, Formula, Argument


def test_generation():
    args = [
        # modus ponens
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('Fa')],
            Formula('Ga'),
        ),
        Argument(
            [Formula('(x): Fx -> Gx'), Formula('(x): Gx -> Hx')],
            Formula('(x): Fx -> Hx'),
        ),

    ]
    for i in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(args, depth=5)
        if proof_tree is not None:
            print(proof_tree.format_str)


if __name__ == '__main__':
    from logger_setup import setup as setup_logger
    setup_logger()
    test_generation()
