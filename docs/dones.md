# proof tree generation

## todo
* [done] 凄く遅い．
* [done]
    * 選ばれるルールに偏りが無いか．
        * たくさん流してstatsを見てみたところ，割とまんべんなくサンプリングされているように見える．
* [done] 現状，pred_argの頻度が小さい．
    * [done] generator で，失敗したときのtraceを出す．特定のパターンで常に失敗していたらいやなので．
* [done] どこまでが命題論理で，どこまでが述語? => A. 量化があれば述語論理．それ以外は，命題論理．
    - 考え方
        1. {A}{a} -> {B}{a}, {A}{a} := {B}{a} という論証を考える．このとき，量化が無いのであれば，{A}{a} = P, {B}{b} = Q と置き直すことによって，P -> Q, P := R と書き直すことができる．よって，この論証実際のところ，命題論理である．
            * **「命題論理の命題を，述語{A},{B}や定数{a}{b}を使って表現しているだけ」**と考えれば良い．
        2. 量化がなされたとき，この置き換えはできなくなる．
            * (x): {A}x -> {B}x, {A}{a} := {B}{a}
                1. xに{a}などのあらゆる定数を入れた式をP, Q, R と置いていけば，"真理値の意味"で，等価な命題論理は作れる気がする．
                2. しかし，これは前者の述語論理が後者の命題論理と同じであることを意味しない．後者と"真理値の意味で等価"な体系を量化子で表現したものを述語論理と呼んでいる．よって，述語論理を表現するためには，量化子をそのまま表現する必要がある．
* [done] 命題論理
    - 定理
        - 取りあえず，"基本的な"，すなわち，他の定理を導くときに良く使えそうな以下の定理を入れている．
            - syllogism
            - contraposition
* [done] 述語論理
    - [done] 常識推論ルールは命題論理にも見える．重複した場合，どうするか？
        - [pending] argumentの同一性を見て除去する．
            - argumentの同一性判定の実装が面倒．
        - [done] idの同一性を見て，除去する．
    - [done] 常識推論ルールを入れたい．
        1. [rejected] Ga -> Fa
            - 推論ルールにこれを入れる必要は無い．2に含まれているから．
            - Ga -> Fa, Ga := Fa
        2. [done] Ga -> Fb
            - Ga -> Fb, Ga := Fb
    - [done] 公理系
        ```
        (x) Fx -> Gx  Fa
        ----------------
        Ga


        (x) Fx -> Gx
        ----------------
        Fa -> Ga   Fa
        ---------------
        Ga





        ---- premise ----
        F(a)
        G(a)
        -----------------
        F(a) & G(a)   (x) F(x) /\ G(x) -> H(x)
        -----------------
        H(a)
        ```
    - [done] quantifierの公理をどのように入れるか．
        - 事例
            ```
            {
                "id": "mb0",
                "base_scheme_group": "Modus barbara",
                "scheme_variant": "base_scheme",
                "premises": [
                    "(x): {F}x -> {G}x",
                    "{F}{a}"
                ],
                "conclusion": "{G}{a}"
            },
            ```
            これの証明は，以下
            ```
            (x): {F}x -> {G}x
            ----------------------- ()-elim
            {F}{a} -> {G}{a}    {F}{a}
            ----------------------- ->-elim
            {G}{a}
            ```
        - 手法
            1. [done] ()-elimを導入する．
                * 任意の論理式を表す必要がある．
                    * 論理式全パターンを手で列挙
                    * 自動でパターンを増やす．
                        - argumentのpremise, conclusionの論理式を全て列挙して，x化すればよい．
                        * [done] 重複チェックが必要
                    * 自動で制生成する．
                * 例
                    ```
                    (x): {F}x -> {G}x
                    ----------------------- ()-elim
                    {F}{a} -> {G}{a}    {F}{a}
                    ----------------------- ->-elim
                    {G}{a}
                    ```
            2. [rejected] 既存の推論ルールに関して，()版の推論ルールを作る．
                - [rejected] ここで作成する推論ルールは，1を用いて定理として示せる．よって，蛇足ではある．
                - 例: ()- modus ponens
                    ```
                    (x): {F}x -> {G}x  {F}{a}
                    ----------------------- generalized ()-elim
                    {G}{a}
                    ```
                    元バージョン
                    ```
                    {F}{a} -> {G}{a}  {F}{a}
                    ----------------------- ()-elim
                    {G}{a}
                    ```
                - これは，先行研究と同じ手法であると言える．
    * [rejected] 命題論理との混合
        * [rejected] 工数の割に効果が小さそう．
        * e.g.) {A}{a} and {B}

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



