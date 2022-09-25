import csv
import json
import os
import threading
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

encoding = 'utf8'
semaphore = threading.Semaphore(10)


def scrapeCourse(u):
    file = f"udemy_courses/{u.replace('/', '_')[1:]}.json"
    if os.path.isfile(file):
        # print(f"Already scraped {u}")
        try:
            # with open(file, "r", encoding=encoding) as f:
            #     return json.load(f)
            return
        except:
            print(f"Error {file}")
            traceback.print_exc()
    with semaphore:
        url = f"https://www.udemy.com{u}"
        print(f"Working on {url}")
        try:
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            data = {
                "Course": soup.find('h1').text,
                "URL": url,
                "Cost": soup.find('meta', {'property': "udemy_com:price"})['content'] if soup.find('meta', {
                    'property': "udemy_com:price"}) else "Free",
                "Details": soup.find('div', {"data-purpose": "course-description"}).find('div').text,
                "Language": soup.find('div', {"data-purpose": "lead-course-locale"}).text,
                "Platform": "Udemy",
                "Logo": soup.find('meta', {'property': "og:image"})['content'],
                "Filter": " > ".join(
                    [x.text.strip() for x in soup.find("div", {"class": "udlite-breadcrumb"}).find_all('a')])
            }
            print(json.dumps(data, indent=4, ensure_ascii=False))
            with open(file, "w", encoding=encoding) as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return data
        except:
            print(f"Error {url}")
            # traceback.print_exc()
            with open("udemy_errors.txt", "a", encoding=encoding) as f:
                f.write(url + "\n")


def getCourses(cid, pageno=1):
    file = f"udemy_pages/{cid}_{pageno}.json"
    if os.path.isfile(file):
        # print(f"Already scraped {cid} {pageno}")
        with open(file, encoding=encoding) as f:
            return json.load(f)
    params = (
        ('p', pageno),
        ('page_size', '60'),
        ('category_id', cid),
        ('source_page', 'category_page'),
        ('locale', 'en_US'),
        ('currency', 'usd'),
        ('navigation_locale', 'en_US'),
        # ('skip_price', 'true'),
        ('sos', 'pc'),
        ('fl', 'cat'),
    )
    res = requests.get('https://www.udemy.com/api-2.0/discovery-units/all_courses/', params=params).json()
    with open(file, 'w', encoding=encoding) as f:
        json.dump(res, f, indent=4)
    return res


def processCategory(category):
    print(f"Working on category {category.text}")
    unit = getCourses(category['data-id'])['unit']
    total_pages = unit['pagination']['total_page']
    print(f"Total pages: {total_pages}")
    threads = []
    for page in range(1, total_pages + 1):
        print(f"Working on page {page}")
        for course in unit['items']:
            threads.append(threading.Thread(target=scrapeCourse, args=(course['url'],)))
            threads[-1].start()
        unit = getCourses(category['data-id'], page)['unit']
    for thread in threads:
        thread.join()


def getCategories():
    soup = BeautifulSoup(requests.get('https://www.udemy.com/').text, 'lxml')
    # print(soup.prettify())
    for category in soup.find_all('a', {'class': 'js-side-nav-cat', "data-id": True}):
        # print("Category class"+category['class'])
        if "subcat" in str(category['class']):
            print(f"Skipping subcategory {category.text}")
            continue
        try:
            processCategory(category)
            combineJson()
        except:
            traceback.print_exc()


def main():
    logo()
    for d in ["udemy_pages", "udemy_courses"]:
        if not os.path.isdir(d):
            os.mkdir(d)
    combineJson()
    getCategories()
    # scrapeCourse('/course/ios-13-app-development-bootcamp/')


def combineJson():
    data = []
    for file in os.listdir("udemy_courses"):
        with open(f"udemy_courses/{file}", "r", encoding=encoding) as f:
            try:
                data.append(json.load(f))
            except:
                print(f"Error {file}")
                traceback.print_exc()
    with open("udemy.csv", "w", encoding=encoding, newline='') as f:
        c = csv.DictWriter(f, fieldnames=data[0].keys())
        c.writeheader()
        c.writerows(data)
    convert("udemy.csv")
    print("Done")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            try:
                ws.append(row)
            except:
                print(f"Error {row}")
                traceback.print_exc()
    wb.save(filename.replace("csv", "xlsx"))


def logo():
    print(r"""
     __    __   _______   _______ .___  ___. ____    ____ 
    |  |  |  | |       \ |   ____||   \/   | \   \  /   / 
    |  |  |  | |  .--.  ||  |__   |  \  /  |  \   \/   /  
    |  |  |  | |  |  |  ||   __|  |  |\/|  |   \_    _/   
    |  `--'  | |  '--'  ||  |____ |  |  |  |     |  |     
     \______/  |_______/ |_______||__|  |__|     |__|     
=============================================================
        Udemy courses scraper by @evilgenius786
=============================================================
[+] API Based
[+] No login required
[+] CSV/JSON output
_____________________________________________________________
""")


if __name__ == '__main__':
    main()
