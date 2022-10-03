import csv
import json
import os
import threading
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

name = "Brilliant"
encoding = "utf-8"
thread_count = 10
semaphore = threading.Semaphore(thread_count)


def getCourse(href):
    with semaphore:
        url = f"https://brilliant.org{href}"
        file = f"{name}-courses/{href.replace('/','_')}.json"
        if os.path.isfile(file):
            print(f"Already scraped {url}")
            return
        print("Working on", url)
        try:
            soup = getSoup(url)
            data = {
                "Course": soup.find('title').text.split('|')[0].strip(),
                "URL": soup.find('meta', {'property': 'og:url'})['content'],
                "Details": soup.find('div',{"class":"text"}).find('div').text.strip(),
                # "Language": soup.find('title', string="Available languages").text,
                "Platform": name,
                "Logo": soup.find('meta', {'property': 'og:image'})['content'],
                # "Filter": " > ".join([a.text for a in soup.find_all('a', {"class": "breadcrumb__link"})]),
            }
            # if "totalPrice" in str(soup):
            #     price = json.loads(re.search(r'"totalPrice":(.*?)}-->', str(soup)).group(1))
            #     data["Cost"] = f"{price['amount']} {price['currencyCode']}"
            print(json.dumps(data, indent=4))
            with open(file, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        except:
            traceback.print_exc()
            print(f"Error on url {url}")


def main():
    logo()
    if not os.path.isdir(f"{name}-courses"):
        os.mkdir(f"{name}-courses")
    soup = getSoup('https://brilliant.org/courses/')
    for a in soup.find_all('a',{"test-id":"course_item_link","href":True}):
        getCourse(f"{a['href']}")
    combineJson()


def logo():
    print(r"""
    __________        .__.__  .__  .__               __   
    \______   \_______|__|  | |  | |__|____    _____/  |_ 
     |    |  _/\_  __ \  |  | |  | |  \__  \  /    \   __\
     |    |   \ |  | \/  |  |_|  |_|  |/ __ \|   |  \  |  
     |______  / |__|  |__|____/____/__(____  /___|  /__|  
            \/                             \/     \/      
===============================================================
             Brilliant scraper by @evilgenius786
===============================================================
[+] CSV/JSON/XLSX files will be saved in the current directory
[+] Without browser
[+] API based
________________________________________________________________
""")


def combineJson():
    data = []
    for file in os.listdir(f"{name}-courses"):
        with open(f"{name}-courses/{file}", "r", encoding=encoding) as f:
            try:
                data.append(json.load(f))
            except:
                traceback.print_exc()
                print(f"Error {file}")
    with open(f"{name}.csv", "w", encoding=encoding, newline='') as f:
        c = csv.DictWriter(f, data[0].keys())
        c.writeheader()
        c.writerows(data)
    convert(f"{name}.csv")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


def getSoup(url):
    return BeautifulSoup(requests.get(url).text, 'html.parser')


if __name__ == '__main__':
    main()
