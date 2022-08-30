# todo
* depth
    - 定義をきちんとする．
    - 0も含める？
* 系列が長い．何が効いている見る．
    * pretty printがdepthをきちんと表すようにしたい．
        - depthの数もきちんと定義する．
* not A に it is not the factを追加する
* 初期実験の設定チューニング
    - 系列を短くするように．
* 初期実験
    - 目的: 我々の手法で，きちんと学習ができることを確認する．
    - todo
        - 反証可能な事例
        - 簡単なデータセットで学習してみる．
            - depth
            - leafs
            - distractors
            - rule
* 研究計画を立てる．
    * backward
        * [pending] 元の問題より簡単か，自明で無い．
        * depth firstではなく，子供(=premise)は同時に生成すべきなのでは？
        * merge
        * 取りあえず，元の問題より簡単か = lossが小さくなるか，を見てみる．
    * FLNL (Formal Logic Natural Language) Corpus
    * introで「axiomを使うので，汎化する．」 => case studyで定理
    * EBでlow-resource実験をやる．事前学習の重要性が増すので，勝ちが確定する．
    * ablation
        - which scheme useful
        - depth
        - which NL translation is useful
    * schemeの
    * retrieverの学習
    * Transformers as Soft Reasoners over Language
        - Fig.(a) を見ると，公理系を使っているように見える．差分は大丈夫か？
    * 公理系が未完全な理由をつらつらと述べられるようにしていく．
        - 「tree構造とconsistentな公理を入れた．graphはfuture work」と言い切れないか？
            - 仮定の導入
            - not関連を入れると，背理法が必要となってしまう．
                - 背理法で導けるcontrapositionを使っているので，直観主義論理の中にとどまっている，という訳では無い．
            - (Ex)-elim
    * faithful inference: NLIの間を埋める
    * 仮説検証器
        - 「AIは人間を滅ぼすべきだ」
    * 「示した定理は使って良い」
        - e.g.) generalized modus ponene
    * 本研究，完全性が無い．やはり，完全な体系でやりたい．
    * contextの生成からやらせれば，fact => 証明 すべてを自分でできる．これが目指す最終形態．
    * 背理法 x 自然言語 できれば絶対に面白い．
        - 人工知能学会?
    * 先行研究は (x) のargumentしか無いので，Aa -> Bb などの常識知識は表せていない．
    * デモペーパーを出す
        * 仮説検証マシン
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

## future
* n項述語のn=1, n=0 を合わせた体系は，意味のある体系になっているのだろうか？
    - 完全性など．

















# general
* generatorのデバッグには，line-profilerを使うと良い．どこで止まっているか分かるから．
* 命名規則
    * [論理学の命名規則](https://en.wikipedia.org/wiki/Atomic_formula#Atomic_formula_in_first-order_logic)
        - term = constant + variables + predicate(constant, variable)
        - formula = more complicated ones built by the system's inductive rules.
        - atomic formula = predicate(constant, variable)
    * 論理学を作る (P138)
        - interprete = to map a formula to another formula given a mapping
        - an interpretation ~ a mapping
        - a model ~ an interpretation
    * ours
        - interprand = symbols to be interpreted = predicates + constants
        - pullled formula = a formula which is interpreted by a mapping from that space to this space
        - pushed formula = inverse of pulled formula
* 実行速度
    - 1sec / (1 tree * 1 process)
* depthの定義は soft reasoner 3.1 overviewに従う
    ```
    The facts, rules, and questions are then expressed in (synthetic) English using simple natural language templates. We generate five datasets, each constrained by the maximum depth of inference required to prove the facts used in its questions (up to depths D=0, D≤1, D≤2, D≤3 and D≤5 respectively). Depth D=0 means the true facts can be “proved” by simple lookup in the context (no inference)
    ```

## Known issues
* add_complicated_arguments=False でProofTreeを生成すると，失敗(retry)になりやすい．これは，argumentとしてand_introを選んだ後に，続けられるargumentが無いためである．
    1. and_introのconclusionは ({A} & {B}) という形をしている．
    2. add_complicated_arguments=Falseでは，前提が({A} & {B})の形なのは，& elimだけである．
    3. & elimのconclusionは{A}もしくは{B}であるが，これは1のant_introの前提としてtreeに既に入っている．よって，`_is_formula_new() = False`となるので，& elimの利用は却下される．
    対処療法として，retryを大きくしている．
* ./10.create_formal_logic_corpus.py で投げたジョブの一部が永遠に終わらない．
    - 原因
        - ./create_formal_logic_corpus.py の logger.info('[pass or not checking for finding the cause of hangups] 02')の前で止まっている．
            - while Trueに迷い込んだ？
            - メモリやCPUなどの使用量が大きすぎて終わらない？
            - qsubの問題？
    - 対策
        - 現状， ./10.create_formal_logic_corpus.py でtimeoutすることによって，対処している．
        - [todo] もちろんこれは対処療法に過ぎないので，時間があるときに根本原因を探したい．






# proof tree generation

## todo
* [pending] quantが選ばれる頻度が，頻度重みから想定されるよりも，低い．おそらく，何らかの条件において，排除される確率が高くなっている．
    - [pending] ただ，低すぎて出てこないという訳でもない．よって保留．

## 論証(推論ルール)
* [todo] ルール導入の方針
    * 定理はどれを入れるべきか？
        - EBでよく使われる定理は入れる．転移性能のため．
            - syllogism等
        - 「今回入れられなかった公理」を使わないと導けない定理は入れる．
            - e.g.) not関連の公理を入れられなかった => contraposition, ドモルガンを入れる
        - 論文用に雰囲気を出すため(だけ)に，いろいろと入れる．
