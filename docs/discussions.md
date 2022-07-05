# todo
* "要求機能"


# 要求機能
* multi step
* 他の言語テンプレート
* 命題論理化
* 推論ルールの多様化

## NLProofSへの変換

* 入力
    - `./res/data/SYL01-2020-10-24-144K/jsonlines/SYL01-2020-10-24-144K-gmt0-train.jsonl`
        ```
        {
          "id": 195481,
          "premise": "Here comes a perfectly valid argument: First of all, it is not the case that Connie is a rare consumer of Eucalyptus soap. Next, every frequent consumer of Nubian Heritage soap is a rare consumer of Eucalyptus soap. We may conclude that",
          "conclusion": " it is false that Connie is a frequent consumer of Nubian Heritage soap.",
          "scheme_id": "gmt0",
          "domain_id": "consumers_personalcare",
          "base_scheme_group": "Generalized modus tollens",
          "scheme_variant": "base_scheme",
          "permutate_premises": "True"
        }
        ```
* 出力
    * ./data/proofwriter-dataset-V2020.12.3/preprocessed_OWA/depth-3/meta-dev.jsonl
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


