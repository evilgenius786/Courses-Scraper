import csv
import json
import os
import threading
import traceback
from urllib.parse import urlparse

import openpyxl
import requests
from bs4 import BeautifulSoup

encoding = "utf8"
semaphore = threading.Semaphore(10)


def scrapeCourse(course):
    url = course.find("a").get("href")
    file = getFileName(url)
    if os.path.isfile(file):
        print(f"{url} already scraped.")
        return
    with semaphore:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        try:
            price = soup.find("div", {"id": "usd_price_next"})
            if not price:
                price = soup.find("div", {"id": "usd_price"})
            data = {
                "Name": course.find("div", {"class": "course-title"}).text.strip(),
                "URL": url,
                "Price": price.find("h4").text.strip(),
                "Details": soup.find("div", {"id": "nav-overview"}).text.strip(),
                "Language": course.find("div", {"class": "course-language"}).text.strip(),
                "Platform": "meirc",
                "Logo": soup.find("div", {"class": "common-banner-image"}).find("img")['src'],
                "Filter": url.split(".com/")[-1].replace("/", " > ").replace("-", " ").title()
            }
            print(json.dumps(data, indent=4))
            with open(file, "w", encoding=encoding) as f:
                json.dump(data, f, indent=4)
        except:
            traceback.print_exc()
            print(f"Error in {url}")
            with open("error.html", "w", encoding=encoding) as f:
                f.write(soup.prettify())


def combineJsonToCsv():
    with open('meric.csv', 'w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'URL', 'Price', 'Details', 'Language', 'Platform', 'Logo',
                                               'Filter'])
        writer.writeheader()
        for i in os.listdir('meric'):
            with open(f"meric/{i}", encoding=encoding, errors='ignore') as f:
                try:
                    writer.writerow(json.load(f))
                except:
                    traceback.print_exc()
                    print(f"Error in {i}")


def getFileName(url):
    return "meric/" + urlparse(url).path.replace("/", "_") + ".json"


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


def main():
    logo()
    if not os.path.isdir('meric_categories'):
        os.mkdir('meric_categories')
    if not os.path.isdir('meric'):
        os.mkdir('meric')
    spawnCategory()
    threads = []
    for category in os.listdir('meric_categories'):
        print(f"Scraping category {category}")
        soup = BeautifulSoup(open(f"./meric_categories/{category}", encoding='utf8',errors='ignore').read(), "lxml")
        for course in soup.find_all("div", {"class": "courselisting-col"}):
            threads.append(threading.Thread(target=scrapeCourse, args=(course,)))
            threads[-1].start()
    for thread in threads:
        thread.join()
    combineJsonToCsv()
    convert("meric.csv")


def spawnCategory():
    # Process all categories at once!!
    # processCategory("0")
    # Process one category at a time
    cat_soup = BeautifulSoup(requests.get("https://www.meirc.com/categories").text, "lxml")
    for category in cat_soup.find_all("div", {"class": "categorypage-content h-100 d-inline-block"}):
        try:
            processCategory(category.find("a").get("href").split("/")[-1])
        except:
            print(f"Error in category {category.find('a').get('href').split('/')[-1]}")
            traceback.print_exc()


def processCategory(category):
    file = f"./meric_categories/{category}.html"
    if os.path.isfile(file):
        print(f"{category} already scraped.")
        return
    url = f"https://www.meirc.com/training-courses/{category}"
    if category == "0":
        url = "https://www.meirc.com/training-courses"
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    total = soup.find("input", {"id": "total_course_count"})['value']
    print(f"Found {total} courses in ({category}) category")
    courses = ""
    for i in range(0, int(total) + 1, 24):
        print(f"Scraping page {i} of {total}")
        headers = {'x-requested-with': 'XMLHttpRequest'}
        data = {
            'row': f'{i}',
            'cat_uri': f'{category}',
            'course_type': '0',
            'month': '0',
            'lang': '0',
            'city': '0',
            'year': '0'
        }
        x = ""
        if category == "0":
            x = "upcoming_"
        response = requests.post(f'https://www.meirc.com/categories/{x}auto_scroll_data', headers=headers, data=data)
        courses += response.text
    with open(file, "w", encoding='utf8') as f:
        f.write(courses)


def logo():
    print(r"""
                     .__                 
      _____    ____  |__|_______   ____  
     /     \ _/ __ \ |  |\_  __ \_/ ___\ 
    |  Y Y  \\  ___/ |  | |  | \/\  \___ 
    |__|_|  / \___  >|__| |__|    \___  >
          \/      \/                  \/ 
==============================================
      meirc.com scraper by @evilgenius786
==============================================
[+] Scraping courses from meirc.com
[+] Without browser
[+] API Based
______________________________________________
""")


if __name__ == '__main__':
    main()
