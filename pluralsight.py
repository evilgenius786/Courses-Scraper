import csv
import json
import os

import openpyxl
import requests

perPage = 100
total = 14087
api = 'https://api-us1.cludo.com/api/v3/10000847/10001278/search'


def fetchPage(page):
    file = f'pluralsight-pages/{page}.json'
    if os.path.isfile(file):
        print(f'[+] Skipping {page}')
        return
    print("[+] Fetching page", page)
    data = {"ResponseType": "json", "query": "*", "enableFacetFiltering": "true",
            "facets": {"categories": ["course", "labs"]}, "page": page, "perPage": perPage, "operator": "and"}
    headers = {
        'authorization': 'SiteKey MTAwMDA4NDc6MTAwMDEyNzg6U2VhcmNoS2V5',
        'Content-Type': 'application/json; charset=UTF-8',
    }
    response = requests.post(api, headers=headers, data=json.dumps(data))
    js = response.json()
    # print(json.dumps(js, indent=4))
    with open(file, 'w') as f:
        json.dump(js, f, indent=4)


encoding = 'utf8'


def processPages():
    rows = []
    for file in os.listdir('pluralsight-pages'):
        with open(f'pluralsight-pages/{file}', encoding=encoding) as f:
            js = json.load(f)
            if "TypedDocuments" not in js:
                continue
            for doc in js['TypedDocuments']:
                field = doc['Fields']
                data = {
                    "Course": field['Title']['Value'],
                    "URL": field['Url']['Value'],
                    # "Cost":"",
                    "Details": field['Description']['Value'],
                    "Language": "English",
                    "Platform": "PluralSight",
                    "Logo": field['Image']['Value'],
                    "Filter": "Home > Browse > Course",
                }
                print(json.dumps(data, indent=4))
                rows.append(data)
    with open('PluralSight.csv', 'w', encoding=encoding,newline='') as pfile:
        c = csv.DictWriter(pfile, fieldnames=rows[0].keys())
        c.writeheader()
        c.writerows(rows)
    convert('PluralSight.csv')


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


def main():
    logo()
    if not os.path.isdir('pluralsight-pages'):
        os.mkdir('pluralsight-pages')
    processPages()

    # for page in range(1, total // perPage + 2):
    #     fetchPage(page)


def logo():
    print(r"""
__________.__                      .__      _________.__       .__     __   
\______   \  |  __ ______________  |  |    /   _____/|__| ____ |  |___/  |_ 
 |     ___/  | |  |  \_  __ \__  \ |  |    \_____  \ |  |/ ___\|  |  \   __\
 |    |   |  |_|  |  /|  | \// __ \|  |__  /        \|  / /_/  >   Y  \  |  
 |____|   |____/____/ |__|  (____  /____/ /_______  /|__\___  /|___|  /__|  
                                 \/               \/   /_____/      \/      
=============================================================================
            PluralSight courses scraper by @evilgenius786
=============================================================================
[+] CSV/JSON Output
[+] Resumable
[+] API Based
_____________________________________________________________________________
""")


if __name__ == '__main__':
    main()