- [pending] 主語違いパターン
    - [pending] 少し工数が高いこと．自然言語で頻繁に発生するパターンでは無さそうであること，による．
    - e.g.) Aa v Bb
    - c.f.) Aa v Ba (今現在あるやつら)
    - 実装のための作業
        1. argument configに，主語違いパターンを書き入れる
        2. generate_complicated_argumentsで，主語違いパターンを生み出す
            - これをやらないと，主語違いパターンを持ったargumentが少なくなり，chainable_args=0が発生する．
        3. translation configに主語違いパターンの翻訳を書き込む．
            - 工数が大きい．
- [pending] pred_arg + pred パターン
    - [pending] 少し工数が高いこと．自然言語で頻繁に発生するパターンでは無さそうであること，による．
    - e.g.) Aa v B
    - "主語違いパターン" と同様の作業が発生する．
    - これが実装されていないことによって，pred_argのみでできたtree，もしくはpredのみでできたtreeの2種類に限られてしまい，pred_argとpredの混ざったtreeが作成できていない．
* [pending] -> 導入
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
* [pending] AND + not
    * [pending]
        - 実装コストが割とある．
        - これ無しでも，notの意味は学べる．例えば，contrapositionみたいなので．
            - というか，not関連のパターンは２重否定の除去から全て導ける．
    * やりたいこと
        * not(A v B) みたいのを扱う．
        * 上記のドモルガンバージョンを扱う．
    * 上記のパターンを追加した場合，consistency checking 周りも更新する必要があると思う．
* [pending] (Ex)-intro: F(a) := (Ex) F(x)
    - 現在，(Ex)-elimが実装されていないので，(Ex) F(x)を前提に持つargumentが存在しない．よって，(Ex) F(x)を導いてしまうと，chainable_args=0となり， ProofTreeGenerationFailure()になってしまうため．
* [pending] 定理: (x): Fx -> Gx, (x): Fx := (x) Gx
    - これを証明するには，(x)-introが必要なので，現状の公理系では導けない．
    - しかし，このパターンは自然言語では多く無さそうなので，入れない．
    - このパターンを入れないことによって，(x): Fx といったleaf_nodeから親を生成することができず， ProofTreeGenerationFailure()が発生することに注意．
    - 例
* [done] notの意味を表現する．
    - [done] contraposition
    - [done] ドモルガン

