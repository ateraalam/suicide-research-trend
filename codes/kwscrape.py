# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 10:53:03 2025

@author: cdbha
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from time import sleep
import pandas as pd
import os


def getKeywords(author, title, driver):
    pubmed = 'https://pubmed.ncbi.nlm.nih.gov/advanced/'

    print(f'Starting search for: {str(title)}')
    sleep(0.5)

    print('\tLoading page...')
    authone = str(author).split(' and ')[0]
    title = str(title)
    driver.get(pubmed)

    sleep(1)

    print('\tExecuting search...')
    select_el = driver.find_element(By.ID, 'field-selector')
    select = Select(select_el)

    select.select_by_value('Author')
    searchbar = driver.find_element(By.ID, 'id_term')
    searchbar.send_keys(authone + Keys.ENTER)

    select.select_by_value('Title')
    searchbar.send_keys(title + Keys.ENTER)

    button = driver.find_element(By.CLASS_NAME, 'search-btn')
    button.click()

    keys = []
    print('\tLooking for keywords...')
    try:
        mesh = driver.find_element(By.ID,
                                   'mesh-terms').find_element(By.CLASS_NAME,
                                                              'keywords-list')

        buttons = mesh.find_elements(By.TAG_NAME, 'button')

        for button in buttons:
            keys.append(button.text.strip())
        sleep(1)
    except Exception:
        keys.append('N\\A')
        sleep(1)
    print(f'Keywords found: {keys}')

    return keys


def main(file_path):

    options = Options()
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/bib")
    options.set_preference("browser.helperApps.alwaysAsk.force", False)

    driver = webdriver.Firefox(options=options)
    df = pd.read_csv(file_path + r'\v2.scrubbed_data.csv')
    for index, row in df.iterrows():
        if pd.isna(row['keywords']) or row['keywords'] == '':
            df.at[index, 'keywords'] = getKeywords(row['author_details'], row['title'], driver)

            print('Writing to CSV...\n')
            df.to_csv(file_path + r'\bibwithkw.csv', index=False)

        else:
            print('Already found! Skipping...\n')

    print(df[['author_details', 'title', 'keywords']])
    df.to_csv(file_path + r'\bibwithkw.csv', index=False)

    driver.close()

if __name__ == '__main__':
    # Setup for web driver:
    options = Options()
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/bib")
    options.set_preference("browser.helperApps.alwaysAsk.force", False)

    driver = webdriver.Firefox(options=options)

    main()
