import statistics
from typing import Tuple
import json
from collections import defaultdict
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('t5-base')


def get_stats(sentence: str) -> Tuple[int, int, float]:
    tokens = tokenizer.tokenize(sentence)

    num_tokens_org = len(sentence.split(' '))
    num_tokens_tokenized = len(tokens)
    ratio = num_tokens_tokenized / num_tokens_org

    return num_tokens_org, num_tokens_tokenized, ratio


ratios = []

for line in open('./samples/dataset_name=20220830.distractor.jsonl'):
    instance = json.loads(line.rstrip('\n'))
    context = instance['context']
    num_tokens_org, num_tokens_tokenized, ratio = get_stats(context)
    ratios.append(ratio)


print(f'number of tokens before and after tokenization ratio:  {statistics.mean(ratios)} +- {statistics.stdev(ratios)}')
