import cgi
import os
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

###############################
# import argparse

# parser = argparse.ArgumentParser(description='Download resources from VG sites')
# # Required positional argument

# parser.add_argument('site', type=str,
#                     help='spriteresources / modelresources / textureresources')

# parser.add_argument('mode', type=str,
#                     help='console / game / letter')

# # Optional positional argument
# parser.add_argument('opt_pos_arg', type=int, nargs='?',
#                     help='An optional integer positional argument')

# # Optional argument
# parser.add_argument('--opt_arg', type=int,
#                     help='An optional integer argument')

# # Switch
# parser.add_argument('--switch', action='store_true',
#                     help='A boolean switch')

# args = parser.parse_args()
###############################


def scrape_console(base_url, console_url):
    url = urljoin(base_url, console_url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    letters = soup.find('div', {'id': 'letters'})
    letters_links = letters.find_all('a')
    proper_divs = []
    print(f"Getting game links for {console_url}")
    for link in tqdm(letters_links):
        page_r = requests.get(urljoin(base_url, link.get('href')))
        page_soup = BeautifulSoup(page_r.text, "html.parser")
        content = page_soup.find('div', {'id': 'content'})
        content_div = content.find_all('div')
        for div in content_div:
            if 'id' not in div.attrs:  # Every other div has some id except for game ones
                if div.find_all('a'):
                    game_divs = div.find_all('a')
                    for game_div in game_divs:
                        proper_divs.append(game_div.get('href'))

    paths = []
    for div in proper_divs:
        paths.append(div.split('/')[-2])
    print(f"Found {len(paths)} games.")

    filename = f"{console_url}.txt"
    f = open(filename, "w")
    f.write(f"{base_url}\n")
    f.write(f"{console_url}/\n")
    for path in paths:
        f.write(f"{path}/\n")
    f.close()

    scrape_game(filename)


def scrape_game(urls_file):
    paths = []
    with open(urls_file) as file:
        for line in file:
            paths.append(line.rstrip())

    BASE_URL = paths.pop(0)
    CONSOLE = paths.pop(0)
    SINGLE = False

    print(f"Scraping {len(paths)} games...")
    for j, path in enumerate(paths):
        console = CONSOLE
        print(f"\n--- Processing [{j+1}/{len(paths)}] {path} ---")
        url = urljoin(BASE_URL, console)
        url = urljoin(url, path)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        titles = []
        sections = soup.find_all('div', {'class': 'sect-name'})
        for section in sections:
            titles.append(section['title'])

        sheets = soup.find_all("div", class_="updatesheeticons")

        sheet_dict = {}

        sheet_counter = 0
        for sheet in sheets:
            links = sheet.find_all('a')
            title = titles.pop(0)
            sheet_dict[title] = []
            for link in links:
                sheet_dict[title].append((BASE_URL + link.get('href')))
                sheet_counter += 1

        print(
            f"Found {len(sheets)} categories and {sheet_counter} sprite sheets. Getting download links...")
        if sheet_counter == 1:
            SINGLE = True

        download_dict = {}
        for sheet_name, sheet_pages in tqdm(sheet_dict.items(), colour='#00f0ff'):
            download_dict[sheet_name] = []
            for sheet_page in sheet_pages:
                sheet_r = requests.get(sheet_page)
                sheet_soup = BeautifulSoup(sheet_r.content, "html.parser")
                download_link = sheet_soup.find("tr", class_="rowfooter")
                href_link = download_link.find('a').get('href')
                dlink = urljoin(BASE_URL, href_link)
                download_dict[sheet_name].append(dlink.strip())

        print("Downloading...")
        for name, dlinks in tqdm(download_dict.items(), colour='#02ff20'):
            for dl in dlinks:
                remotefile = urlopen(dl)
                blah = remotefile.info()['Content-Disposition']
                value, params = cgi.parse_header(blah)
                filename = params["filename"]
                if SINGLE:
                    Path(os.path.join("single", console)).mkdir(
                        parents=True, exist_ok=True)
                    fullpath = os.path.join("single", console, filename)
                else:
                    Path(os.path.join(console, path, name)).mkdir(
                        parents=True, exist_ok=True)
                    fullpath = os.path.join(console, path, name, filename)
                urlretrieve(dl, fullpath)

    print("Finished\n")


def main():
    scrape_game("custom_edited.txt")


if __name__ == main():
    main()
