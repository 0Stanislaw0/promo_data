import json
import time
import random
import os
from typing import List, Union, Dict
from datetime import datetime
from loguru import logger
from item import Item
from writer import WriterCSV
from crawler import Crawler


with open("config.json", "r") as js:
    data = json.load(js)
    CATEGORIES: List[str] = data.get("categories")
    RESTART_COUNT: int = data.get("restart").get("restart_count")
    INTERVAL_M: Union[int, float] = data.get("restart").get("interval_m")
    HEADERS: Dict[str, str] = data.get("headers")
    OUTPUT_DIRECTORY: str =  data.get("output_directory")
    MAX_RETRIES: int = data.get("max_retries")
    DELAY_RANGE_S: Dict[str, int] = data.get("delay_range_s")
    cwd = os.getcwd()
    targetPath = os.path.join(cwd, data.get("logs_dir"))
    while not os.path.exists(targetPath):
        os.mkdir(targetPath)
    targetFile = os.path.join(targetPath, "main.log")

logger.add(targetFile, format="{time} {level} {message}", level="DEBUG",
           rotation="100 Mb", compression="zip")


@logger.catch
def main():
    crawler = Crawler(HEADERS, MAX_RETRIES, DELAY_RANGE_S)
    writer_CSV = WriterCSV(OUTPUT_DIRECTORY)
    logger.debug("получаем категори ")
    crawler.get_categories()
    logger.debug("получаем подкатегории")
    crawler.get_subcategories()
    writer_CSV.prepare_csv_categories()
    for ind, key in enumerate(crawler.schema):
        writer_CSV.write_csv_categories((" ", key,
                                        crawler.URL+crawler.schema
                                        .get(key).get("href")))

    for ind, key in enumerate(crawler.schema):
        for link in crawler.schema.get(key).get("subcategories"):
            for k, v in link.items():
                writer_CSV.write_csv_categories((ind + 1, k, v))

    for key in CATEGORIES:
        """ получаем ссылки на товары, обходим товары и записываем в csv """
        value = crawler.schema.get(key, None)
        crawler.get_link_items(value.get("subcategories"))
        writer_CSV.prepare_csv_file(key)
        for links in crawler.product_links:
            for link in links:
                time.sleep(random.choice(crawler.RNG))
                if value.get("href") in link:
                    logger.debug(f"обрабатывается {key}, {link}")
                    item = Item(crawler.URL+link, HEADERS, MAX_RETRIES)
                    item.get_info()
                    for sub in value.get("subcategories"):
                        for category in sub.keys():
                            data = (datetime.now(),) + (category,) \
                                + (item.url,) + item.full_info()
                    writer_CSV.write_csv_file(key, data)


if "__main__" == __name__:
    count = 0
    while RESTART_COUNT > count:
        try:
            main()
            break
        except:
            time.sleep(INTERVAL_M*60)
            count += 1
