#!/usr/bin/env python
import time
import json
from typing import Iterable, Dict, Optional
from pathlib import Path
from pprint import pformat
import logging

import click

import requests
from bs4 import BeautifulSoup

from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def scrape_word_list(url: str) -> Iterable[str]:
    next_page_url = url
    while next_page_url is not None:
        logger.info(next_page_url)
        response = requests.get(next_page_url)
        response.encoding = response.apparent_encoding
         
        bs = BeautifulSoup(response.text, 'html.parser')

        for group in bs.find_all('div', class_='mw-category-group'):
            for anchor in group.find_all('a'):
                yield anchor.get('title')

        next_page_path = None
        for anchor in bs.find_all('a'):
            if anchor.string == 'next page':
                next_page_path = anchor.get('href')
                break
        if next_page_path is not None:
            next_page_url = 'https://en.wiktionary.org/' + next_page_path
        else:
            next_page_url = None

        time.sleep(0.3)


@click.command()
@click.option('--output-dir', default='./res/word_banks/english')
def main(output_dir):
    setup_logger(do_stderr=True, level=logging.INFO)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
     
    with open(output_dir / 'transitive_verbs.txt', 'w') as f_out:
        for word in scrape_word_list('https://en.wiktionary.org/wiki/Category:English_transitive_verbs'):
            f_out.write(word + '\n')

    with open(output_dir / 'intransitive_verbs.txt', 'w') as f_out:
        for word in scrape_word_list('https://en.wiktionary.org/wiki/Category:English_intransitive_verbs'):
            f_out.write(word + '\n')

    logger.info('done all!')


if __name__ == '__main__':
    main()
