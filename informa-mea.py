import csv
import json
import os.path
import threading
import traceback
from urllib.parse import urlparse

import openpyxl
import requests
from bs4 import BeautifulSoup

semaphore = threading.Semaphore(10)
encoding = 'utf-8'


def scrapeCourse(i):
    with semaphore:
        url = i['url']
        print(f"Working on {url}")
        file = getFileName(url)
        if os.path.isfile(file):
            return json.load(open(file))
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        data = {
            "Name": soup.find("h1").text,
            "URL": url,
            "Price": i['offers']['price'],
            "Details": soup.find("div", {"class": "et_pb_all_tabs"}).text.strip(),
            "Language": ", ".join([op.text for op in soup.find("select", {"name": "language"}).find_all('option')]),
            "Platform": "informa-mea",
            "Logo": i['image'],
            "Filter": soup.find("div", {"class": "detailbrd"}).text.strip(),
        }
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
        print(data)
        return data


def combineJsonToCsv():
    with open('informa-mea.csv', 'w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'URL', 'Price', 'Details', 'Language', 'Platform', 'Logo',
                                               'Filter'])
        writer.writeheader()
        for i in os.listdir('informa-mea'):
            with open(f"informa-mea/{i}", encoding=encoding, errors='ignore') as f:
                try:
                    writer.writerow(json.load(f))
                except:
                    traceback.print_exc()
                    print(f"Error in {i}")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    count = 0
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
            count += 1
    if count > 1:
        wb.save(filename.replace("csv", "xlsx"))
    else:
        os.remove(filename)


def main():
    logo()
    if not os.path.isdir('informa-mea'):
        os.mkdir('informa-mea')
    if not os.path.isfile('informa-mea.json'):
        getList()
    elif not os.path.isfile('informa-mea.json'):
        with open('informa-mea.json') as f:
            array = json.load(f)
        threads = []
        for i in array:
            threads.append(threading.Thread(target=scrapeCourse, args=(i,)))
        for i in threads:
            i.start()
        for i in threads:
            i.join()
    else:
        combineJsonToCsv()
        convert('informa-mea.csv')
    print("Done")


def getFileName(url):
    return "informa-mea/" + urlparse(url).path.replace("/", "_") + ".json"


def getList():
    array = []
    for i in range(0, 5):
        data = {
            'ajaxsearch': '1',
            'topic': '',
            'tableview': 'listview',
            'page': f'{i}',
            'sort_order': '',
            'limitperpage': '100'
        }
        response = requests.post('https://www.informa-mea.com/registration/', data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            js = json.loads(soup.find_all('script', {"type": "application/ld+json"})[1].text)
            array.extend(js)
            print(js)
        except:
            print(soup)
    with open('informa-mea.json', 'w') as f:
        json.dump(array, f, indent=4)


def logo():
    print(r"""
  ___         __                              __  __            
 |_ _| _ _   / _| ___  _ _  _ __   __ _  ___ |  \/  | ___  __ _ 
  | | | ' \ |  _|/ _ \| '_|| '  \ / _` ||___|| |\/| |/ -_)/ _` |
 |___||_||_||_|  \___/|_|  |_|_|_|\__,_|     |_|  |_|\___|\__,_|
==================================================================
       informa-mea.com scraper by github.com/evilgenius786
==================================================================
[+] Scraping informa-mea.com
[+] API Based
[+] Resumable
[+] JSON Output
__________________________________________________________________
""")


if __name__ == '__main__':
    main()
