import csv
import os.path
import sys
import threading

import openpyxl
import requests
import json

from bs4 import BeautifulSoup

api = "https://www.skillshare.com/api/graphql"
headers = {'content-type': 'application/json'}
ps = 5000
name = "SkillShare"
encoding = "utf-8"
thread_count = 10
semaphore = threading.Semaphore(thread_count)


def processCourse(course):
    url = course['url']
    file = f'{name}-courses/{url.split("/")[-1]}.json'
    if os.path.isfile(file):
        print(f'Already scraped {url}')
        return
    with semaphore:
        print(f"Working on {url}")
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        # print(soup)
        # js = json.loads(soup.find('script', type='application/ld+json').text)
        # print(json.dumps(js, indent=4))
        data = {
            # "Course": soup.find('span',{'class':"title"}).text.strip(),
            "Course": course['title'],
            "URL": url,
            # "Cost":"",
            "Details": soup.find('div', {"class": "description-column"}).text.strip(),
            # "Language": soup.find('title', string="Available languages").text,
            "Platform": "SkillShare",
            # "Logo": js['image'],
            "Logo": course['largeCoverUrl'],
            # "Filter": " > ".join([x.text.strip() for x in soup.find("div", {"aria-label": "breadcrumbs"})])
        }
        print(json.dumps(data, indent=4))
        with open(file, 'w') as outfile:
            json.dump(data, outfile, indent=4)


def processCourses():
    threads = []
    for file in os.listdir(f'{name}'):
        if file.startswith('courses-') and file.endswith('.json'):
            with open(f'{name}/{file}') as json_file:
                data = json.load(json_file)
                for course in data['data']['classListByType']['nodes']:
                    threads.append(threading.Thread(target=processCourse, args=(course,)))
                    threads[-1].start()
    for thread in threads:
        thread.join()


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


def main():
    logo()
    for d in [f'{name}', f'{name}-courses']:
        if not os.path.isdir(d):
            os.mkdir(d)
    combineJson()
    # for i in range(40440 // ps + 1):
    #     getCourses(i)
    # processCourses()


def getCursor(pageSize):
    payload = json.dumps({
        "operationName": "GetClassesPageInfo",
        "variables": {
            "type": "TRENDING_CLASSES",
            "filter": {
                "subCategory": "",
                "classLength": []
            },
            "pageSize": pageSize,
            "sortAttribute": "SIX_MONTHS_ENGAGEMENT"
        },
        "query": "query GetClassesPageInfo($filter: ClassFilters!, $pageSize: Int, $type: ClassListType!, "
                 "$sortAttribute: ClassListByTypeSortAttribute) {\n  classListByType(type: $type, where: $filter, "
                 "first: $pageSize, sortAttribute: $sortAttribute) {\n    pageInfo {\n      endCursor\n      "
                 "__typename\n    }\n    __typename\n  }\n}\n "
    })
    response = requests.request("POST", api, data=payload, headers=headers)
    print(response.text.strip())
    return response.json()['data']['classListByType']['pageInfo']['endCursor']


def getCourses(i):
    file = f'{name}/courses-{i}.json'
    if os.path.isfile(file):
        print(f'File {file} already exists')
        return
    print(f'Getting courses {i * ps}')
    payload = json.dumps({
        "operationName": "GetClassesByType",
        "variables": {
            "type": "TRENDING_CLASSES",
            "filter": {
                "subCategory": "",
                "classLength": []
            },
            "pageSize": ps,
            "cursor": getCursor(i * ps),
            "sortAttribute": "SIX_MONTHS_ENGAGEMENT"
        },
        "query": "query GetClassesByType($filter: ClassFilters!, $pageSize: Int, $cursor: String, "
                 "$type: ClassListType!, $sortAttribute: ClassListByTypeSortAttribute) {\n  classListByType(type: "
                 "$type, where: $filter, first: $pageSize, after: $cursor, sortAttribute: $sortAttribute) {\n    "
                 "totalCount\n    nodes {\n      id\n      title\n      url\n      sku\n      largeCoverUrl\n      "
                 "studentCount\n      durationInSeconds\n      teacher {\n        id\n        name\n        "
                 "username\n        headline\n        vanityUsername\n        smallPictureUrl\n        __typename\n   "
                 "   }\n      badges {\n        type\n        __typename\n      }\n      viewer {\n        "
                 "hasSavedClass\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n "
    })
    response = requests.request("POST", api, data=payload, headers=headers)
    # print(json.dumps(response.json(), indent=4))
    print(f'Writing courses {i * ps}')
    with open(file, 'w') as outfile:
        json.dump(response.json(), outfile, indent=4)


def logo():
    print(r"""
      ___________   .__.__  .__    _________.__                          
     /   _____/  | _|__|  | |  |  /   _____/|  |__ _____ _______   ____  
     \_____  \|  |/ /  |  | |  |  \_____  \ |  |  \\__  \\_  __ \_/ __ \ 
     /        \    <|  |  |_|  |__/        \|   Y  \/ __ \|  | \/\  ___/ 
    /_______  /__|_ \__|____/____/_______  /|___|  (____  /__|    \___  >
            \/     \/                    \/      \/     \/            \/ 
==============================================================================
                SkillShare Course scraper by @evilgenius786
==============================================================================
[+] Scrapes all courses from SkillShare
[+] CSV/JSON Output
[+] No API Key Required
[+] Without browser
______________________________________________________________________________
""")


if __name__ == "__main__":
    main()
