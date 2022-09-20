import csv
import json
import os.path
import threading
import traceback
from urllib.parse import urlparse

import openpyxl
import requests
from bs4 import BeautifulSoup

semaphore = threading.Semaphore(100)
encoding = 'utf-8'


def combineJsonToCsv():
    with open('theknowledgeacademy.csv', 'w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'URL', 'Price', 'Details', 'Language', 'Platform', 'Logo',
                                               'Filter'])
        writer.writeheader()
        for i in os.listdir('theknowledgeacademy'):
            with open(f"theknowledgeacademy/{i}", encoding=encoding, errors='ignore') as f:
                try:
                    writer.writerow(json.load(f))
                except:
                    traceback.print_exc()
                    print(f"Error in {i}")
    convert("theknowledgeacademy.csv")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    count = 0
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
            count += 1
    wb.save(filename.replace("csv", "xlsx"))


def parseListings(course):
    url = course.find("a")['href']
    file = getFileName(url)
    if os.path.isfile(file):
        print(f"Already scraped {url}")
        return
        # with open(file, "r") as f:
        #     return json.load(f)
    with semaphore:
        print(f"Scraping {url}")
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        data = {
            "Name": course.find("a")['data-name'],
            "URL": url,
            "Price": course.find("div", {"class": "price"}).find('span').text,
            "Details": soup.find("div", {"id": "showmoreoverview"}).text.strip(),
            "Language": "English",
            "Platform": "theknowledgeacademy",
            "Logo": "https://www.theknowledgeacademy.com/" + course.find("img")['src'],
            "Filter": soup.find("div", {"class": "breadcrums"}).text.strip(),
        }
        # print(json.dumps(data, indent=4))
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


def main():
    logo()
    if not os.path.isdir("theknowledgeacademy"):
        os.mkdir("theknowledgeacademy")

    # return
    if not os.path.isfile("theknowledgeacademy.json"):
        getListings()
    else:
        threads = []
        with open("theknowledgeacademy.json", "r") as f:
            soup = BeautifulSoup(json.load(f)['Data'], 'lxml')
            for course in soup.find_all("div", {"class": "courses-item"}):
                # print(course)
                threads.append(threading.Thread(target=parseListings, args=(course,)))
                threads[-1].start()
        for thread in threads:
            thread.join()
        combineJsonToCsv()


def getListings():
    data = {
        # 'search': '',
        # 'sort': '',
        'page': '0',
        'CatalogueData': '1',
        'LIMIT': '1559',
        'OFFSET': '0'
    }
    response = requests.post('https://www.theknowledgeacademy.com/admin/ajax/catalogue/catalogue.php', data=data)
    print(response.text)
    with open("theknowledgeacademy.json", "w") as f:
        json.dump(response.json(), f, indent=4)


def getFileName(url):
    return "theknowledgeacademy/" + urlparse(url).path.replace("/", "_") + ".json"


def logo():
    print(r"""
  ______ __           __ __                         __           __        ___                            __                       
 /_  __// /_   ___   / //_/ ____   ____  _      __ / /___   ____/ /____ _ /   |  ____ _ _____ ____ _ ____/ /___   ____ ___   __  __
  / /  / __ \ / _ \ / ,<   / __ \ / __ \| | /| / // // _ \ / __  // __ `// /| | / __ `// ___// __ `// __  // _ \ / __ `__ \ / / / /
 / /  / / / //  __// /| | / / / // /_/ /| |/ |/ // //  __// /_/ // /_/ // ___ |/ /_/ // /__ / /_/ // /_/ //  __// / / / / // /_/ / 
/_/  /_/ /_/ \___//_/ |_|/_/ /_/ \____/ |__/|__//_/ \___/ \__,_/ \__, //_/  |_|\__,_/ \___/ \__,_/ \__,_/ \___//_/ /_/ /_/ \__, /  
                                                                /____/                                                    /____/   
==================================================================================================================================
                                theknowledgeacademy scraper by github.com/evilgenius786
==================================================================================================================================
[+] Scraping theknowledgeacademy.com
[+] Resumable
[+] CSV/JSON output
__________________________________________________________________________________________________________________________________
""")


if __name__ == '__main__':
    main()
