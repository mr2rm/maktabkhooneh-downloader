#!python

import os
import sys
from getopt import getopt

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import trange

CONTINUE = False


def download_course():
    course_path = os.path.join(os.getenv('base_dir'), os.getenv('course_name'))
    os.makedirs(course_path, exist_ok=True)

    response = requests.get(os.getenv('course_url'))
    soup = BeautifulSoup(response.content, 'html.parser')
    unit_elements = soup.find_all('a', attrs={'class': 'chapter__unit'})

    progress_bar_size = len(unit_elements)
    for i in trange(progress_bar_size, desc=os.getenv('course_name'), mininterval=0):
        filename = f'{i + 1:02d}.mp4'
        path = os.path.join(course_path, filename)

        if CONTINUE and os.path.isfile(path):
            continue

        print(f'### Downloading {filename} ###')
        unit_path = unit_elements[i]['href']
        response = requests.get(f"{os.getenv('base_url')}{unit_path}", headers={
            'Cookie': f"sessionid={os.getenv('session_id')};"
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        download_link = soup.find('div', attrs={'class': 'unit-content--download'}).find('a')['href']

        response = requests.get(download_link)
        with open(path, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    opts, argv = getopt(sys.argv[1:], 'r', ['resume'])
    for opt, arg in opts:
        if opt in ('-r', '--resume'):
            CONTINUE = True

    load_dotenv(verbose=True)
    download_course()
