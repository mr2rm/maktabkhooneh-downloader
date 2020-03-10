#!python

import os
import sys
from getopt import getopt
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import trange

BASE_URL = 'https://maktabkhooneh.org'


class ArgumentParser:
    short_options = 'l:n:ruf'
    long_options = ['link=', 'name=', 'resume', 'untitled', 'fast']
    error_messages = {
        'UnsetLinkError': "'link' argument is not provided",
        'InvalidLinkError': "'link' argument is not valid",
        'InvalidTokenError': "'session_id' is not valid",
    }

    def __init__(self, args):
        self.args = args
        self.error = None
        self.course_url = None
        self.course_name = None
        self.resume = False
        self.untitled = False
        self.fast = False

    @staticmethod
    def is_valid_url(url):
        parsed_url = urlparse(url)
        validated_props = map(
            lambda p: bool(getattr(parsed_url, p)),
            ['scheme', 'netloc', 'path']
        )
        return all(validated_props)

    def get_error(self, err_key):
        if err_key not in self.error_messages:
            return 'Oops!'
        return f'{err_key}: {self.error_messages[err_key]}'

    def validate_course_url(self):
        if not self.course_url:
            return 'UnsetLinkError'
        if not self.is_valid_url(self.course_url):
            return 'InvalidLinkError'

    def parse(self):
        opts, args = getopt(self.args, self.short_options, self.long_options)
        for opt, arg in opts:
            if opt in ('-l', '--link'):
                self.course_url = arg
            elif opt in ('-n', '--name'):
                self.course_name = arg
            elif opt in ('-r', '--resume'):
                self.resume = True
            elif opt in ('-u', '--untitled'):
                self.untitled = True
            elif opt in ('-f', '--fast'):
                self.fast = False

    def is_valid(self):
        self.error = self.validate_course_url()
        return not bool(self.error)

    @staticmethod
    def raise_error(message):
        print(message)
        sys.exit(1)


def download_course(args):
    response = requests.get(args.course_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    units = soup.find_all('a', attrs={'class': 'chapter__unit'})

    course_name = args.course_name or soup.find('h1', attrs={'class': 'course-content__title'}).text
    course_path = os.path.join(os.getenv('base_dir'), course_name)
    os.makedirs(course_path, exist_ok=True)

    progress_bar = trange(len(units), mininterval=0)
    for i in progress_bar:
        this_unit = units[i]

        filename = f'{i + 1:02d}'
        progress_bar.set_description(f'Unit #{filename}')

        if not args.untitled:
            unit_title = this_unit['title']
            filename = f'{filename}. {unit_title}'
        filename = f'{filename}.mp4'

        path = os.path.join(course_path, filename)
        if args.resume and os.path.isfile(path):
            continue

        unit_path = this_unit['href']
        response = requests.get(f"{BASE_URL}{unit_path}", headers={
            'Cookie': f"sessionid={os.getenv('session_id')};"
        })
        soup = BeautifulSoup(response.content, 'html.parser')

        downloads = soup.find_all('div', attrs={'class': 'unit-content--download'})
        if not downloads:
            continue

        idx = int(args.fast and len(downloads) > 1)
        download_link = downloads[idx].find('a')
        if not download_link:
            return 'InvalidTokenError'

        response = requests.get(download_link['href'])
        with open(path, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    args = ArgumentParser(args=sys.argv[1:])
    args.parse()

    if not args.is_valid():
        args.raise_error(args.error)

    load_dotenv(verbose=True)
    error_code = download_course(args)
    if error_code:
        error = args.get_error(error_code)
        args.raise_error(error)
