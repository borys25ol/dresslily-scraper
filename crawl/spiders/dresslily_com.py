# -*- coding: utf-8 -*-
import math
import re

from scrapy import Spider, Request
from scrapy_splash import SplashRequest

from crawl.items import DresslilyItemLoader, ProductItem, ReviewItem


class DresslilyComSpider(Spider):
    name = "dresslily.com"
    allowed_domains = ["dresslily.com"]
    start_urls = ["https://www.dresslily.com/hoodies-c-181.html"]

    product_next_page_pattern = (
        "https://www.dresslily.com/hoodies-c-181-page-{page}.html"
    )
    review_page_pattern = (
        "https://www.dresslily.com/m-review-a-view_review-goods_id-{product_id}.htm"
    )
    review_next_page_pattern = "https://www.dresslily.com/m-review-a-view_review-goods_id-{product_id}-page-{page}.html"

    products_per_page = 120
    reviews_per_page = 6

    custom_settings = {"CONCURRENT_REQUESTS": 2}

    def parse(self, response):
        """
        Calculate total pages in category and create requests for next pages.

        Using Splash for rendering JavaScript for showing discount badge.

        :param response: HTTP response
        :return: Splash requests for next pages
        """
        total_products = response.xpath('//div[@class="cat-name"]/span/text()')
        total_products = total_products.re_first(r"\d+")
        total_pages = math.ceil(int(total_products) / self.products_per_page)

        for page in range(1, total_pages + 1):
            url = self.product_next_page_pattern.format(page=page)
            yield SplashRequest(
                url=url,
                callback=self.parse_next_page,
                endpoint="render.html",
                args={"wait": 5},
            )

    def parse_next_page(self, response):
        """
        Create requests for product link and put discount to Request Meta.

        :param response: HTTP response
        :return: Scrapy Requests
        """
        products = response.xpath(
            '//div[@class="category-list js-category"]/div[contains(@class, "category-good")]'
        )
        for product in products:
            regular_price = product.xpath(
                './/span[@class="my-shop-price category-good-price-market dl-has-rrp-tag"]/@data-orgp'
            ).get()

            product_url = product.xpath(
                './p[@class="category-good-name"]/a/@href'
            ).get()

            yield Request(
                url=product_url,
                callback=self.parse_product,
                meta={"regular_price": float(regular_price) if regular_price else None},
            )

    def parse_product(self, response):
        """
        Scraping data from product pages.

        If rating and reviews contained on the product page than collected it too.

        :param response: HTTP response
        :return: item
        """
        l = DresslilyItemLoader(item=ProductItem(), response=response)

        regular_price = response.meta["regular_price"]

        l.add_xpath("product_id", '//input[@id="hidden-goodsId"]/@value')
        l.add_xpath("product_id", '//input[@id="hidden-goodsId-forAll"]/@value')

        l.add_value("product_url", response.url)

        l.add_css("name", ".goodtitle-wrap span.goodtitle")

        price_match = re.search('o\.goods\.price = "(.+)",', response.text)
        price = price_match.group(1)

        if regular_price:
            market_price_match = re.search(
                'o\.goods\.market_price = "(.+)",', response.text
            )
            market_price = market_price_match.group(1)

            l.add_value("discounted_price", price)
            l.add_value("original_price", market_price)
        else:
            l.add_value("original_price", price)

        l.add_css("rating", "#js_reviewCountText::text")

        product_info_names = l.get_xpath(
            '//div[@class="xxkkk20"]/strong/text()', self.get_valid_text
        )
        product_info_values = l.get_xpath(
            '//div[@class="xxkkk20"]/text()', self.get_valid_text, re=r"\w.+"
        )

        l.add_value(
            "product_info",
            self.get_product_info(product_info_names, product_info_values),
        )

        if l.get_output_value("rating"):
            yield response.request.replace(
                url=self.review_page_pattern.format(
                    product_id=l.get_output_value("product_id")
                ),
                callback=self.parse_reviews_next_page,
                meta={"product_id": l.get_output_value("product_id")},
            )

        yield l.load_item()

    def parse_reviews_next_page(self, response):
        """
        Create requests for reviews link.

        :param response: HTTP response
        :return: Scrapy Requests
        """
        total_reviews = response.xpath('//p[@class="reviewnum"]/text()').re_first(
            r"\d+"
        )
        total_pages = math.ceil(int(total_reviews) / self.reviews_per_page)
        for page in range(1, total_pages + 1):
            url = self.review_next_page_pattern.format(
                page=page, product_id=response.meta["product_id"]
            )
            yield response.request.replace(
                url=url, callback=self.parse_reviews, meta=response.meta
            )

    def parse_reviews(self, response):
        """
        Scraping data from reviews pages.

        :param response: HTTP response
        :return: item
        """
        reviews = response.xpath('//div[@class="reviewwrap"]//div[@class="reviewinfo"]')
        for review in reviews:
            l = DresslilyItemLoader(item=ReviewItem(), selector=review)

            l.add_value("product_id", response.meta["product_id"])

            l.add_xpath("rating", './/i[@class="icon-star-black"]', len)

            l.add_xpath("timestamp", './span[@class="reviewtime"]/text()')

            l.add_xpath("text", './p[@class="reviewcon"]/text()')

            l.add_xpath("size", './p[@class="color-size"]/span/text()', re="Size: (.+)")

            l.add_xpath(
                "color", './p[@class="color-size"]/span/text()', re="Color: (.+)"
            )

            yield l.load_item()

    @staticmethod
    def get_valid_text(values):
        """
        Extract clean text.
        """
        return [value.strip() for value in values]

    @staticmethod
    def get_product_info(names, values):
        """
        Extract joined product attributes.
        Data separated by `;`.

        Example: `Shirt Length:Regular;Sleeve Length:Full;`
        """
        joined = ["".join(map(str, item)) for item in zip(names, values)]
        return ";".join(joined)
