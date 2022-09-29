import csv
import json

import openpyxl
import requests

name = "Udacity"
encoding = "utf-8"


def main():
    url = "https://www.udacity.com/data/catalog.json"
    js = requests.get(url).json()
    rows = []
    for course in js:
        if course['type'] != 'course':
            continue
        data = {
            "Course": course['payload']['title'],
            "URL": f"https://www.udacity.com{course['url']}",
            # "Cost":"",
            "Details": course['payload'].get('shortSummary', ""),
            # "Language": soup.find('title', string="Available languages").text,
            "Platform": "Udacity",
            "Logo": course['payload'].get('imageUrl', ""),
            "Filter": course['payload']['school'].replace("School of ", "").strip()
        }
        print(json.dumps(data, indent=4, ensure_ascii=False))
        rows.append(data)
    with open(f"{name}.json", "w") as f:
        f.write(json.dumps(rows, indent=4))
    combineJson(rows)


def combineJson(data):

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


if __name__ == '__main__':
    main()
