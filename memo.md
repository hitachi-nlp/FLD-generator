# z3 checkers
* "トップダウンで考える"
    * 全部リファクタリング．
* checkersの整理
    - checkしている部分をきれいにする．
    - z3じゃない方を消す？
    - is_consistent_formula_set
* speedup
    * distractor側も，generate()が非効率になっていないか？
    * checkingの順番
* timeout戻す
* ここで重要なものをOSSに移す．




# [todo] 最終チェック
- 最終的な証明が無矛盾していないか？ (途中1ステップごとに却下しているので，かならず無矛盾なはず)
- [done] negation_elim, negation_intro
- [done] assumpが出ているか？
    * negation
    * ->intro
* [transferred] "多様なargumentが使えているか？"
- 最終的なチェックに引っかかっていないか？



# 多様なargumentが使えているか？
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


## done
* [done] なぜサンプル10件くらいでとまる？
* [done] timeoutが大きすぎる
    - いや，これは正しい挙動である．



# [done] トップダウンで考える

## [todo] 何をcheckすべきか？
- [done] "inconsistency"
- [done] "smaller proofs"
- [transferred] is_new など．

## smaller proofs
* step_smaller_proof_checking=「証明木の構築過程で，1ステップごとに，smaller_proofが存在するかどうかをチェックし，存在していたら却下する」という方針が正しいか？
    * [conclusion]
        - この方針で良い．必要十分条件になっているので．
    * 考え方
        - 必要条件: 「final_no_smaller_proof -> step_no_smaller_proof」が言えるとする．そうすると，step_no_smaller_proofはfinal_no_smaller_proofの必要条件となる．
        - 十分条件: 「step_no_smaller_proof -> final_no_smaller_proof」が言えるとする．そうすると，step_no_smaller_proof_checkingはfinal_no_smaller_proofの十分条件となる．
    * generate_stemの場合
        * 必要条件は言える．証明木の途中までに複数証明があれば，最後にも複数証明があることは言える．
        * 十分条件は言える．最後のステップの保証による．
    * extend_branchesの場合
        * 必要条件は言える．背理法を使う．
        * 十分条件は言える．最後のステップの保証による．

## inconsistency
* step_consistency_checking=「証明木の構築過程で，1ステップごとに，leaf_nodeが矛盾しているかどうかをチェックし，矛盾していたら却下する」という方針が正しいか？
    * [conclusion]
        * generate_stem/extend_branches/distractor 全ての場合で，最終目標の必要十分条件になっている．よってこの方針は正しい．
    * 考え方
        - 最終的に保証したいのは，final_consistency=「最終的な証明木が無矛盾」ということ．
        - step_consistency=「証明木の構築過程で無矛盾」とfinal_consistency=「最終的な証明木が無矛盾」の関係を考える．
        - 必要条件: 「final_consistency -> step_consistency」が言えるとする．そうすると，step_consistency_checkingはfinal_consistencyの必要条件となる．
        - 十分条件: 「step_consistency -> final_consistency」が言えるとする．そうすると，step_consistency_checkingはfinal_consistencyの十分条件となる．
    * generate_stemの場合
        * 必要条件は言える．なぜならば，最終的な証明木の葉ノードは，中間的な証明木の葉ノードの上位集合であり，「上位集合が無矛盾ならば下位集合も無矛盾」が成り立つから．
        * 十分条件は言えないが，最後のステップで十分性を保証できる．よって，OK．
    * extend_branchesの場合
        * 必要条件は言える．妥当な論証(前提が真なら結論も真)のみを使っているので．
        * 十分条件は言えないが，最後のステップで十分性を保証できる．よって，OK．
            * 十分条件が成り立っていない例:
                ```
                A & B      ^B
                -----
                A
                ```
    * distractorの場合
        * 必要も十分も言える．
* contradictionは？
    * [accepted] assumpをleafと考えない場合
        * 最終的な木には矛盾は生じない．矛盾につながるleaf全て，negation_introによってasump参照され，leafではなくなるため．
        * ただ，木の構築途中では，leafが矛盾する瞬間がある(=negation_elimをする瞬間)．この瞬間だけ，矛盾を許すようにすれば良い．
    * [rejected] assumpをleafと考える場合
        * contradiction argumentの両側にあるleaf群同士のみ，矛盾が許される．
        * should_consistent_formula_sets みたいなものを用意すれば良い．
* assumpは？
    - step_consistency_checkingに入れて良い．
        * assumpといっても，leaf_nodeの特別なバージョンでしかない．
        * 矛盾が許される場合は，上記の「contradictionは？」で尽くされており，新たに条件を加える必要はない．
        * 現状はleaf_nodesに含まれている．
    - assump
        1. 一旦，現状の仕様でいく．
        2. [rejected] 仕様を固めなおす．
            - [rejected] 現状で正しい．
            - 現状の課題
                - .leaf_nodes でassumpもその親も入っている．これは矛盾．
                - .leaf_nodesではassumpが入っているが，traverseでは入っていない．これも矛盾．
            - 決めるべきこと
                - traverse系にassumpを含めるか？
                - .leaf_nodes は誰をいれるか？
