#!/usr/bin/env python
import logging
from typing import Set
from pathlib import Path
import json

from nltk.stem.wordnet import WordNetLemmatizer as WNL
import click


logger = logging.getLogger(__name__)


@click.command()
@click.option('--input-dir',
              type=str,
              default='/groups/1/gca50126/honoka/work/projects/NLProofS/data/proofwriter-dataset-V2020.12.3/preprocessed_OWA/depth-3ext')
@click.option('--output-path', default='./outputs/C00.build_ruletaker_vocab/vocab.json')
def main(output_path,
         input_dir):
    input_dir = Path(input_dir)
    output_path = Path(output_path)

    vocab: Set[str] = set()
    wnl = WNL()
    for input_json_file in input_dir.glob('**/*.jsonl'):
        for line in open(str(input_json_file), 'r'):
            data = json.loads(line.strip('\n'))
            words = [word.strip(',') for word in data['context'].split(' ')]
            for word in words:
                vocab.add(wnl.lemmatize(word).lower())

    output_path.parent.mkdir(exist_ok=True, parents=True)
    print(f'writing into "{str(output_path)}"')
    json.dump(sorted(vocab),
              open(str(output_path), 'w'),
              ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


if __name__ == '__main__':
    main()
