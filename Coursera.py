import csv
import json
import os.path
import threading
import time
import traceback

import openpyxl
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

timeout = 10
debug = True
headless = False
images = False
maximize = False
incognito = False
ce = "https://www.coursera.org"

semaphore = threading.Semaphore(10)


def scrapeCourseera(u, logo_):
    file = f"coursera/{u.replace('/', '_')[1:]}.json"
    url = f"{ce}{u}"
    if os.path.isfile(file):
        print(f"Already scraped {url}")
        return
    with semaphore:
        try:
            print(f"Working on {url}")
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            data = {
                "Course": soup.find('h1').text,
                "URL": url,
                # "Cost":"",
                "Details": soup.find('div', class_="description").text,
                "Language": soup.find('title', string="Available languages").text,
                "Platform": "Coursera",
                "Logo": logo_,
                "Filter": " > ".join([x.text.strip() for x in soup.find("div", {"aria-label": "breadcrumbs"})])
            }
            print(json.dumps(data, indent=4, ensure_ascii=False))
            with open(file, "w") as f:
                f.write(json.dumps(data, indent=4))
            return data
        except:
            print(f"Error {url}")
            with open("error.txt", "a") as f:
                f.write(f"{url}\n")


def main():
    logo()
    # combineJson()
    # convert("coursera.csv")
    # return
    driver = getChromeDriver()
    if not os.path.isdir("coursera"):
        os.mkdir("coursera")
    threads = []
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            current = getElement(driver, '//button[@class="box number current"]')
            print(f"Working on {current.text}")
            getElement(driver, '//div[@class="ais-InfiniteHits"]')
            courses = soup.find('div', {"class": "ais-InfiniteHits"}).find('ul').find_all("li")
            for course in courses:
                t = threading.Thread(target=scrapeCourseera,
                                     args=(course.find('a').get('href'), course.find('img').get('src'),))
                t.start()
                threads.append(t)
            nxt = getElement(driver, "//button[@aria-label='Next Page']")
            if nxt.get_attribute("disabled"):
                print("All done...")
                break
            click(driver, "//button[@aria-label='Next Page']")
            time.sleep(1)
        except:
            traceback.print_exc()
    print("Waiting for threads...")
    for t in threads:
        t.join()
    print("Done")


encoding = "utf-8"


def combineJson():
    data = []
    for file in os.listdir("coursera"):
        with open(f"coursera/{file}", "r", encoding=encoding) as f:
            data.append(json.loads(f.read()))
    with open("coursera.csv", "w", encoding=encoding,newline='') as f:
        c = csv.DictWriter(f, data[0].keys())
        c.writeheader()
        c.writerows(data)


def convert(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(filename, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ws.append(row)
    wb.save(filename.replace("csv", "xlsx"))


def logo():
    print(r"""
       ____                                _____             
      / ___| ___   _   _  _ __  ___   ___ | ____| _ __  __ _ 
     | |    / _ \ | | | || '__|/ __| / _ \|  _|  | '__|/ _` |
     | |___| (_) || |_| || |   \__ \|  __/| |___ | |  | (_| |
      \____|\___/  \__,_||_|   |___/ \___||_____||_|   \__,_|
==================================================================
        Courseera Scraper by @evilgenius786
==================================================================
[+] Resumable
[+] Hybrid approach
__________________________________________________________________
""")


def click(driver, xpath):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def getElement(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))


def getChromeDriver(proxy=None):
    options = webdriver.ChromeOptions()
    if debug:
        # print("Connecting existing Chrome for debugging...")
        options.debugger_address = "127.0.0.1:9222"
    else:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--user-data-dir=C:/Selenium1/ChromeProfile')
    if not images:
        # print("Turning off images to save bandwidth")
        options.add_argument("--blink-settings=imagesEnabled=false")
    if headless:
        # print("Going headless")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    if maximize:
        # print("Maximizing Chrome ")
        options.add_argument("--start-maximized")
    if proxy:
        # print(f"Adding proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")
    if incognito:
        # print("Going incognito")
        options.add_argument("--incognito")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


if __name__ == '__main__':
    main()
