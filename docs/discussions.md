# todo
* "要求機能"



# 要求機能

## multistep化
* todo

* 目標
    - modus ponensを2つつなげたルールを作る．
        ```
        (x) Fx -> Gx  Fa
        ----------------
               Ga    (x) Gx -> Hx
               ------------------
                       Ha
        ```
* 生成手法
    - treeを作るべき．そちらの方が分かりやすそう．
    - treeが偏らないためには，以下を満遍なくやる必要がある:
        - 導いた結論を使ってさらに導出
        - 前提を導出
        - 前提(3つ以上ある場合)のうち，3つ目を導出
* データ作成
    - ランダムにルールをサンプリングして，どのように証明データを作るか．
    - 例えば，generalized contraposition が選ばれた場合:
        - P=`(x) Gx -> ^Fx` がまず証明される．
        - 次にありうるステップとして，
            1. PのpremiseであるGa をデータセットに加え，modus ponens によって，^Faを導出する．
                ```
                Gx -> ^Fx    Ga
                ----------------------
                ^Fa
                ```
                **いや，これは2と変わらない．** 別のルール = modus ponens であるだけだ．
            2. Pを"premiseのうちの１つとして"，別のルールを用いて，別の命題を求める．
                ```
                Gx -> ^Fx    ^Fx -> Hx
                ----------------------
                Gx -> Hx
                ```
    - F, Gに対称性がある．どうするか？
        - 前件のマッチングなどに使いたい．
        - placeholderのpermutation版でマッチングさせればよい．
    - "not バージョン"のルールは任意個できる．これをどう表現するか？
        - placeholderのnot版でマッチングさせればよい．
    - テストケースドリブンでやる．
    - G, Fになってからじゃないと，命題のunificationが取れない．
        ```
            {
                "id": "hyps27",
                "base_scheme_group": "Hypothetical Syllogism 2",
                "scheme_variant": "de_morgan",
                "scheme": [
                    ["(x): (¬${A}x & ¬${B}x) -> ¬${C}x", {"A": "${F}", "B": "${I}", "C": "${G}"}],
                    ["(x): ¬${A}x -> ${B}x", {"A": "${H}", "B": "${G}"}],
                    ["(x): ¬(${A}x v ${B}x) -> ${C}x", {"A": "${F}", "B": "${I}", "C": "${H}"}]
                ],
                "predicate-placeholders": ["F","G","H","I"],
                "entity-placeholders": []
            },        ```
            AがFになったりHになったりしている．
        ```
        G, F でやっておいて，A, Bに戻して，翻訳する．


## 推論ルールの拡充
* \/導入
    ```
    ---- premise ----
    F(a)
    G(a)
    (x) F(x) /\ G(x) -> H(x)

    ---- hypothesis ----
    H(a)

    ```
* syllogismをmodus ponensから導出する．
    ```
    ---- premise ----
    (x) Fx -> G(x)
    (x) Gx -> H(x)

    ---- hypothesis ----
    (x) Fx -> H(x)


    ---- proof ----
    ```
    これを自然演繹で示そうとすると，仮定導入(しかも，自由変数として出現させる)が必要になる．
    ただ，できなくはない，気がする．自由変数は"something"にすればよい．



## full
* ./learning_to_reason/ideas.dataset.md
    * 既存研究との比較
        * ours
            - task
                * deduction
            - 推論ルール
                - **Critical Thinkingよりも増やす．and導入など．**
            - 複合命題(e.g., A->B)の証明
                - **yesにする．RuleTakerではできていなかった．**
            - マルチステップ推論
                - **yesにする．Critical Thinkingではできていなかった．**
            - 言語
                - 形式主義学習などで多様にする．
            - verified on NL dataset: no
            - 公理系
                * predicate logic




# naming
* Q    : atomic formula
* Q v A: logical formula
* v    : logical connective

