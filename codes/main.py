# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 07:53:39 2025

@author: W. Hall

IE 7475 Project Main File

This is the master code file that
runs all of our code in sequence,
making reproducing our group's
work simple and efficient.

This code will:
    1) Scrape SafetyLit for all available
    required data

    2) Use NLP and other sites to produce
    missing data points

    3) Clean and validate all data

"""

import os
import SafetyLit_Scraper, kwscrape, methscrape, doi_scraper
import grantscraper, preventionscraper, datavalidationfixed
from rich import print


def main(dir_path):
    print('Running primary scraper...')
    SafetyLit_Scraper.main()
    input('Scraping done!\nPlace scrubbed data in v2.scrubbed_data.csv')
    print('Running keyword scraper...')
    kwscrape.main(dir_path)
    print('Running methodology scraper...')
    methscrape.main(dir_path)
    print('Running DOI scraper...')
    doi_scraper.main(dir_path)
    print('Running grant scraper...')
    grantscraper.main(dir_path)
    print('Running prevention scraper...')
    preventionscraper.main(dir_path)
    print('Running data validation...')
    datavalidationfixed.main(dir_path)


if __name__ == '__main__':
    # Set current directory as working directory
    dir_path = os.path.dirname(os.path.realpath(__file__)) + r'\safetylit_records'
    main(dir_path)
