import os
import requests
from bs4 import BeautifulSoup

url = 'https://maktabkhooneh.org/course/%D8%B3%D8%A7%D8%AE%D8%AA%D9%85%D8%A7%D9%86-%D8%AF%D8%A7%D8%AF%D9%87-%D9%87%D8%A7-mk118/'
session_id = 'yn92x7lck1u5ire119t1u2rkpjy46vhr'
course_name = 'Data Structure'

base_dir = f'/home/rahmani/Downloads/{course_name}'
os.makedirs(base_dir, exist_ok=True)

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
unit_elements = soup.find_all('a', attrs={'class': 'chapter__unit'})

for i, unit in enumerate(unit_elements, start=1):
    filename = f'{i:02d}.mp4'
    print(f'### Downloading {filename} ###')

    unit_path = unit['href']
    response = requests.get(f'https://maktabkhooneh.org{unit_path}', headers={
        'Cookie': f'sessionid={session_id};'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    download_link = soup.find('div', attrs={'class': 'unit-content--download'}).find('a')['href']
    
    response = requests.get(download_link)

    path = os.path.join(base_dir, filename)
    with open(path, 'wb') as f:
        f.write(response.content)
