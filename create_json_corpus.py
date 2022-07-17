import random
import json
from pathlib import Path
import logging
from typing import Dict, Union

import click
from logger_setup import setup as setup_logger
from tqdm import tqdm
import jsonlines
from aacorpus import pipeline


def create_json(config: Dict,
                scheme_id: str,
                split: str,
                size: int,
                output_dir: Union[Path, str]):

    domain_ids = [domain['id'] for domain in config['domains']]

    output_json_path = Path(output_dir) / f'{scheme_id}-{split}.jsonl'
    arg_id = 1
    with jsonlines.open(str(output_json_path), mode='w') as writer:
        for _ in range(size):
            argument = pipeline(
                config,
                random.choice(domain_ids),
                scheme_id,
                permutate_premises=True,
                argument_id=f'{split}-{str(arg_id)}',
                split_arg = True if split == 'test' else False)
            arg_id = arg_id + 1
            writer.write(argument)

    return True


@click.command()
@click.argument('corpus-name')
@click.argument('split', type=click.Choice(['train', 'valid', 'test']))
@click.option('--output-dir', default='./corpora')
@click.option('--config', default='./configs/conf_syllogistic_corpus-02.json')
@click.option('--size', type=int, default=None)
def main(corpus_name, split, output_dir, config, size):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed()

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    config = json.load(open(config))
    scheme_ids = [s['id'] for s in config['formal_argument_schemes']]
    for scheme_id in tqdm(scheme_ids):
        create_json(config, scheme_id, split, size, output_dir)


if __name__ == '__main__':
    main()
