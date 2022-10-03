import csv
import json
import os
import threading
import time
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

name = "CreativeLive"
encoding = "utf-8"
thread_count = 10
semaphore = threading.Semaphore(thread_count)


def getCourse(href):
    with semaphore:
        url = href
        file = f"{name}-courses/{url.split('/')[-1]}.json"
        if os.path.isfile(file):
            print(f"Already scraped {url}")
            return
        print("Working on", url)
        try:
            soup = getSoup(url)
            data = {
                "Course": soup.find('meta', {'property': 'og:title'})['content'],
                "URL": soup.find('meta', {'property': 'og:url'})['content'],
                "Cost": f"{soup.find('meta', {'property': 'og:price:amount'})['content']} "
                        f"{soup.find('meta', {'property': 'product:price:currency'})['content']}",
                "Details": soup.find('h2', {"class": "h3 text-uppercase"}).parent.text.strip(),
                # "Language": soup.find('title', string="Available languages").text,
                "Platform": soup.find('meta', {'property': 'og:site_name'})['content'],
                "Logo": soup.find('meta', {'property': 'og:image'})['content'],
                "Filter": " > ".join([span.text.replace(">", "").strip() for span in
                                   soup.find('div', {'class': 'bread-crumbs one-line small-text-mobile'}).find_all(
                                       'span') if span.text.strip() != ">"]),
            }
            print(json.dumps(data, indent=4))
            with open(file, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        except:
            traceback.print_exc()
            print(f"Error on url {url}")


def getSoup(url):
    return BeautifulSoup(requests.get(url).text, 'html.parser')


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


def getUrls():
    total = 2213
    per_page = 24
    for i in range(1, int(total / per_page) + 2):
        file = f"{name}-pages/{i}.txt"
        if os.path.isfile(file):
            print(f"Already scraped {i}")
            continue
        url = f"https://www.creativelive.com/catalog?page={i}"
        print("Working on", url)
        soup = getSoup(url)
        # print(soup.prettify())
        urls = [url['href'] for url in soup.find_all('a', {'class': 'black'})[1:]]
        print(urls)
        with open(file, 'w') as outfile:
            outfile.write("\n".join(urls))


def startUrls():
    threads = []
    for file in os.listdir(f"{name}-pages"):
        with open(f"{name}-pages/{file}", "r", encoding=encoding) as f:
            for url in f.read().splitlines():
                threads.append(threading.Thread(target=getCourse, args=(f"https://www.creativelive.com{url}",)))
                threads[-1].start()
                # time.sleep(0.1)
    for thread in threads:
        thread.join()


def main():
    # getCourse('https://www.creativelive.com/class/fundamentals-of-photography-john-greengo-2018')
    # return
    logo()
    if not os.path.isdir(f"{name}-courses"):
        os.mkdir(f"{name}-courses")
    if not os.path.isdir(f"{name}-pages"):
        os.mkdir(f"{name}-pages")
    getUrls()
    startUrls()
    combineJson()


def logo():
    print(r"""
    _________                        __  .__             .____    .__              
    \_   ___ \_______   ____ _____ _/  |_|__|__  __ ____ |    |   |__|__  __ ____  
    /    \  \/\_  __ \_/ __ \\__  \\   __\  \  \/ // __ \|    |   |  \  \/ // __ \ 
    \     \____|  | \/\  ___/ / __ \|  | |  |\   /\  ___/|    |___|  |\   /\  ___/ 
     \______  /|__|    \___  >____  /__| |__| \_/  \___  >_______ \__| \_/  \___  >
            \/             \/     \/                   \/        \/             \/ 
=========================================================================================
           CreativeLive courses scraper by @evilgenius786
=========================================================================================
[+] CSV/JSON/XLSX files will be saved in the current directory
[+] Without browser
[+] API based
_________________________________________________________________________________________
""")


if __name__ == '__main__':
    main()
