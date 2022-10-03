import csv
import json
import os
import re
import threading
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

name = "Linkedin"
encoding = "utf-8"
thread_count = 10
semaphore = threading.Semaphore(thread_count)

with open('linkedin-cookie.txt', 'r') as cfile:
    cookie = cfile.read().strip()

api = "https://www.linkedin.com/learning-api/searchV2"
req = "L5hEE1hhTnuGVRZHQUgsOQ%3D%3D"
count = 50


def getCourse(slug):
    with semaphore:
        url = f"https://www.linkedin.com/learning/{slug}"
        file = f"{name}-courses/{slug}.json"
        if os.path.isfile(file):
            print(f"Already scraped {url}")
            return
        print("Working on", url)
        try:
            soup = getSoup(url)
            data = {
                "Course": soup.find('title').text.split('|')[0].strip(),
                "URL": soup.find('meta', {'property': 'og:url'})['content'],
                "Details": soup.find('section',
                                     {"class": "show-more-less-html course-details__description"}).text.strip(),
                # "Language": soup.find('title', string="Available languages").text,
                "Platform": soup.find('meta', {'property': 'og:site_name'})['content'],
                "Logo": soup.find('meta', {'property': 'og:image'})['content'],
                "Filter": " > ".join([a.text for a in soup.find_all('a', {"class": "breadcrumb__link"})]),
            }
            if "totalPrice" in str(soup):
                price = json.loads(re.search(r'"totalPrice":(.*?)}-->', str(soup)).group(1))
                data["Cost"] = f"{price['amount']} {price['currencyCode']}"
            print(json.dumps(data, indent=4))
            with open(file, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        except:
            traceback.print_exc()
            print(f"Error on url {url}")


def getSlugs():
    for topic in ['creative', 'business', 'technology']:
        print("Working on topic", topic)
        url = f"{api}?categorySlugs=List({topic})&q=categorySlugs&searchRequestId={req}&sortBy=RELEVANCE&count={count}"
        response = requests.get(url, headers=getheaders()).json()
        total = response['data']['paging']['total']
        print(f"Total {topic} courses: {total}")
        for i in range(0, min(total, 1000), count):
            file = f"{name}-slugs/{topic}-{i}.json"
            if os.path.isfile(file):
                print(f"Already scraped {topic}({i})")
                continue
            u = f"{url}&start={i}"
            print(f"Working on {u}")
            response = requests.get(u, headers=getheaders()).json()
            with open(file, 'w') as jfile:
                json.dump(response, jfile, indent=4)


def processSlugs():
    threads = []
    for file in os.listdir(f"{name}-slugs"):
        with open(f"{name}-slugs/{file}", "r", encoding=encoding) as f:
            data = json.loads(f.read())
            for course in data['included']:
                if "slug" in course:
                    threads.append(threading.Thread(target=getCourse, args=(course['slug'],)))
                    threads[-1].start()
    for thread in threads:
        thread.join()


def main():
    # getCourse('ux-foundations-multidevice-design-2')
    # input("Press enter to exit")
    logo()
    if not os.path.isdir(f"{name}-courses"):
        os.mkdir(f"{name}-courses")
    if not os.path.isdir(f"{name}-slugs"):
        os.mkdir(f"{name}-slugs")
    # getSlugs()
    # processSlugs()
    combineJson()


def logo():
    print(r"""
    .____    .__        __              .___.__        
    |    |   |__| ____ |  | __ ____   __| _/|__| ____  
    |    |   |  |/    \|  |/ // __ \ / __ | |  |/    \ 
    |    |___|  |   |  \    <\  ___// /_/ | |  |   |  \
    |_______ \__|___|  /__|_ \\___  >____ | |__|___|  /
            \/       \/     \/    \/     \/         \/ 
===============================================================
  Linkedin courses (formerly lynda) scraper by @evilgenius786
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


def getheaders():
    return {
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'cookie': cookie,
        'csrf-token': 'ajax:7524689687418270255',
        'user-agent': 'Mozilla/5.0',
        'x-restli-protocol-version': '2.0.0'
    }


def getSoup(url):
    return BeautifulSoup(requests.get(url).text, 'html.parser')


if __name__ == '__main__':
    main()
