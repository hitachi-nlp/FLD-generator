# todo
* ours: ./outputs/00.create_json_corpus/20220705.trial/org/test/mb7-test.jsonl
* gold: ./res/data/20201106-TEST_ONLY-SYL02/jsonlines/20201106-TEST_ONLY-SYL02-mb7-test.jsonl
* "要求機能"



# 要求機能
* multi step
* 他の言語テンプレート
* 命題論理化
* 推論ルールの多様化

## NLProofSへの変換
* 入力
    - "./outputs/00.create_json_corpus/20220705.trial/org/test/mb7-test.jsonl"
        ```
        {
          "conclusion": " Stegosaurus is a descendant of Diplodocus.",

          "premise": "Consider the following argument: If someone is neither a successor of Archaeopteryx nor a contemporary of Triceratops, then they are a descendant of Diplodocus. Moreover, it is not the case that Stegosaurus is a successor of Archaeopteryx or a contemporary of Triceratops. Thus,",


          "id": "test-1",
          "scheme_id": "mb7",
          "domain_id": "dinos",
          "base_scheme_group": "Modus barbara",
          "scheme_variant": "de_morgan",
          "permutate_premises": "True",
          "split": " descendant of Diplodocus.",
          "split_extended": " a descendant of Diplodocus.",
          "split_inversed": " not a descendant of Diplodocus."
        }
        ```
* 出力
    * "./data/proofwriter-dataset-V2020.12.3/preprocessed_OWA/depth-3/meta-dev.jsonl"
        ```json
        {
          "hypothesis": "the lion needs the lion",

          "context": "sent1: if something sees the lion and it visits the lion then it is young sent2: the lion visits the cow sent3: the lion is nice sent4: if something needs the cow then the cow visits the lion sent5: the lion is blue sent6: the lion sees the cow sent7: the cow visits the lion sent8: if something is blue and it needs the lion then it sees the lion sent9: the cow is cold sent10: the cow is young sent11: if something sees the lion then it is cold sent12: the lion needs the cow sent13: if something is blue then it needs the lion sent14: if something visits the cow and the cow needs the lion then the cow sees the lion sent15: the cow needs the lion sent16: the cow is kind sent17: the lion is kind sent18: the cow sees the lion sent19: if something needs the cow then it is blue sent20: if something is young then it needs the lion",

          "proofs": [
            "sent5 & sent13 -> hypothesis;",
            "sent12 & sent19 -> int1: the lion is blue; sent13 & int1 -> hypothesis;"
          ],
          "answer": true,
          "depth": 1
        }
        ```
