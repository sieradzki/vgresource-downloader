import argparse
import cgi
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def scrape_console(base_url, console_url):
    url = urljoin(base_url, console_url)
    r = requests.get(url)
    if r.status_code != 200:
        print(
            f"Error connecting to {url}. Check link validity or your internet connection.")
        return
    soup = BeautifulSoup(r.text, "html.parser")
    letters = soup.find('div', {'id': 'letters'})
    letters_links = letters.find_all('a')
    proper_divs = []
    print(f"Getting game links for {console_url}")
    for link in tqdm(letters_links):
        page_url = urljoin(base_url, link.get('href'))
        page_r = requests.get(page_url)
        if page_r.status_code != 200:
            print(
                f"Error connecting to {page_url}. Check link validity or your internet connection.")
            return
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
    f.write(f"{console_url}/\n")
    for path in paths:
        f.write(f"{path}/\n")
    f.close()

    scrape_game(base_url, filename)


def scrape_game(base_url, urls_file):
    paths = []
    with open(urls_file) as file:
        for line in file:
            paths.append(line.rstrip())

    CONSOLE = paths.pop(0)

    save_filename = f"{CONSOLE.split('/')[0]}_done.txt"
    last = 0
    if os.path.isfile(save_filename):
        print("Found save file")
        f = open(save_filename, "r")
        last = int(f.readline())
        last += 1
        f.close()
        print(f"Continuing from {last}: {paths[last]}")

    print(f"Scraping {len(paths)-last} games...")
    for j, path in enumerate((pbar := tqdm(paths[last:], unit='game', colour='#253fff'))):
        pbar.set_description(f"{path}")

        SINGLE = False
        console = CONSOLE
        url = urljoin(base_url, console)
        url = urljoin(url, path)
        r = requests.get(url)
        if r.status_code != 200:
            print(
                f"Error connecting to {url}. Check link validity or your internet connection.")
            return
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
                sheet_dict[title].append((base_url + link.get('href')))
                sheet_counter += 1

        # print(
        #     f"Found {len(sheets)} categories and {sheet_counter} sprite sheets. Getting download links...")
        if sheet_counter == 1:
            SINGLE = True

        download_dict = {}
        for sheet_name, sheet_pages in sheet_dict.items():
            download_dict[sheet_name] = []
            for sheet_page in sheet_pages:
                sheet_r = requests.get(sheet_page)
                if sheet_r.status_code != 200:
                    print(
                        f"Error connecting to {sheet_page}. Check link validity or your internet connection.")
                    return
                sheet_soup = BeautifulSoup(sheet_r.content, "html.parser")
                download_link = sheet_soup.find("tr", class_="rowfooter")
                href_link = download_link.find('a').get('href')
                dlink = urljoin(base_url, href_link)
                download_dict[sheet_name].append(dlink.strip())

        # print("Downloading...")
        for name, dlinks in download_dict.items():
            for dl in dlinks:
                try:
                    remotefile = urlopen(dl)
                except HTTPError as e:
                    # do something
                    print('Error code: ', e.code)
                except URLError as e:
                    # do something (set req to blank)
                    print('Reason: ', e.reason)
                content = remotefile.info()['Content-Disposition']
                _, params = cgi.parse_header(content)
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

        f = open(save_filename, "w")
        f.write(f"{j+last}")
        f.close()

    print("Finished\n")


def main():
    parser = argparse.ArgumentParser(
        description='Download resources from VG sites\n Example usage: python scraper.py 1 console --console=mobile', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('site', type=int,
                        help='sprites-resource: 1\nmodel-resource: 2\ntexture-resource: 3\nsound-resource: 4')

    parser.add_argument('mode', type=str,
                        help='console / game')  # / genre

    parser.add_argument('--urls', type=str,
                        help='Path to file containing urls. Use with mode=game.')
    parser.add_argument('--console', type=str,
                        help='Console name. Use with mode=console.')

    # parser.add_argument('--genre', type=str,
    #                     help='Genre name. Use with mode=console.') # Should be simple to implement. Just add genre/ to base url

    # parser.add_argument('--single', type=bool,
    #                     help='Save single files in "single/" directory to avoid creating many unnecessary folders.')
    # parser.add_argument('--ignore-categories', type=str,
    #                     help='Ignore specified categories. Separate categories with ",".')
    args = parser.parse_args()

    site = args.site
    if site == 1:
        base_url = "https://www.spriters-resource.com/"
    elif site == 2:
        base_url = "https://www.models-resource.com/"
    elif site == 3:
        base_url = "https://www.textures-resource.com/"
    elif site == 4:
        base_url = "https://www.sounds-resource.com/"
    else:
        print(
            f"Bad argument: site. Provided value: {site}. Excpected: 1 / 2 / 3 / 4")
        return
    mode = args.mode

    if mode == 'console':
        if args.console:
            console = args.console
        else:
            print("Missing argument: console.")
            return
        scrape_console(base_url, console)
    elif mode == 'game':
        if args.urls:
            urls = args.urls
        else:
            print("Missing argument: urls.")
            return
        if os.path.isfile(urls):
            scrape_game(base_url, urls)
        else:
            print(f"File {urls} doesn't exist.")
    else:
        print(
            f"Bad argument: mode. Provided value: {mode}. Excpected: console / game")


if __name__ == main():
    main()
