# z3 checkers
* なぜloopにおちいる
    - leafの時点で別の証明がある．
        - なぜ？
        - distractor側は，"leafの時点では無いが"とする．
* tautology checker で遅くなったか？
    - 無くても良さそう？
* proof_treeの途中で切るのは，条件が厳しすぎて，多様な論証を使えなさそう．
    ```
    >>> print(proof_tree.format_str)
    0    1    2    3    4    5    6    7    8    9
    |    |    |    |    |    |    |    |    |    |
    |    |    |  None
    |    |    |ProofNode(Formula("{A}{a}", transl=None))
    |    |    |    |    |    |    |    |    |    |
    0    1    2    3    4    5    6    7    8    9
    |    |    |    |    |    |    |    |    |    |                                                                                                                                        Breakpoints:
    |    |  Argument(id="or_intro_0.pred_arg.shared_arg", assumptions={}, premises=[Formula("{A}{a}", transl=None)], conclusion=Formula("({A}{a} v {B}{a})", transl=None),                    runscript.py:255 (0 hits)
    intermediate_constants=[])                                                                                                                                                                show_results.py:73 (0 hits)
    |    |ProofNode(Formula("({A}{a} v {B}{a})", transl=None))                                                                                                                                evaluate_episodes.py:261 (0 hits)
    |    |    |    |    |    |    |    |    |    |                                                                                                                                            search.py:152 (0 hits)
    0    1    2    3    4    5    6    7    8    9                                                                                                                                            model_setup.py:58 (0 hits)
    |    |    |    |    |    |    |    |    |    |                                                                                                                                            runner.py:183 (0 hits)
    |    |  None
    |    |ProofNode(Formula("{A}{a} -> {CA}{cu}", transl=None))
    |    |    |    |    |    |    |    |    |    |
    0    1    2    3    4    5    6    7    8    9
    |    |    |    |    |    |    |    |    |    |
    |    |  None
    |    |ProofNode(Formula("{B}{a} -> {CA}{cu}", transl=None))
    |    |    |    |    |    |    |    |    |    |
    0    1    2    3    4    5    6    7    8    9
    |    |    |    |    |    |    |    |    |    |
    |  Argument(id="or_elim.pred_arg.shared_arg", assumptions={}, premises=[Formula("({A}{a} v {B}{a})", transl=None), Formula("{A}{a} -> {CA}{cu}", transl=None), Formula("{B}{a} ->
    {CA}{cu}", transl=None)], conclusion=Formula("{CA}{cu}", transl=None), intermediate_constants=[])
    |ProofNode(Formula("{CA}{cu}", transl=None))
    ```
* timeoutが大きすぎる
    - いや，これは正しい挙動である．

* なぜ10件くらい？
* checkersの整理
