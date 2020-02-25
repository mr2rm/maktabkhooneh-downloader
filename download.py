#!python

import os
import sys
from getopt import getopt

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import trange

BASE_URL = 'https://maktabkhooneh.org'

course_url = None
course_name = None
resume = False


def download_course():
    global course_url, course_name, resume

    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    unit_elements = soup.find_all('a', attrs={'class': 'chapter__unit'})
    if not course_name:
        course_name = soup.find('h1', attrs={'class': 'course-content__title'}).text

    course_path = os.path.join(os.getenv('base_dir'), course_name)
    os.makedirs(course_path, exist_ok=True)

    progress_bar_size = len(unit_elements)
    for i in trange(progress_bar_size, desc=course_name, mininterval=0):
        filename = f'{i + 1:02d}.mp4'
        path = os.path.join(course_path, filename)

        if resume and os.path.isfile(path):
            continue

        print(f'### Downloading {filename} ###')
        unit_path = unit_elements[i]['href']
        response = requests.get(f"{BASE_URL}{unit_path}", headers={
            'Cookie': f"sessionid={os.getenv('session_id')};"
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        download_link = soup.find('div', attrs={'class': 'unit-content--download'}).find('a')['href']

        response = requests.get(download_link)
        with open(path, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], 'l:n:r', ['link=', 'name=', 'resume'])
    for opt, arg in opts:
        if opt in ('-l', '--link'):
            course_url = arg
        elif opt in ('-n', '--name'):
            course_name = arg
        elif opt in ('-r', '--resume'):
            resume = True

    load_dotenv(verbose=True)
    download_course()
