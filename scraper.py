import cgi
import os
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

paths = []
with open("urls.txt") as file:
    for line in file:
        paths.append(line.rstrip())

BASE_URL = paths.pop(0)
CONSOLE = paths.pop(0)
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

    for sheet in sheets:
        links = sheet.find_all('a')
        title = titles.pop(0)
        sheet_dict[title] = []
        for link in links:
            sheet_dict[title].append((BASE_URL + link.get('href')))

    print(f"Found {len(sheets)} categories. Getting download links...")
    #print(f"Found {len(list(sheet_dict.values())[0])} sprite sheets.")
    if len(sheet_dict) == 1:
        if len(list(sheet_dict.values())[0]):
            console = "single"

    download_dict = {}
    #print(f"Found {len(sheet_dict.items())} sprite sheets\n")
    for sheet_name, sheet_pages in tqdm(sheet_dict.items()):
        download_dict[sheet_name] = []
        for sheet_page in sheet_pages:
            sheet_r = requests.get(sheet_page)
            sheet_soup = BeautifulSoup(sheet_r.content, "html.parser")
            download_link = sheet_soup.find("tr", class_="rowfooter")
            href_link = download_link.find('a').get('href')
            dlink = urljoin(BASE_URL, href_link)
            download_dict[sheet_name].append(dlink.strip())

    #print(f"Found {len(download_links)} sprite-sheets\nDownloading...")
    print("Downloading...")
    for name, dlinks in tqdm(download_dict.items()):
        for dl in dlinks:
            remotefile = urlopen(dl)
            blah = remotefile.info()['Content-Disposition']
            value, params = cgi.parse_header(blah)
            filename = params["filename"]
            if console == "single":
                Path(os.path.join(console)).mkdir(
                parents=True, exist_ok=True)
                fullpath = os.path.join(console, filename)
            else:
                Path(os.path.join(console, path, name)).mkdir(
                    parents=True, exist_ok=True)
                fullpath = os.path.join(console, path, name, filename)
            urlretrieve(dl, fullpath)

print("Finished\n")
