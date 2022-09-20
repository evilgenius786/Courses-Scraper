import csv
import json
import os.path
import traceback
from urllib.parse import quote

import openpyxl
import requests
from bs4 import BeautifulSoup

encoding = "utf-8"


# url="https://www.edlal.org/"
def getCourcse(u, logo, h1):
    url = f"https://www.edlal.org{u}"
    name = h1.replace('/', '_').replace('"', "_")
    file = f"edlal/{name}.json"
    if os.path.isfile(file):
        print(f"{h1} already scraped.")
        with open(file, "r", encoding=encoding) as f:
            return json.load(f)
    print(f"Working on {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    cat = soup.find("a", {"itemprop": "category"})
    if not cat:
        cat = "Other"
    else:
        cat = cat.text
    data = {
        "Course": h1,
        "URL": url,
        "Cost": "Free",
        "Details": soup.find("div", {"id": "brief"}).text.strip(),
        # "Language": "",
        "Platform": "Edlal",
        "Logo": f"http:{logo}",
        "Filter": f'{h1} > {cat}'.strip()
    }
    print(json.dumps(data, indent=4, ensure_ascii=False))
    with open(file, "w", encoding=encoding) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    if not os.path.isdir("edlal"):
        os.mkdir("edlal")
    url = "https://www.edlal.org/view-courses/"
    combineJson()
    return
    while url != "#":
        print(f"Working on page {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        for course in soup.find("ul", {"id": "course-cards"}).find_all('li', {"class": "course-card"}):
            try:
                getCourcse(course.find("a")["href"], course.find("img")["src"], course.find("h1").text)
            except:
                print(f"Error {course.text}")
                traceback.print_exc()
        nxt = soup.find("a", {"rel": "next"})
        if next:
            url = "https://www.edlal.org/" + nxt["href"]
        else:
            url = "#"


def combineJson():
    data = []
    for file in os.listdir("edlal"):
        with open(f"edlal/{file}", "r", encoding=encoding) as f:
            try:
                data.append(json.load(f))
            except:
                print(f"Error {file}")
                traceback.print_exc()
    with open("edlal.csv", "w", encoding=encoding,newline='') as f:
        c = csv.DictWriter(f, fieldnames=data[0].keys())
        c.writeheader()
        c.writerows(data)
    convert("edlal.csv")
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
