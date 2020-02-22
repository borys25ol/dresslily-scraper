# -*- coding: utf-8 -*-
import pathlib

from scrapy import signals
from scrapy.exporters import CsvItemExporter

from crawl.items import ProductItem, ReviewItem


class CsvPipeline(object):
    """Custom CSV pipeline.
    Push all items to 'products.csv' if item from OlxItem
    Push all items to 'reviews.csv' if item from UserItem
    """
    def __init__(self):
        self.product_fields_to_export = [
            'product_id', 'product_url', 'name', 'discount', 'discounted_price', 'original_price', 'rating',
            'product_info'
        ]
        self.review_fields_to_export = [
            'product_id', 'rating', 'timestamp', 'text', 'size', 'color'
        ]
        self.product_file_name = pathlib.Path(__file__).parent / 'results'/ 'products.csv'
        self.reviews_file_name = pathlib.Path(__file__).parent / 'results'/ 'reviews.csv'
        self.delimiter = ','

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.product_file = open(self.product_file_name, 'w+b')
        self.review_file = open(self.reviews_file_name, 'w+b')
        self.product_exporter = CsvItemExporter(
            self.product_file,
            fields_to_export=self.product_fields_to_export,
            delimiter=self.delimiter
        )
        self.review_exporter = CsvItemExporter(
            self.review_file,
            fields_to_export=self.review_fields_to_export,
            delimiter=self.delimiter
        )
        self.product_exporter.start_exporting()
        self.review_exporter.start_exporting()

    def spider_closed(self, spider):
        """
        Finish exporting to CSV files and close CSV files.
        """
        self.product_exporter.finish_exporting()
        self.review_exporter.finish_exporting()
        self.product_file.close()
        self.review_file.close()

    def process_item(self, item, spider):
        """ This method is called for every item pipeline component.
        Pipeline uses for save data to CSV file.

        Data from ProductItem store to products.csv;
        Data from ReviewItem store to reviews.csv;

        :param item: container which collect all scraped data
        :param spider: spider specifications
        :return: container which collect all scraped data
        """
        if isinstance(item, ProductItem):
            self.product_exporter.export_item(item)
        elif isinstance(item, ReviewItem):
            self.review_exporter.export_item(item)
        return item
