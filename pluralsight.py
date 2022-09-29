import json
import os

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


def main():
    logo()
    if not os.path.isdir('pluralsight-pages'):
        os.mkdir('pluralsight-pages')
    for page in range(1, total // perPage + 2):
        fetchPage(page)


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
