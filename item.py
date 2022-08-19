from typing import List
from loguru import logger
import soupsieve as sv
from bs4 import BeautifulSoup, Tag
import httpx
import json

with open("config.json", "r") as js:
    data = json.load(js)
    HEADERS = data.get("headers")
    MAX_RETRIES = data.get("max_retries")
   
class Item:
    def __init__(self, url: str) -> None:
        self.url = url
        self.soup: List[Tag] = []
        self.info: BeautifulSoup = ""
        self.articul: List[str] = []
        self.country: str = ""
        self.item_name: str = ""
        self.barcode: List[str] = []
        self.packaging: List[str] = []
        self.discount: List[str] = []
        self.price: List[str] = []
        self.discount_price: List[str] = []
        self.directory: str = ""
        self.pictures: List[str] = []


    @logger.catch
    def get_soup(self):
        self.soup: BeautifulSoup = self.souped(self.url)
        self.info: List[Tag] = sv.select('div:is(.catalog-element-right)',
                                         self.soup
                                         )
        return self.soup

    @logger.catch
    def get_item_name(self):
        self.item_name = self.info[0].h1.text

    @logger.catch
    def get_articul(self):
        articul: List[Tag] = sv.select('div:is(.catalog-element-articul)',
                                       self.info[0]
                                       )
        self.articul: List[str] = [tag.text.split(":")[1].strip()
                                   for tag in articul
                                   ]

    @logger.catch
    def get_country(self):
        country: List[Tag] = sv.select('div:is(.catalog-element-offer-left)',
                                       self.info[0]
                                       )
        self.country: str = country[0].p.text.split(":")[1]

    @logger.catch
    def get_barcode(self):
        barcode: List[Tag] = sv.select('div:is(.catalog-element-barcode)',
                                       self.info[0]
                                       )
        self.barcode: List[str] = [tag.span.text for tag in barcode]

    @logger.catch
    def get_packaging(self):
        fasovka = sv.select('td:is(.tg-yw4l22) > b', self.soup)
        for ind, val in enumerate(fasovka[6:]):
            if val.text == "Фасовка:":
                self.packaging.append(fasovka[6+ind+1].text)

    @logger.catch
    def get_discount(self):
        discount = sv.select('td:is(.tg-yw4l22) > \
                             span:not(.catalog-price)',
                             self.soup
                             )
        ln = len(discount)
        if ln > 2:
            mx = len(discount)//2
        else:
            mx = ln
        mx = len(discount)//2
        for val in discount[:mx]:
            self.discount.append(val.text)

    @logger.catch
    def get_price(self):
        price = sv.select('td:is(.tg-yw4l22) > s', self.soup)
        ln = len(price)
        if ln > 2:
            mx = len(price)//2
        else:
            mx = ln
        for ind, val in enumerate(price[:mx]):
            self.price.append(val.text)

    @logger.catch
    def get_disc_price(self):
        discount_price = sv.select('td:is(.tg-yw4l22) > \
                                   span:is(.catalog-price)',
                                   self.soup
                                   )
        ln = len(discount_price)
        if ln > 2:
            mx = len(discount_price)//2
        else:
            mx = ln
        for ind, val in enumerate(discount_price[:mx]):
            self.discount_price.append(val.text)

    @logger.catch
    def get_directory(self):
        ul = sv.select('ul:is(.breadcrumb-navigation)', self.soup)
        temp = [tag.text for tag in ul[0].find_all("li")]
        self.directory = " ".join(temp)

    @logger.catch
    def get_pictures(self):
        pictures = sv.select('div:is(.catalog-element-small-picture) > a',
                             self.soup)
        for i in pictures:
            self.pictures.append(i["href"])

    @logger.catch
    def get_info(self):
        self.get_soup()
        self.get_item_name()
        self.get_articul()
        self.get_country()
        self.get_barcode()
        self.get_packaging()
        self.get_discount()
        self.get_price()
        self.get_disc_price()
        self.get_directory()
        self.get_pictures()

    @logger.catch
    def full_info(self):
        if not self.price:
            return (self.price, self.discount_price, self.barcode,
                    self.articul, self.item_name, self.country,
                    self.packaging, self.discount, self.directory,
                    self.pictures, False
                    )
        else:
            return (self.price, self.discount_price, self.barcode,
                    self.articul, self.item_name, self.country,
                    self.packaging, self.discount, self.directory,
                    self.pictures
                    )
    
    @logger.catch
    def souped(self,url):
        count = 0
        while MAX_RETRIES > count:
            req = httpx.get(url, params=HEADERS)
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                return soup
            else:
                count+=1
                logger.error("BAD STATUS CODE")
            

