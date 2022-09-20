import csv
import json
import os.path

import openpyxl
import requests

encoding = 'utf8'


def main():
    headers = {'Content-Type': 'application/json'}
    data = {
        "pageSize": 1000,
        "pageIndex": 0,
        "level": "All",
        "minRating": 0,
        "minHours": 0,
        "maxHours": 1000
    }
    response = requests.post('https://ethrai.sa/api/Commons/products/search',
                             headers=headers,
                             data=json.dumps(data))
    print(response.text)
    with open('ethrai.json', 'w') as f:
        json.dump(response.json(), f, indent=4)


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


def getCourseDetails():
    if not os.path.isdir("ethrai_courses"):
        os.mkdir("ethrai_courses")
    with open("ethrai.json", "r") as f:
        data = json.load(f)
    rows = []
    for course in data["courses"]:
        file = f"./ethrai_courses/{course['code']}.json"
        if os.path.isfile(file):
            print(f"{course['code']} already scraped.")
            with open(file, "r") as f:
                response = json.load(f)
        else:
            print(course["slug"])
            url = f"https://ethrai.sa/api/Courses/{course['slug']}"
            print(url)
            response = requests.get(url).json()
            with open(file, "w") as f:
                json.dump(response, f, indent=4)
        # print(json.dumps(response, indent=4))
        crs = response["course"]
        row = {
            "CourseEn": crs["nameEn"],
            "CourseAr": crs["nameAr"],
            "URL": f"https://ethrai.sa/courses/{course['slug']}",
            "Price": course["price"],
            "DetailsAr": crs["summaryAr"],
            "DetailsEn": crs["summaryEn"],
            # "Language": response["language"],
            "Platform": "ethrai",
            "Logo": crs["logo"],
            "Filter": " > ".join([cat["nameEn"] for cat in response["categories"]])
        }
        rows.append(row)
    with open("ethrai.csv", "w", newline='', encoding=encoding) as f:
        c = csv.DictWriter(f, fieldnames=rows[0].keys())
        c.writeheader()
        c.writerows(rows)
    convert("ethrai.csv")


if __name__ == '__main__':
    getCourseDetails()