# translation

## [todo] 事例
* [rejected] {A}{a} に対して，`That {a} is {A}`というtranslationを加える．
    - [rejected] verb_clauseとほぼ同じになるので，表現を膨らませる効果が無さそう．
* [done] 問題
    * 課題
        1. "{noun_clause.{A}x} is {noun_clause.{B}x}." に noun_clauseである`That x is A`が入らないこと．
        2. "{noun_clause.{A}} is {noun_clause.{B}}." に noun_clauseである`That A occurs`が入らないこと．
    * 考察
        * {A}x
            - {A}x.subj
                - x that is A
                - A x
            - {A}x.fact
                - That x is A
    * 方針1
        - isは主語が共有されている場合のみ．
            * 課題2は解決．
    * translation
        1. G[NOUN] -> F[NOUN]
            - Hard storm leads to injured people.
            - That storm occurs leads to that people are injured.
        2. G[NOUN]a -> F[NOUN]b
            - Hard storm leads to injured people.
            - That storm occurs leads to that people are injured.
        3. G[NOUN]a -> F[NOUN]a
            - A red apple is kind apple.
            - That apple is red leads to that apple is kind.
        3より2が先に出ることを保証する．
* [done] G -> H = storm cause disastor
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
* [done] ./log.txt
    - translation Ax -> Bx のヒットが少ない．
        * {A}x はotherに入っている？
            * [todo] (x): {A}x がtranslationに存在しない
                - というか，implicationが無い(x): .. が全て存在しない．
        * [done] Ax -> Bxが少ないのは？
            - 単にそれらのargumentが当たる頻度が少ないだけであることを確認した．translationのせいでは無い．
        * [rejected] generalized modus ponensが無いから？
            * generalized modus ponensは定理としてしか導けから？
                - これは違う．(x)-elimだけあれば，利用されるはず．
* [done] not the fact が入っていない．
* [done] {A}{a} & {B}{b} => {A}{a} & {B}{a}
* [done] {A}{a} -> (¬{B}{b} v {C}{b})
    - 中身が間違っている．
* [done] Ga -> Fa, Ga -> Fb を別の翻訳にする．
    - プログラムで"a" -> "the"と変えるようにした．
* [done] the, it, a などの整合性
* [done] it はプログラムでやれば？
    - is
* [done] warningが出ないことを確認する．


## その他
- [done] 命題論理のA, B のAに，verb_clauseを入れたい
    - [done] 現状，{A}{a} -> {B}{b} というルールを書くのがもっとも易しい．
        * {A} の翻訳を verb_clause にするのはtranslator実装上，非常にコストが高い．
            * 我々のFWにおいて，{A}というのは命題記号ではなく，述語を表していることが根本原因
    - [rejected] 現状だと，A -> noun_clause なので，"If A is B then C is D" "If C is D then E is F" := "If A is B then E is F" のような英語で表されるsyllogismを表現できていない．
        * A, B などを文に置き換えるか？

* [rejected] notの翻訳として，non- + 形容詞を常に使えるか？
    - 使えない．nickelic などは，non-nickelicという使い方はされない．
* [rejected] "not"の翻訳に，wordnetの対義語が使えるか？
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
* [done] not + {and, or}
    * notのスコープは基本的に，notの後ろ全てと解釈される．
        * The apple is not new and red.  = リンゴは新しくて赤いものではありません。 = ¬ (new & red)
        * The apple is not new or red.   = リンゴは新しくもなく、赤くもない。       = ¬ (new v red) = ¬new and ¬red
    * 例外
        * [rejected] The apple is not new but red.  = リンゴは新品ではなく、赤色です。         = ¬ new & red
            - not but は口語的には，2つの形容詞に反義的なつながりがあることを仮定している．よって， つながりの無い形容詞でこの表現を使うのは，言語的にはおかしい．
            - さらに，EntailmentBankに "not but"という表現があるようには思えないので，転移実験のプラスにもならない．
        * The apple is not new and is not red.  = リンゴは新しくもなく、赤くもない。         = ¬new & ¬red

## [done] アルゴリズム
1. [done] 名詞節 vs 動詞節を決める
2. [rejected] ドメインを決める (human, objet)
    - EBへの転移で必要なのはobjectのみである
3. [done] predicate, individual を集める．
4. [done] テンプレートに当てはめる．

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



