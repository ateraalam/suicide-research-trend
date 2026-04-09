import os
import time
import re
import json
import csv
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

################################################################################
# Utility Functions
################################################################################

def create_folder(folder="./safetylit_records"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def setup_driver():
    options = Options()
    # Uncomment the next line to run headless if desired:
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_ids(html):
    soup = BeautifulSoup(html, "html.parser")
    return [tag["title"] for tag in soup.find_all("abbr", class_="unapi-id") if tag.get("title")]

def parse_bibtex_entries(bibtex_text):
    entries = []
    raw_entries = bibtex_text.split("@article")
    for raw in raw_entries:
        raw = raw.strip()
        if not raw:
            continue
        entry_text = "@article" + raw
        entry_data = {}
        lines = entry_text.splitlines()
        for line in lines:
            if "=" in line:
                try:
                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip().lstrip("{").rstrip("},").strip('"')
                    entry_data[key] = value
                except Exception:
                    continue
        entries.append(entry_data)
    return entries

def separate_authors(author_str):
    if not author_str:
        return None
    return [a.strip() for a in author_str.split(" and ") if a.strip()]

def parse_records_text(text):
    match = re.search(r"Records\s+(\d+)-(\d+)\s+of\s+(\d+)", text)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        total = int(match.group(3))
        return (start, end, total)
    return (0, 0, 0)

def get_total_pages(driver):
    try:
        td_element = driver.find_element(By.XPATH, '//*[@id="paginationForm"]/table/tbody/tr[1]/td')
        records_text = td_element.text
        print("Pagination text:", records_text)
        start_num, end_num, total_records = parse_records_text(records_text)
        display_count = 10
        if total_records:
            computed_pages = (total_records // display_count) + (1 if total_records % display_count else 0)
            return computed_pages
        else:
            return 10
    except Exception as e:
        print("Error in get_total_pages:", e)
        return 10

def get_session_and_pages(driver):
    session = None
    for cookie in driver.get_cookies():
        if cookie["name"] == "PHPSESSID":
            session = cookie["value"]
            break
    pages = get_total_pages(driver)
    return session, pages

def find_next_button(driver, current_page):
    buttons = driver.find_elements(
        By.XPATH,
        '//*[@id="paginationForm"]//input[@type="button" and @class="submit" and @value=">"]'
    )
    if not buttons:
        raise Exception("No next buttons found at all.")
    for btn in buttons:
        onclick = btn.get_attribute("onclick")  # e.g., doSubmit('3')
        m = re.search(r"doSubmit\('(\d+)'\)", onclick)
        if m:
            target_page = int(m.group(1))
            if target_page > current_page:
                return btn
    raise Exception("No valid next button referencing page > current_page.")

################################################################################
# Main Scraper
################################################################################

def main():
    folder = create_folder("./safetylit_records")
    driver = setup_driver()

    # 1) Open the first search results page with all parameters.
    results_url = "https://www.safetylit.org/citations/index.php?fuseaction=citations.summaries_performance&thesfilter=1&find_1=suicide&find_2=self-harm&find_3=suicidal&field_1=textword&find_13=&find_14=&find_15=&op_1=not&find_4=Aptosis&find_5=Artistic&find_6=Assisted&field_2=textword&find_16=Business&find_17=Cellular&find_18=Economic&op_2=not&find_7=Educational&find_8=Financial&find_9=Fiscal&field_3=textword&find_19=Literary&find_20=Molecular&find_21=National&op_3=not&find_10=Political&find_11=Professional&find_12=Social&field_4=textword&find_22=Substrate&find_23=&find_24=&from=1990&to=2004&pub_type=none&categories%5B%5D=24&categories%5B%5D=26&categories%5B%5D=23&categories%5B%5D=25&categories%5B%5D=1&categories%5B%5D=27&categories%5B%5D=2&categories%5B%5D=3&categories%5B%5D=4&categories%5B%5D=5&categories%5B%5D=36&categories%5B%5D=28&categories%5B%5D=35&categories%5B%5D=34&categories%5B%5D=29&categories%5B%5D=6&categories%5B%5D=30&categories%5B%5D=39&categories%5B%5D=7&categories%5B%5D=37&categories%5B%5D=31&categories%5B%5D=38&categories%5B%5D=32&categories%5B%5D=8&categories%5B%5D=40&categories%5B%5D=9&categories%5B%5D=10&categories%5B%5D=33&categories%5B%5D=22&categories%5B%5D=11&categories%5B%5D=12&categories%5B%5D=13&categories%5B%5D=14&categories%5B%5D=15&categories%5B%5D=16&categories%5B%5D=17&categories%5B%5D=21&categories%5B%5D=18&categories%5B%5D=41&categories%5B%5D=19&categories%5B%5D=20"
    driver.get(results_url)
    time.sleep(3)
    print("DEBUG: Current URL:", driver.current_url)
    driver.get(results_url)
    time.sleep(3)
    print("DEBUG: current_url =", driver.current_url)

    # 2) Parse pagination text to determine total pages
    try:
        td_element = driver.find_element(By.XPATH, '//*[@id="paginationForm"]/table/tbody/tr[1]/td')
        records_text = td_element.text
        print("Pagination text:", records_text)
        start_num, end_num, total_records = parse_records_text(records_text)
        if total_records == 0:
            print("Could not parse total records from the page. Defaulting to 10 pages.")
            total_pages = 10
        else:
            display_count = 10
            total_pages = (total_records // display_count) + (1 if total_records % display_count else 0)
    except Exception as e:
        print("Error parsing pagination info:", e)
        total_pages = 10

    print(f"Determined total_pages (computed) = {total_pages}")
    # Force total_pages to 1617
    total_pages = 1617
    print(f"Overriding total_pages to: {total_pages}")

    all_records = []
    current_page = 1

    # 3) Loop through pages to extract data
    while current_page <= total_pages:
        html = driver.page_source
        record_ids = extract_ids(html)
        print(f"Page {current_page}: Found {len(record_ids)} record IDs.")

        if record_ids:
            post_data = {"export": "bib", "export_recs": "|".join(record_ids)}
            headers = {"User-Agent": "Mozilla/5.0"}
            bib_response = requests.post(
                "https://www.safetylit.org/unapi/conversion_all.php",
                data=post_data,
                headers=headers
            )
            if "@article" in bib_response.text:
                entries = parse_bibtex_entries(bib_response.text)
                for entry in entries:
                    authors = separate_authors(entry.get("author", None))
                    record_data = {
                        "title": entry.get("title", ""),
                        "author_details": "; ".join(authors) if authors else "",
                        "author_affiliations": entry.get("affiliation", ""),
                        "journal_name": entry.get("journal", ""),
                        "publication_year": entry.get("year", ""),
                        "language": entry.get("language", ""),
                        "keywords": entry.get("keywords", ""),
                        "doi": entry.get("doi", ""),
                        "research_methodology": entry.get("methodology", ""),
                        "data_source": "SafetyLit",
                        "grant_info": entry.get("grant", ""),
                        "suicide_prevention_measures": entry.get("prevention", ""),
                        "abstract": entry.get("abstract", "")

                    }
                    all_records.append(record_data)
                print(f"Page {current_page}: Processed {len(record_ids)} record IDs.")
            else:
                print(f"Page {current_page}: No valid BibTeX data returned.")
        else:
            print(f"Page {current_page}: No record IDs found on this page.")

        current_page += 1
        try:
            next_button = find_next_button(driver, current_page - 1)
            next_button.click()
            time.sleep(3)
        except Exception as e:
            print(f"No more next button or cannot click next button (page {current_page-1}):", e)
            break

    # 4) Save all records to a master CSV file
    master_csv = os.path.join(folder, "v1.raw_scrape.csv")
    fieldnames = ["title", "author_details", "author_affiliations", "journal_name", "publication_year",
                  "language", "keywords", "doi", "research_methodology", "data_source",
                  "grant_info", "suicide_prevention_measures", "abstract"]
    try:
        with open(master_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in all_records:
                writer.writerow(record)
        print(f"Master CSV saved: {master_csv}")
    except Exception as e:
        print("Error saving CSV:", e)

    # 5) Retrieve PHP session ID from cookies and total pages, then quit.
    session, pages = get_session_and_pages(driver)
    print(f"Session: {session}")
    print(f"Pages (from get_total_pages): {pages}")

    driver.quit()
    return session, pages

if __name__ == "__main__":
    import csv
    session, pages = main()
    print("Final session and pages:", session, pages)
