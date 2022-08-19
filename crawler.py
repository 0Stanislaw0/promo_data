from typing import List, Dict, Any
import soupsieve as sv
from bs4 import BeautifulSoup, Tag
import json
import time
import random
import os
import httpx
from loguru import logger


with open("config.json", "r") as js:
    data = json.load(js)
    DELAY_RANGE_S = data.get("delay_range_s")
    HEADERS = data.get("headers")
    MAX_RETRIES = data.get("max_retries")

class Crawler:
    def __init__(self) -> None:
        self.RNG = range(DELAY_RANGE_S.get("min"), 
                         DELAY_RANGE_S.get("max")
                         )

        self.URL = 'https://zootovary.ru'
        self.ids: List[Tag] = []
        self.soup: BeautifulSoup = None
        self.schema: Dict[str, Any] = {}
        self.product_links: List[List[str]] = []

    @logger.catch
    def get_categories(self):
        self.soup = self.souped(self.URL)
        self.ids = [tag for tag in self.soup.select('a[id]')]

    @logger.catch
    def add_to_schema(self, number: int, lst: List[str]) -> None:
        self.schema[self.ids[number].string] = {"href": self.ids[number]
                                                .get('href'),
                                                "subcategories": lst
                                                }

    @logger.catch
    def get_subcategories(self):
        cols = [tag for tag in self.soup.select('ul.catalog-cols')]
        temp = []
        count = 0
        for categoria in cols:
            li = [tag for tag in categoria.select('li>ul')]
            for i in li:
                for a in i.find_all("li"):
                    temp.append({a.a.text: a.a["href"]})
            self.add_to_schema(count, temp)
            count += 1
            temp = []

    
    def get_max_page(self, subcategoria):
        soup = self.souped(subcategoria+"?pc=60")
        a = sv.select('div:is(.navigation)', soup)
        try:
            max_page = a[0].find_all('a')[-1].text
        except IndexError:
            return 1
        try:
            max_page = int(max_page)
        except ValueError:
            max_page = a[0].find_all('a')[-1]["href"].split("=")[-1]
        return max_page

    @logger.catch
    def get_link_items(self, subcategories) -> None:
        for sub in subcategories:
            temp = []
            for k, v in sub.items():
                time.sleep(random.choice(self.RNG))
                max_page = self.get_max_page(self.URL+v)
                for number in range(1, int(max_page)+1):
                    time.sleep(random.choice(self.RNG))
                    logger.debug("get link items, page ", number)
                    soup = self.souped(self.URL+v+"?pc=60"+f"&PAGEN_1={number}")
                    a = sv.select('a:is(.name)', soup)[:60]
                    for i in a:
                        temp.append(i["href"])
            self.product_links.append(temp)

    def souped(self, url):
        count = 0
        while MAX_RETRIES > count:
            req = httpx.get(url, params=HEADERS)
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                return soup
            else:
                count+=1
                logger.error("BAD STATUS CODE")
            
            

