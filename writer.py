import csv
import os
import json
from loguru import logger


class WriterCSV:
    
    def __init__(self, directory: str) -> None:
        self.index: int = 1
        cwd = os.getcwd()
        targetPath = os.path.join(cwd, directory)
        self.targetPath = targetPath
        while not os.path.exists(targetPath):
            os.mkdir(targetPath)

    @logger.catch
    def prepare_csv_categories(self):
        logger.debug("создаем файл категории товаров")
        header = ("id", "parent_id", 'categoria', "url")
        targetFile = os.path.join(self.targetPath, 'categories.csv')
        with open(targetFile, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    @logger.catch
    def write_csv_categories(self, data):
        logger.debug("записываем в файл категории")
        targetFile = os.path.join(self.targetPath, 'categories.csv')
        with open(targetFile, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow((self.index,)+data)
            self.index += 1

    @logger.catch
    def prepare_csv_file(self, name: str):
        logger.debug(f"создаем файл категории {name}.csv")
        header = ("price_datetime", "sku_category", "sku_link",
                  "price", "price_promo", "sku_barcode",
                  "sku_article", "sku_name", "sku_country",
                  "sku_packaging", "directory", "sku_images",
                  "in_stock"
                  )
        targetFile = os.path.join(self.targetPath, f"{name}.csv")
        with open(targetFile, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    @logger.catch
    def write_csv_file(self, name, data):
        logger.debug(f"записываем в файл {name}.csv")
        targetFile = os.path.join(self.targetPath, f"{name}.csv")
        with open(targetFile, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(data)