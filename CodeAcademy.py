import csv
import json
import os
import threading
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

name = "CodeAcademy"
encoding = "utf-8"
thread_count = 10
semaphore = threading.Semaphore(thread_count)


def getCourse(href):
    with semaphore:
        url = f"https://www.codeacademy.com{href}"
        file = f"{name}-courses/{href.replace('/', '_')}.json"
        if os.path.isfile(file):
            print(f"Already scraped {url}")
            return
        print("Working on", url)
        try:
            soup = getSoup(url)
            # input(soup.prettify())
            data = {
                "Course": soup.find('title').text.split('|')[0].strip(),
                "URL": url,
                "Details": soup.find('div',{"data-testid":"markdown"}).text.strip(),
                # "Language": soup.find('title', string="Available languages").text,
                "Platform": name,
                # "Logo": soup.find('meta', {'property': 'og:image'})['content'],
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
    soup = getSoup('https://www.codecademy.com/catalog/all')
    # print(soup.prettify())
    for li in soup.find('h2', string="Courses").parent.find_all('li'):
        getCourse(li.find('a')['href'])
    combineJson()


def logo():
    print(r"""
 _____           _       ___                _                      
/  __ \         | |     / _ \              | |                     
| /  \/ ___   __| | ___/ /_\ \ ___ __ _  __| | ___ _ __ ___  _   _ 
| |    / _ \ / _` |/ _ \  _  |/ __/ _` |/ _` |/ _ \ '_ ` _ \| | | |
| \__/\ (_) | (_| |  __/ | | | (_| (_| | (_| |  __/ | | | | | |_| |
 \____/\___/ \__,_|\___\_| |_/\___\__,_|\__,_|\___|_| |_| |_|\__, |
                                                              __/ |
                                                             |___/ 
====================================================================
             CodeAcademy scraper by @evilgenius786
====================================================================
[+] CSV/JSON/XLSX files will be saved in the current directory
[+] Without browser
[+] API based
____________________________________________________________________
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
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}
    return BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')


if __name__ == '__main__':
    main()
