import csv
import json
import math
import os
import traceback

import cloudscraper
import openpyxl
import requests
from bs4 import BeautifulSoup

name = "DataCamp"
encoding = "utf-8"


def getCourse(href):
    url = href
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
        "Details": course['description'],
        # "Language": soup.find('title', string="Available languages").text,
        "Platform": name,
        # "Logo": course['cinematic12x5'],
        "Filter": " > ".join([track['title'] for track in course['tracks']]) + " > " + course['title'],
    }
    # print(json.dumps(data, indent=4))
    with open(file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def getSoup(url):
    return BeautifulSoup(cloudscraper.create_scraper().get(url).text, 'html.parser')


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


def main():
    logo()
    if not os.path.isdir(f"{name}-courses"):
        os.mkdir(f"{name}-courses")
    api = 'https://www.datacamp.com/_next/data/u36Osysd7EQtPklFb3Ghr/courses-all.json'
    data = json.loads(getSoup(api).text)
    nbHits = data['pageProps']['nbHits']
    for i in range(2, math.ceil(nbHits / 30)+1):
        print(f"Working on page {i}")
        for course in data['pageProps']['hits']:
            slug = course['slug']
            url = f"https://www.datacamp.com/courses/{slug}"
            data = {
                "Course": course['title'],
                "URL": url,
                # "Cost":"",
                "Details": course['description'],
                # "Language": soup.find('title', string="Available languages").text,
                "Platform": name,
                # "Logo": course['cinematic12x5'],
                # "Filter": " > ".join([track['title'] for track in course['tracks']]) + " > " + course['title'],
            }
            file = f"{name}-courses/{slug}.json"
            with open(file, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        data = json.loads(cloudscraper.create_scraper().get(api, params={'page': i}).text)
    combineJson()


def logo():
    print(r"""
 _______       ___   .___________.    ___       ______     ___      .___  ___. .______   
|       \     /   \  |           |   /   \     /      |   /   \     |   \/   | |   _  \  
|  .--.  |   /  ^  \ `---|  |----`  /  ^  \   |  ,----'  /  ^  \    |  \  /  | |  |_)  | 
|  |  |  |  /  /_\  \    |  |      /  /_\  \  |  |      /  /_\  \   |  |\/|  | |   ___/  
|  '--'  | /  _____  \   |  |     /  _____  \ |  `----./  _____  \  |  |  |  | |  |      
|_______/ /__/     \__\  |__|    /__/     \__\ \______/__/     \__\ |__|  |__| | _|      
=========================================================================================
           DataCamp courses scraper by @evilgenius786
=========================================================================================
[+] CSV/JOSN/XLSX files will be saved in the current directory
[+] Without browser
[+] API based
_________________________________________________________________________________________
""")


if __name__ == '__main__':
    main()
