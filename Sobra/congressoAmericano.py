import keyword
from bs4 import BeautifulSoup

import requests

url = 'https://www.house.gov/representatives'
text = requests.get(url).text
soup = BeautifulSoup(text, 'html5lib')

all_urls = [a['href'] for a in soup('a') if a.has_attr('href')]

print(len(all_urls))

import re 

regex = r'^https?://.*\.house\.gov.?$'

assert re.match(regex, 'http://joel.house.gov')
assert re.match(regex, 'https://joel.house.gov/')
assert not re.match(regex, 'http://joel.house..com')
assert not re.match(regex, 'http://joel.house.gov/biography')

good_urls = [url for url in all_urls if re.match(regex, url)]
good_urls = list(set(good_urls))
print(len(good_urls))

from typing import Dict, Set

press_releases: Dict[str, Set[str]] = {}

for house_url in good_urls:
    html = requests.get(house_url).text
    soup = BeautifulSoup(html, 'html5lib')
    pr_links = [a['href'] for a in soup('a') if a.has_attr('href') and 'press-release' in a['href']]
    # print(f"{house_url} has {len(pr_links)}") 
    press_releases[house_url] = pr_links

def paragraph_mentions(text: str, word: str) -> bool:
    soup = BeautifulSoup(text, 'html5lib')
    paragraphs = [p.get_text() for p in soup('p')]
                  
    return any(word.lower() in p.lower() for p in paragraphs)

for house_url, pr_links in press_releases.items():
    for pr_link in pr_links:
        try:
            html = requests.get(pr_link).text
        except requests.RequestException:
            continue

        if paragraph_mentions(html, 'data'):
            print(f"Encontrado em: {house_url}")
            break