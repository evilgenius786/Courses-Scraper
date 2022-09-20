import csv
import json
import os
import traceback

import openpyxl
import requests
from bs4 import BeautifulSoup

encoding = "utf-8"


def getCourse(url):
    print(f"Working on {url}")
    name = url.split('/courses/')[1].replace("/about", "").replace("/", "_")
    file = f"doroob/{name}.json".replace(":", "_")
    # print(file)
    if os.path.isfile(file):
        print(f"Already scraped ({file}) ({url}).")
        with open(file, "r", encoding=encoding) as f:
            return json.load(f)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    data = {
        "Course": soup.find('h1').text.strip(),
        "URL": url,
        # "Cost": "Free",
        "Details": soup.find("div", {"class": "details"}).text.strip(),
        # "Language": "",
        "Platform": "Doroob",
        "Logo": f"https://lms.doroob.sa{soup.find('div', {'class': 'hero'}).find('img')['src']}",
        # "Filter": f'{h1} > {cat}'.strip()
    }
    print(json.dumps(data, indent=4, ensure_ascii=False))
    with open(file, "w", encoding=encoding) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    if not os.path.isdir("doroob"):
        os.mkdir("doroob")
    # getCourse('https://lms.doroob.sa/courses/course-v1:Doroob+W.S-CSCIN005+NOV2021/about')
    soup = BeautifulSoup(requests.get('https://lms.doroob.sa/courses').text, 'html.parser')
    for course in soup.find_all('div', {'class': 'course-catalog__item'}):
        getCourse(f"{course.find('a')['href']}")
    combineJson()


def combineJson():
    data = []
    for file in os.listdir("doroob"):
        with open(f"doroob/{file}", "r", encoding=encoding) as f:
            try:
                data.append(json.load(f))
            except:
                print(f"Error {file}")
                traceback.print_exc()
    with open("doroob.csv", "w", encoding=encoding, newline='') as f:
        c = csv.DictWriter(f, fieldnames=data[0].keys())
        c.writeheader()
        c.writerows(data)
    convert("doroob.csv")
    print("Done")


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


if __name__ == '__main__':
    main()
