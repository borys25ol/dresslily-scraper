# -*- coding: utf-8 -*-
from pathlib import Path

from scrapy import signals
from scrapy.exporters import CsvItemExporter

from crawl.items import ProductItem, ReviewItem


class CsvPipeline:
    """
    Custom CSV pipeline.

    Push all items to 'products.csv' if item from `ProductItem`.
    Push all items to 'reviews.csv' if item from `ReviewItem`.
    """

    PRODUCT_FIELDS = [
        "product_id",
        "product_url",
        "name",
        "discount",
        "discounted_price",
        "original_price",
        "rating",
        "product_info",
    ]
    REVIEWS_FIELDS = [
        "product_id",
        "rating",
        "timestamp",
        "text",
        "size",
        "color",
    ]

    PRODUCTS_FILE_NAME = Path(__file__).parent / "results" / "products.csv"
    REVIEWS_FILE_NAME = Path(__file__).parent / "results" / "reviews.csv"

    DELIMITER = ","

    def __init__(self):
        self.product_file = None
        self.review_file = None
        self.product_exporter = None
        self.review_exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        Setup signals for crawler.
        """
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        """
        Initialize exporters after scraping start.
        """
        self.product_file = open(self.PRODUCTS_FILE_NAME, "w+b")
        self.review_file = open(self.REVIEWS_FILE_NAME, "w+b")

        self.product_exporter = CsvItemExporter(
            file=self.product_file,
            fields_to_export=self.PRODUCT_FIELDS,
            delimiter=self.DELIMITER,
        )
        self.review_exporter = CsvItemExporter(
            file=self.review_file,
            fields_to_export=self.REVIEWS_FIELDS,
            delimiter=self.DELIMITER,
        )

        self.product_exporter.start_exporting()
        self.review_exporter.start_exporting()

    def spider_closed(self, spider):
        """
        Finish exporting to CSV files and close files.
        """
        self.product_exporter.finish_exporting()
        self.review_exporter.finish_exporting()

        self.product_file.close()
        self.review_file.close()

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component.
        Pipeline uses for save data to CSV file.

        Data from `ProductItem` store to `products.csv`;
        Data from `ReviewItem` store to `reviews.csv`;

        :param item: container which collect all scraped data
        :param spider: spider specifications
        :return: container which collect all scraped data
        """
        if isinstance(item, ProductItem):
            self.product_exporter.export_item(item)

        elif isinstance(item, ReviewItem):
            self.review_exporter.export_item(item)

        return item
