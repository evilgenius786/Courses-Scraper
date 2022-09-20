import csv
import json
import os.path
import threading
import time
import traceback

import openpyxl
import requests

api = "https://api.mnar.sa/api"
semaphore = threading.Semaphore(10)
encoding = 'utf8'


def fetchCourse(course):
    file = f"./mnar/{course['nid']}.json"
    if os.path.isfile(file):
        print(f"[!] {course['nid']} already exists")
        with open(file, encoding=encoding) as f:
            return json.load(f)
    with semaphore:
        try:
            print("Fetching", course['nid'])
            res = requests.get(f'{api}/master-course/{course["nid"]}')
            details = res.json()
            print(json.dumps(details, indent=4, ensure_ascii=False))
            with open(file, "w", encoding=encoding) as f:
                json.dump(details, f, ensure_ascii=False)
            return details
        except:
            traceback.print_exc()


def main():
    logo()
    if not os.path.isdir("mnar"):
        os.mkdir("mnar")
    # threads = []
    # courses = requests.get(f'{api}/courses-search-adv?page=1&items_per_page=256').json()['data']['other']['items']
    # for course in courses:
    #     print(f"Courses count: {len(courses)}")
    #     threads.append(threading.Thread(target=fetchCourse, args=(course,)))
    #     threads[-1].start()
    # for thread in threads:
    #     thread.join()
    processJson()


def processJson():
    rows = []
    for file in os.listdir("mnar"):
        with open(f"mnar/{file}", encoding=encoding) as f:
            data = json.load(f)
            row = {
                "Course": data['data']['master_course_profile']['master_course_title'],
                "URL": "https://mnar.sa/course/" + data['data']['master_course_profile']['master_course_ID'],
                "Cost": data['data']['master_course_profile']['master_course_bar_info']['price'],
                "Details": data['data']['master_course_profile']['master_course_description'],
                "Language": data['data']['master_course_profile']['master_course_bar_info']['learning_language'],
                "Platform": "mnar.sa",
                "Logo": data['data']['master_course_profile']['master_course_training_center']['training_center_logo'],
                # "Filter": data['data']['master_course_profile']['master_course_bar_info']['filter'],
            }
            rows.append(row)
    with open("mnar.csv", "w", encoding=encoding, newline='') as f:
        cf = csv.DictWriter(f, fieldnames=rows[0].keys())
        cf.writeheader()
        cf.writerows(rows)
    convert("mnar.csv")


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


def logo():
    print(r"""
       __  ___ _  __ ___    ___      ____ ___ 
      /  |/  // |/ // _ |  / _ \    / __// _ |
     / /|_/ //    // __ | / , _/_  _\ \ / __ |
    /_/  /_//_/|_//_/ |_|/_/|_|(_)/___//_/ |_|
===================================================
    mnar.sa scraper by github.com/evilgenius786
===================================================
[+] Multithreaded
[+] API based
[+] CSV/JSON response
[+] Without browser
___________________________________________________
                                              
""")


if __name__ == '__main__':
    main()
