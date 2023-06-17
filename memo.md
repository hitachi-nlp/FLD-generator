# z3 checkers
* contradictionを出す
    - proof_tree_generatorsにおいて，contradiction以外の場合，consistentであることを確かめる．
    - proof_tree_generatorsにおいて，is_consistentチェックを外す．
* 新しく加えたチェック部分において、proof_tree.nodes とやっているならば、それはassumpも含んでしまっている?
* checkersの整理
    - z3じゃない方を消す？
    - is_consistent_formula_set
* speedup
    * distractor側も，generate()が非効率になっていないか？
* timeout戻す

## done
* [done] なぜサンプル10件くらいでとまる？
* [done] timeoutが大きすぎる
    - いや，これは正しい挙動である．

