# tod
* git stash pop
* ng formula系をまとめる
    * ./formal_logic/generators.py の中のロジックをformula.pyにうつす
    * `_is_conclusion_in_premises`を入れると，A v B -> A が排除されてしまう．

* config
    * nonの廃止
    * ness, neg などを追加する．
    * templace noun_clause "{a} that is not " を追加する．
    * it vs one
* 1-pass通す

* 高速化
    - bp16
    - maxlen
    - A100 8並列

* コンポーネントを完成させていく
    * "argument生成"
    * [pending] "distractor"
        - [pending] 翻訳に自然文を使う場合は，手法2も検討する．
    * "translation"
        - "アルゴリズム"の実装．Translatorとして実装できる．
    * "OWA vs CWA"
        - [todo] EBへの転移実験はlabel_true_onlyでやる．
        - [todo] それ以外の実験は，CWAでやる．
* 研究計画を立てる．
    * EBでlow-resource実験をやる．事前学習の重要性が増すので，勝ちが確定する．
    * ablation
        - which scheme useful
        - depth
        - which NL translation is useful
    * schemeの
    * retrieverの学習
    * Transformers as Soft Reasoners over Language
        - Fig.(a) を見ると，公理系を使っているように見える．差分は大丈夫か？


## future
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




# argument生成

## todo
* "パターン"

## [done] 手法
* 手法
    1. replacementで，自動で増やす．
        - 詳細
            * この方法の場合，最初に選んだパターンのreplacementで実現すべき．なぜならば，後段のchainingではパターンを増やす余地はないから．
            * 例えば， A -> (F v G),  A -> (F & G),  A -> ^F などのreplacementでふやす．
        - 考察
            - notだけでなく，&やvも使えるか？
                * 今，premiseに「A & B」が無いので，これがチェインできないことが問題である．
                    * これだけであれば，(x) Fx & Gx -> Hx を定理として加えるだけ．
                * 例えば，modus ponensの「Fx -> Gx」のFが「A & B」に変わった場合，うまく動くか？
                    * できなくもない気がする．replacementを駆使してマッチングを取れるから．
        - Pros
            - 拡張可能性がはある．
        - Cons
            - 調整しにくい．
            - 扱いは難しい．
    2. パターン直書きする．
        - 手法: 先行研究のcomplex predicateのようなもの．
        - Pros
            - 調整は効きやすい．
        - Cons
            - パターンの数が3倍に膨れ上がる．
* 考察
    1. 自然言語のテンプレートは全パターンで自作する必要があるかもしれない．
    2. formal logicは，完全ルールでも作れそう．replacementの最初に，A -> A v B という置き換えを挟むだけ．
        - しかし1があるなら，2を完全ルールでやっても大して工数が減らない？
    3. notをどのように扱うか？ と通じる話がある．
* 方針
    - [done]
        * 自動で増やす方法にトライしてみる．formalもtranslationも．

## パターン
* ルール
    * (x): Fx -> Gx
    * Fa -> Gb
        - If car crashes, human will be injred.
    * A -> B
        - If car crashes, human will be injred.
            - A = car crashes
        - Storm leads to injuries.
            - A = storm
* notの意味
    - ２重否定やドモルガン，あるいはcontrapositionなどを導入しないと，not Aは単なる独立な命題になってしまう．
* [todo] 形式論理の公理系
    * e.g.) & 導入
        ```
        ---- premise ----
        F(a)
        G(a)
        -----------------
        F(a) & G(a)   (x) F(x) /\ G(x) -> H(x)
        -----------------
        H(a)
        ```
* [todo] 命題論理
* [todo] その他，EBに含まれているパターン
* [pending] ->導入
    - 仮定の除去が必要になるので，現行のFWの延長では実現できない．
    - e.g.) syllogismをmodus ponensから導出する．
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
* [rejected] 個別の事実も入れたい．
    * 「Aa & Ba -> Ca」
    * ベースラインには，全称量化子しか含まれていない．

## [done] notをどのように扱うか？
- 背景
    - 論理学でのnot
        - /\などと同じように，logical connectiveである．
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
- 手法
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





# distractor
* 方針
    - [done] 翻訳にテンプレート文を使う場合は，手法1をやる．
    - [pending] 翻訳に自然文を使う場合は，手法2も検討する．
* 手法
    1. Ga がtreeに合ったときに，GbやHaを加える．
        - Pros
            * 述語論理にとって，hard-negativeになる．
            * 実装が容易．
        - Cons
            * テンプレート文しか使えない．
                * もちろん，proofの文がテンプレート文なら，distractorがテンプレート文であっても問題無い．
    2. 表層が似ている自然文をコーパスから取ってきて追加する．
        - Pros
            * proofの文が自然文の場合は，良いnegativeになる．
        - Cons
            * proofの文がテンプレート文の場合は，negativeにはならない．テンプレート的かどうかで判断できてしまうため．







# translation
* todo
    - "アルゴリズム"
        - ドメインの追加
    - "事例"
    * [pending] int nodeの翻訳からは乱数性を消すべきでは？
        - [pending] 問題になりそうだったら考える．この実装はわりと面倒なので?
        - Pros
            - モデルの中間出力のパターンが固定されるので，よりconsistent．学習しやすいかもしれない．
        - Cons
            - int node 全ての言語パターンが固定されてしまうので，表現の多様性は学習しづらくなるかもしれない．
            - 実際，乱数性があったとしても，単にgenerationの1位, 2位に埋め込むから問題無いかもしれない．

