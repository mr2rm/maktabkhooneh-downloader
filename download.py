#!python

import os
import sys
from getopt import getopt
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import trange, tqdm

BASE_URL = 'https://maktabkhooneh.org'

course_url = None
course_name = None
resume = False
untitled = False
fast = True


def is_valid_url(url):
    parsed_url = urlparse(url)
    validated_props = map(
        lambda p: bool(getattr(parsed_url, p)),
        ['scheme', 'netloc', 'path']
    )
    return all(validated_props)


def download_course():
    global course_url, course_name, resume

    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    unit_elements = soup.find_all('a', attrs={'class': 'chapter__unit'})
    if not course_name:
        course_name = soup.find('h1', attrs={'class': 'course-content__title'}).text

    course_path = os.path.join(os.getenv('base_dir'), course_name)
    os.makedirs(course_path, exist_ok=True)

    progress_bar = trange(len(unit_elements), mininterval=0)
    for i in progress_bar:
        this_unit = unit_elements[i]

        filename = f'{i + 1:02d}'
        progress_bar.set_description(f'Unit #{filename}')

        if not untitled:
            unit_title = this_unit['title']
            filename = f'{filename}. {unit_title}'
        filename = f'{filename}.mp4'

        path = os.path.join(course_path, filename)
        if resume and os.path.isfile(path):
            continue

        unit_path = this_unit['href']
        response = requests.get(f"{BASE_URL}{unit_path}", headers={
            'Cookie': f"sessionid={os.getenv('session_id')};"
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        # TODO: check if token is valid

        downloads = soup.find_all('div', attrs={'class': 'unit-content--download'})
        if not downloads:
            continue

        idx = int(fast and len(downloads) > 1)
        download_link = downloads[idx].find('a')['href']

        response = requests.get(download_link)
        with open(path, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], 'l:n:ruf', ['link=', 'name=', 'resume', 'untitled', 'fast'])
    for opt, arg in opts:
        if opt in ('-l', '--link'):
            course_url = arg
        elif opt in ('-n', '--name'):
            course_name = arg
        elif opt in ('-r', '--resume'):
            resume = True
        elif opt in ('-u', '--untitled'):
            untitled = True
        elif opt in ('-f', '--fast'):
            fast = False

    has_error = False
    if not course_url:
        print("LinkError: 'link' argument is not provided")
        has_error = True
    elif not is_valid_url(course_url):
        print("LinkError: 'link' argument is not valid")
        has_error = True

    if has_error:
        sys.exit(0)

    load_dotenv(verbose=True)
    download_course()
