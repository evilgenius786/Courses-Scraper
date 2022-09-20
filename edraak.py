import csv

import openpyxl
import requests


def main():
    data = requests.get('https://www.edraak.org/api/marketing/explore/').json()
    rows = []
    for category, courses in data['courses_by_category'].items():
        for course in courses:
            row = {
                "CourseEN": course['name_en'],
                "CourseAR": course['name_ar'],
                "URL": course['course_url'],
                # "Cost": data['data']['master_course_profile']['master_course_bar_info']['price'],
                "DetailsEN": course['description_en'],
                "DetailsAR": course['description_ar'],
                "Language": course['language'],
                "Platform": "Edraak",
                "Logo": course['cover_image'],
                "Filter": f"{category} > {course['name_en']}".title(),
            }
            rows.append(row)
    for course in data['specializations']:
        row = {
            "CourseEN": course['name_en'],
            "CourseAR": course['name_ar'],
            "URL": f"https://www.edraak.org/{course['lms_url']}",
            # "Cost": data['data']['master_course_profile']['master_course_bar_info']['price'],
            "DetailsEN": course['description_en'],
            "DetailsAR": course['description_ar'],
            "Language": course['language'],
            "Platform": "Edraak",
            "Logo": course['cover_image'],
            "Filter": f"Specialization > {course['name_en']}".title(),
        }
        rows.append(row)
    with open('edraak.csv', 'w',encoding=encoding,newline='') as f:
        c = csv.DictWriter(f, fieldnames=rows[0].keys())
        c.writeheader()
        c.writerows(rows)
    convert('edraak.csv')

encoding = 'utf-8'
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
