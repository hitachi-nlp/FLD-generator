import random
import jsonlines
import logging
from logger_setup import setup as setup_logger

from pathlib import Path
import click
from tqdm import tqdm
import pandas as pd


logger = logging.getLogger(__name__)


def get_text_mixer(num_jsonl_files: int, type_: str):
    args_length = num_jsonl_files * 10000
    shuffle_ids = list(range(args_length))
    random.shuffle(shuffle_ids)

    if type_ == 'reuter_gutenberg':
        df_reuters = pd.read_csv('corpora/reuters/polished_stories_trc2v2.csv')
        reuters_length = len(df_reuters)
        logging.info('Length News Corpus: %s', reuters_length)

        # SPGutenberg paragraphs
        file1 = open('corpora/spgutenberg/sub_pgcorpus_split-20200814.txt', 'r')
        parlist = file1.readlines()
        file1.close()
        logger.info('Length PGut Corpus: %s', len(parlist))
    elif type_ == 'MOCK':
        pass
    else:
        raise ValueError()

    def get_mixin_text(id_: int):
        if type_ == 'reuter_gutenberg':
            sid = shuffle_ids[id_]
            if sid >= reuters_length:
                r = parlist[sid - reuters_length]
            else:
                r = df_reuters['story_text'][sid] + '\n'
            return r
        elif type_ == 'MOCK':
            return 'MOCK DISTRACTOR SENTENCE\n'
        else:
            raise ValueError()

    return get_mixin_text


@click.command()
@click.argument('input_dir')
@click.argument('output_dir')
@click.option('--text-mixin-type', type=str, default='reuter_gutenberg')
def main(input_dir, output_dir, text_mixin_type):
    setup_logger(do_stderr=True, level=logging.INFO)

    random.seed()
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # List of all jsonl train files
    input_json_files = list(input_dir.glob('**/*.jsonl'))
    get_mixin_text = get_text_mixer(len(input_json_files), type_=text_mixin_type)

    train01_path = output_dir / 'basic-min.txt'  # basic schemes of Modus barbara, Hypothetical syllogism 1, Generalized Contraposition
    train02_path = output_dir / 'basic-all.txt'  # all basic schemes
    train03_path = output_dir / 'all-all.txt'       # all schemes, basic and variants
    with open(train01_path, 'w') as trainfile01, open(train02_path, 'w') as trainfile02, open(train03_path, 'w') as trainfile03:
        for jlfile in tqdm(input_json_files):
            with jsonlines.open(jlfile) as reader:
                for arg in reader:
                    arg_string = ' '.join([arg['premise'], arg['conclusion']])
                    if (arg['scheme_variant'] == 'base_scheme')\
                            & (arg['base_scheme_group'] in ('Modus barbara', 'Hypothetical Syllogism 1', 'Generalized Contraposition')):
                        trainfile01.write(arg_string + '\n')
                        trainfile01.write(get_mixin_text(arg['id']))

                    if (arg['scheme_variant'] == 'base_scheme'):
                        trainfile02.write(arg_string + '\n')
                        trainfile02.write(get_mixin_text(arg['id']))

                    trainfile03.write(arg_string + '\n')
                    trainfile03.write(get_mixin_text(arg['id']))


if __name__ == '__main__':
    main()
