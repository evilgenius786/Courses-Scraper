import csv
import json
import os
import traceback

import cloudscraper
import openpyxl
from bs4 import BeautifulSoup

name = "MasterClass"
encoding = "utf-8"


def combineJson():
    data = []
    for file in os.listdir(f"{name}-courses"):
        with open(f"{name}-courses/{file}", "r", encoding=encoding) as f:
            data.append(json.loads(f.read()))
    with open(f"{name}.csv", "w", encoding=encoding, newline='') as f:
        c = csv.DictWriter(f, data[0].keys())
        c.writeheader()
        c.writerows(data)
    convert(f"{name}.csv")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    # csv.field_size_limit(sys.maxsize)
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


def getMasterclass(href):
    url = f"https://www.masterclass.com{href}"
    file = f"{name}-courses/{url.split('/')[-1][1:]}.json"
    if os.path.isfile(file):
        print(f"Already scraped {url}")
        return
    print("Working on", url)
    soup = getSoup(url)
    try:
        script = json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).text)
    except:
        traceback.print_exc()
        print(soup.prettify())
        # print("Error")
        return
    course = script['props']['pageProps']['course']
    data = {
        "Course": course['title'],
        "URL": url,
        # "Cost":"",
        "Details": course['overview'],
        # "Language": soup.find('title', string="Available languages").text,
        "Platform": name,
        "Logo": course['cinematic12x5'],
        "Filter": " > ".join(course['categoriesLabel'].split(",")) + " > " + course['title'],
    }
    # print(json.dumps(data, indent=4))
    with open(file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def main():
    if not os.path.exists(f"{name}-courses"):
        os.makedirs(f"{name}-courses")
    url = "https://www.masterclass.com/categories/all-classes"
    # url = "https://www.masterclass.com/classes/madeleine-albright-and-condoleezza-rice-teach-diplomacy#details"
    soup = getSoup(url)
    # print(soup.prettify())
    for course in soup.find_all('a', class_='c-button c-button--secondary c-button--full-width'):
        try:
            getMasterclass(course['href'])
        except:
            traceback.print_exc()
            print(course['href'])
    combineJson()


def getSoup(url):
    return BeautifulSoup(cloudscraper.create_scraper().get(url).text, 'html.parser')


def logo():
    print(r"""
    ___  ___             _               _____  _                  
    |  \/  |            | |             /  __ \| |                 
    | .  . |  __ _  ___ | |_  ___  _ __ | /  \/| |  __ _  ___  ___ 
    | |\/| | / _` |/ __|| __|/ _ \| '__|| |    | | / _` |/ __|/ __|
    | |  | || (_| |\__ \| |_|  __/| |   | \__/\| || (_| |\__ \\__ \
    \_|  |_/ \__,_||___/ \__|\___||_|    \____/|_| \__,_||___/|___/
=========================================================================   
        MasterClass courses scraper by @evilgenius786                                                    
=========================================================================
[+] CSV/JSON/XLSX Output
[+] Without browser
[+] Resumable
_________________________________________________________________________                                                       

""")


if __name__ == '__main__':
    main()
