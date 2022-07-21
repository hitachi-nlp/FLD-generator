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
                [todo]: notの変換が必要になる．`¬${B}`
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
- notをどのように扱うか？
    - 論理学でのnot
        - /\などと同じように，logical conectiveである．
        - よって，not導入・除去によって初めて現れる．
            * 除去 = 二重否定を消す
    - aacorpusでのnot
        - /\などと同じように，テンプレートとして事前に固定されている．
            * テンプレートとして用意されれている理由は，自然言語に変換するため．
        - よって，/\などと同じように，自動で除去されることは無い．
    - モチーフ
        1. PのpremiseであるGa をデータセットに加え，modus ponens によって，^Faを導出する．
            ```
            Gx -> ^Fx    Ga
            ----------------------
            ^Fa    ^Fa -> Ha
            ----------------------
            Ha
            ```
            2段目のmodus ponensをどう用意するか？
    - 自然言語テンプレートは，notは別物としてそれぞれ用意するべき．なぜならば，notの言語表現は単に`not`をつけるだけでは導けないものおｍあるから．
        * `Fa -> ^Ga` = Fa prevents Ga
        * `^Fa -> Ga` = Ga unless Fa
    - formal logicとしてどう用意するか？
        - まず，2段目のmodus ponensが実際どういう規則で導かれるかというと，
            1. ^Faは論理式である．
            2. 論理式A, Bについて，modus ponensが成り立つ．
            3. Aに^Faを代入する
            である．
        - これはA=^Faだけではなく，A=F/\G, など，あらゆる論理式で成り立つ．
            * それでは，任意の論理式についてmodus ponensを生成しないといけないの？
                - notに限るとしたら，それはどのように正当化されるか？
                    - まぁ，単純化の仮定によって正当化されるのだけれど．
        - 方針
            - **replacementの時に，notの付与も許すことにする．**
    - そもそも，既存のSATの方式ではダメなんだっけ？
        - SAT方式
            - Z3
            - Transformer Generalize
        - 判断理由は，調整が効かないこと，スパース性，などであった気がする．ただ，後者に関してはSAT方式論文では実現できているようである．よって，考え直しても良いかもしれない．







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