## アルゴリズム
1. [done] 名詞節 vs 動詞節を決める
2. [todo] ドメインを決める (human, objet)
3. [done] predicate, individual を集める．
4. [done] テンプレートに当てはめる．

## 事例
* [todo] G -> H = storm cause disastor
    - これをやるには，{G, ->, H} の３つを同時に見る必要がある．
    - また，treeの中でGは共通していないといけないので，tree全体を見る必要もある．
    * 以上より，Translationの入力は1セットのFormulaである必要がある．
        * List[formula] でよいか．
* [done] Ga -> Ha = If storm is severe, the damage will be huge.
* [done] Ga -> Ha = severe storm will cause huge damage.
    * idea: 動詞節か名詞節かの違いで文型を分ければ良い？
* [done] (x): ({A}x & {B}x) -> {C}x
    * "If someone is a {A} and a {B}, then they are a {C}. "
    * small and smart person is always kind.

## [rejected] 複雑な翻訳をどうするか
* 事例
    * `(x): ({F}x v {H}x) -> {G}x`
        - "If someone is F and H then he is G"
        - F and H person is also G
    * `(x): (^{F}x v {H}x) -> {G}x`
        - "If someone is not F and H then he is G"
        - non-F and H person is also G
    * `(x): {F}x -> {G}x & {H}x`
        - "If someone is F then he is G and H"
        - F person is also G and H.
* (F v H) (F & H) みたいなのに限られているのであれば，例えばregexpなどでいけるのでは？

## [done] 辞書
* 必要な機能
    - 語彙の獲得
        - 名詞・動詞・助動詞 の判定
        - 自動詞か他動詞かを判定する．
    - ing (present continuous) へのtense変換
* ライブラリ・辞書
    * 語彙の獲得
        * WordNet
            * [NLTK :: Sample usage for wordnet](https://www.nltk.org/howto/wordnet.html)
        * [rejected] NodeBox
            * [NodeBox](https://www.nodebox.net/code/index.php/Linguistics#verb_conjugation)
                - もう開発が終わっている．ダウンロードできない．
    * ingへの変換
        * [bjascob/pyInflect](https://github.com/bjascob/pyInflect)
            * [Tags](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)

## 考察
* [rejected] notの翻訳として，non- + 形容詞を常に使えるか？
    - 使えない．nickelic などは，non-nickelicという使い方はされない．
* [todo] wordnetの類義語によって，言語表現を膨らませられるか？
    - ノイジーだから微妙かもしれない．
* "not"の翻訳に，wordnetの対義語が使えるか？
    - 使えない．酸性に対して，アルカリ性が対義語になっている．中性や両性があるので，これは誤り．
* [done] v の口語英語について
    * 問題点と対策
        * `or` のような表現は通常，排他的選言を表してしまう．
            * 対策
                - "or both"を付与する
                    * [Exclusive or - Wikipedia](https://en.wikipedia.org/wiki/Exclusive_or#Exclusive_"or"_in_natural_language)
                        - Either A or B **or both**
        * `not or`の意味は，曖昧性がある．
            - `Anna is not beautiful or smart.` => 口語だと，^beautiful(Anna) or ^smart(Anna) という意味に解釈されてしまう．
            - 対策1: notを後ろに持ってくる: `Anna is either smart or not beautiful`
            - 対策2: 動詞の前にeitherを付与する． `Anna either is smart or is not beautiful`
                - **[accepted]** これならば，片方が動詞，片方が形容詞の場合と整合性がとれる: `Anna either does not sing or is smart.`
        * `or`は言い換えの意味になってしまう場合もある．: `It is not beautiful, or, smart` => `It is not beautiful, or in other words, smart.`
    * キワモノ
        * `¬A -> B` として言う．
            - e.g.) `If it is not beautiful, then it is smart.`
            - `A v B`と`¬A -> B`は同値
                - A v B
                    ```
                    A B AvB
                    1 1 1
                    0 1 1
                    1 0 1
                    0 0 0
                    ```
                - ¬A -> B
                    ```
                    A B AvB
                    1 1 1
                    0 1 1
                    1 0 1
                    0 0 0
                ```





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



# OWA vs CWA

## 方針
- [todo] EBへの転移実験はlabel_true_onlyでやる．
- [todo] それ以外の実験は，CWAでやる．
    - 複合命題のnotなどの問題を回避できる．
    - EntailmentBankはCWAに近いので，CWAで一旦十分．
- (時間ができたら) OWAをやる．
    - 例えば，Ga みたいな単体の命題のOWAは簡単に作れる．
    - 一方で，複合命題の否定は自明では無い．

## 手法
* label_true_only
    - あり得るラベル
        - True : 仮説のproofを作成できる．
* CWA
    - あり得るラベル
        - True : 仮説のproofを作成できる．
        - False: 仮説のproofを作成できない．
    - 手法
        - Falseの方は，ProofTreeから適当にnodeを削り取ったものでできる．
* OWA
    - あり得るラベル
        - True   : 仮説のproofを作成できる．
        - False  : not仮説のproofを作成できる．
        - Unknown: 仮説もnot仮説も，proofを作成できない．
    - 手法
        - FalseはCWAと同じやり方で作れる．
        - Unknownは，not仮説を示すことで作れる．
            * ただ，複合命題 (Fx -> Gx)のnotなど，微妙な問題を持っている．




# done
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
