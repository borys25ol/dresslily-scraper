# -*- coding: utf-8 -*-
import scrapy
from scrapy import Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.html import replace_entities

from crawl.utils import html_to_text, strip_nlts


class DresslilyItemLoader(ItemLoader):
    """
    Default Item loader for ProductItem and ReviewItem
    """
    default_input_processor = MapCompose(
        html_to_text,
        replace_entities,
        strip_nlts,
        str.strip,
    )
    default_output_processor = TakeFirst()


class ProductItem(Item):
    """
    Item for product links

    example: https://www.dresslily.com/whole-colored-drawstring-casual-hoodie-product3647297.html
    """
    product_id = scrapy.Field()
    product_url = scrapy.Field()
    name = scrapy.Field()
    discount = scrapy.Field()
    discounted_price = scrapy.Field(input_processor=MapCompose(float))
    original_price = scrapy.Field(input_processor=MapCompose(float))
    rating = scrapy.Field(input_processor=MapCompose(int))
    product_info = scrapy.Field()


class ReviewItem(scrapy.Item):
    """
    Item for review links

    example: https://www.dresslily.com/m-review-a-view_review-goods_id-5475390-page-1.html
    """
    product_id = scrapy.Field()
    rating = scrapy.Field()
    timestamp = scrapy.Field()
    text = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()