## [pending] 無矛盾性の担保
* [pending] できあがった証明が無矛盾であることを担保する必要がある．今は簡易的なチェックのみを行っている．
    - [pending] 現状，そこまで問題になっていない．
        1. 述語のパターンを増やしたので，衝突する頻度が小さく，簡易的なチェックで十分機能している．
    - ダメな例
        - {G, ^G}
        - {(Ea) Ga, (x) Gx -> Fx,  (x) Gx -> ^F(x)}
            - 後者２つだけでは矛盾していないことに注意．
        - その他にも，複数ステップの証明を介して矛盾するものもあるかも．
    - 解決: Z3でsatであることを確認する．
        * [Testing logical equivalences (and more) using Z3 Theorem Prover - DEV Community](https://dev.to/donaldkellett/testing-logical-equivalences-and-more-using-z3-theorem-prover-3k8h)
        * [Programming Z3](https://theory.stanford.edu/~nikolaj/programmingz3.html)
        * [Z3 Playground](https://jfmc.github.io/z3-play/)




# [done] distractor

## 手法
1. [done] Ga がtreeに合ったときに，GbやHaを加える． (UnkownPASDistractor)
    - Pros
        * 述語論理にとって，hard-negativeになる．
        * 実装が容易．
    - Cons
        * テンプレート文しか使えない．
            * もちろん，proofの文がテンプレート文なら，distractorがテンプレート文であっても問題無い．
2. [done] SameFormUnkownInterprandsDistractor
3. [rejected] 表層が似ている自然文をコーパスから取ってきて追加する．
    - [rejected] easy negativeであること，コストがかかること．
    - Pros
        * proofの文が自然文の場合は，hard negativeになる．
    - Cons
        * proofの文がテンプレート文の場合は，easy negativeになってしまう．"テンプレート的"かどうかで判断できてしまうため．
        * 外部リソースが必要となるので，若干コストがかかる．







# translation

## [todo]
* [todo] 変な表現
    * [todo] データセット公開時には，2のconfigを分けることにより，この表現を除く．
    * 例: ProofNode(Formula("{OU}{a} -> ({IP}{a} v ¬{TN}{a})", transl="a servile aminomethane leads to the aminomethane that either is anamnestic or is not unsexy or both"))
    * なぜこれが起こるか？
        1. {A}{a} -> {B}{b} = {A}{a} leads to {B}{b} は自然．
        2. {A}{a} -> {B}{a} = {A}{a} leads to {B}{b} は不自然． {A}{a} is {B} が自然．
            - e.g.) red apple is tasty
        * 2の翻訳を1で代用していることに起因する問題．
            - 2を1で代用するのは，config発散を防ぐため．

## [todo] 事例
* [todo] 表現の追加
    - EntailmentBank
    - cause verb
* [todo] can_be系の precisionを上げるため，anyによる判定は辞めて，get_synsetsで一番最初のやつ(=最も蓋然性が高いやつ？)だけ使うべき？
    - [todo] precisionを高くした後の語彙数を調べる．これが十分なのであれば，precisionを上げて良い．
    - precisionを上げる
        - Pros
            - 言語的な不自然さが無くなるので，事前学習からの悪影響が小さくなる．
        - Cons
            - 語彙を絞りすぎると，偏りが生じるので，逆に悪影響があるかもしれない．
* [pending] ({A}{a} & {B}{a}), ({A}it & {B}it), ({A}x & {B}x) をテンプレート化してまとめる．
    - [pending] 割と理解しづらくなるような気がしている．また，{a}, it, x, the_thing の4つまでで増えないかもしれない．
    - Pros
        * テンプレートの種類が減るので，ミスがおこりづらい．
            - 現状，{a}, it, x, the_thing と，4倍になっている．これらはコピーペーストで作られる．
    - Cons
        * configが複雑になり，理解しづらくなる．
    - 手法
        * ({A}@hoge@ & {B}@hoge@) みたいのを用意する．
        * keyの解決が必要．nlの解決ではない．
* [pending] 複数形，単数形, 冠詞
    - pending
        - [pending] 文法チェッカーとかで簡易実装できないだろうか？
    - 方針
        - [pending] countableの一般論は複数形か不定冠詞(a/an) + 単数形
            * [done] 不定冠詞(a/an) + 単数形
            * [pending] 複数形
                * 複数形を入れると，is/are [VERB.s]/[VERB.normal]のテンプレート両方を入れる必要があり，複雑化ｓる．
                * 複数形 vs 単数形の判断は難しい
        - [pending] uncountableの一般論は，不定冠詞を付けずに単数形
            * [pending] 単語は全てcountableだとして近似する．多くの単語はcountable/uncountable両方で使えるのでcountableとして扱って問題が生じないこと，同様の理由でuncountable/countableの判断が難しいこと，による．
                * [here](https://stackoverflow.com/questions/7822922/noun-countability) for example.
            * countable / uncountableの区別を付けたいなら，適当なリソースを使うべき．
                * [Category:Uncountable nouns - Simple English Wiktionary](https://simple.wiktionary.org/wiki/Category:Uncountable_nouns).
    - 事例
        * {G}{a}
            - An apple is red.
        * {G}x -> {F}x
            - If something is red, then it is kind.
        * {G}{a} -> {F}{a}
            - If an apple is red, then it is kind.
        * {G}{a} -> {F}{b}
            - If a car crashes, then people is injured.
    - 参考資料
        * [英語で、ある名詞の一般論を述べるとき、単数形、定冠詞、複数形とでそれぞれどんなニュアンスの違いがあるのか？ - 根性による３ヶ国語学習者の日記](https://yaseteru.hatenablog.com/entry/2022/03/07/072635)
        - 自然さでいうと，apples are red > an apple is red
* [pending] term_mappingを先に選んでしまうと，missが発生しやすい．for loopで回したい．
    - [pending] 今現在は，configで指定される語句と，translator.pyが使う語句を合わせているのでmissは発生しない．ただし，将来的にこれが乖離せざるを得ない状況は考えられる．


## [pending] その他
* [pending] wordnetの類義語によって，言語表現を膨らませられるか？
    - ノイジーだから微妙かもしれない．
* [pending] int nodeの翻訳からは乱数性を消すべきでは？
    - [pending] 問題になりそうだったら考える．この実装はわりと面倒なので?
    - Pros
        - モデルの中間出力のパターンが固定されるので，よりconsistent．学習しやすいかもしれない．
    - Cons
        - int node 全ての言語パターンが固定されてしまうので，表現の多様性は学習しづらくなるかもしれない．
        - 実際，乱数性があったとしても，単にgenerationの1位, 2位に埋め込むから問題無いかもしれない．

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




# world assumption

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
