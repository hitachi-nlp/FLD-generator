# z3 checkers
* "トップダウンで考える"
* contradictionを出す
    - proof_tree_generatorsにおいて，contradiction以外の場合，consistentであることを確かめる．
    - proof_tree_generatorsにおいて，is_consistentチェックを外す．
    * arg以外のすべての部分において，矛盾が生じないように．
        - tree_have_contradiction_argで排除してしまうと，本当に今現在矛盾が生じようとしているそれを，排除できない．
* 新しく加えたチェック部分において、proof_tree.nodes とやっているならば、それはassumpも含んでしまっている?
    - いや，そもそも，「negationの場合はinconsistentでもOK」とするので，問題ない．
    - むしろ問題は，proof_tree.nodesなのか proof_tree.leaf_nodesなのか．
        * proof_tree.leaf_nodesで十分である．なぜならば，internal nodeを導くのは，SAT solverが勝手にやるから．
            * ただ，.leaf_nodesにassumpが含まれてしまってはだめ．また，.nodesにも含まれてはだめ．
* checkersの整理
    - z3じゃない方を消す？
    - is_consistent_formula_set
* speedup
    * distractor側も，generate()が非効率になっていないか？
    * checkingの順番
* timeout戻す
* ここで重要なものをOSSに移す．

## done
* [done] なぜサンプル10件くらいでとまる？
* [done] timeoutが大きすぎる
    - いや，これは正しい挙動である．



# トップダウンで考える
* 何をcheckするか？
    - inconsistency
    - [todo] is_new など．

## inconsistency
* step_consistency_checking=「証明木の構築過程で，1ステップごとに，leaf_nodeが矛盾しているかどうかをチェックし，矛盾していたら却下する」という方針が正しいか？
    * まとめ
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
    * contradiction argumentの両側にある論理式群同士のみ，矛盾が許される．
    * should_consistent_formula_sets みたいなものを用意すれば良い．
    * 反論: 「assumpをleafとしない」というだけで終わる気がしてきている．
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
* [todo] チェック
    - 最終的な証明が無矛盾していないか？ (途中1ステップごとに却下しているので，かならず無矛盾なはず)
    - contradictionが出るか？
    - assumpが出ているか？
        * negation
        * ->intro
