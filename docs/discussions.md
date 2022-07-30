# todo
## argument
* 疑問: きちんと多様でchainableな命題がたくさん生まれるだろうか？
- 最初に選んだ後に，replacementで膨らませるべき?
    - notなど．
- replacementでは，notだけでなく，&やvも使うべき？
    * 今，premiseに「A & B」が無いので，これがチェインできないことが問題である．
        * これだけであれば，(x) Fx & Gx -> Hx を定理として加えるだけ．
* 個別の事実も入れたい．
    * 「Aa & Ba -> Ca」
    * ベースラインには，全称量化子しか含まれていない．
* 命題論理も．

## その後
* argumentを増やす
    * 命題論理も．
    * notなどは，初手で入れないと現れない．
* "Translation"
* distractor

## future
* ->導入 (仮定の除去)が入れられていない．
* できあがった証明が無矛盾であることを担保する必要がある．今は簡易的なチェックのみを行っている．
    - ダメな例
        - {G, ^G}
        - {(Ea) Ga, (x) Gx -> Fx,  (x) Gx -> ^F(x)}
            - 後者２つだけでは矛盾していないことに注意．
        - その他にも，複数ステップの証明を介して矛盾するものもあるかも．
    - 解決: Z3でsatであることを確認する．
        * [Testing logical equivalences (and more) using Z3 Theorem Prover - DEV Community](https://dev.to/donaldkellett/testing-logical-equivalences-and-more-using-z3-theorem-prover-3k8h)
        * [Programming Z3](https://theory.stanford.edu/~nikolaj/programmingz3.html)
        * [Z3 Playground](https://jfmc.github.io/z3-play/)



# Translation
* todo
    - "アルゴリズム"の実装．Translatorとして実装できる．
    - motivational exampleを取り入れるように．

## 事例と機能
* G -> H = storm cause disastor
    - これをやるには，{G, ->, H} の３つを同時に見る必要がある．
    - また，treeの中でGは共通していないといけないので，tree全体を見る必要もある．
    * 以上より，Translationの入力は1セットのFormulaである必要がある．
        * List[formula] でよいか．
* Ga -> Ha = If storm is severe, the damage will be huge.
* Ga -> Ha = severe storm will cause huge damage.
    * idea: 動詞節か名詞節かの違いで文型を分ければ良い？
* (x): ({A}x & {B}x) -> {C}x
    * "If someone is a {A} and a {B}, then they are a {C}. "
    * small and smart person is always kind.

## アルゴリズム
1. 名詞節 vs 動詞節を決める
2. ドメインを決める (human, objet)
3. predicate, individual を集める．
4. テンプレートに当てはめる．



# 目標
* ./learning_to_reason/ideas.dataset.md
    * 既存研究との比較
        * ours
            - task
                * deduction
            - 推論ルール
                - **Critical Thinkingよりも増やす．and導入など．**
                - "推論ルールの拡充"を参考にすること．
            - 複合命題(e.g., A->B)の証明
                - **yesにする．RuleTakerではできていなかった．**
            - [done] マルチステップ推論
                - **yesにする．Critical Thinkingではできていなかった．**
            - 言語
                - 形式主義学習などで多様にする．
            - verified on NL dataset: no
            - 公理系
                * predicate logic




# 推論ルールの拡充
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



# 考察
* 二重否定をどうするか？
    - 取りあえず，replace関数で処理できるようにしておく．
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
    - 自然言語テンプレートは，notは別物としてそれぞれ用意するべき．なぜならば，notの言語表現は単に`not`をつけるだけでは導けないものもあるから．
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
* 最初のルールのnegation variantsをどのように生成するか？
    - configに対して，replacementをかける．
* [done] データ作成
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
