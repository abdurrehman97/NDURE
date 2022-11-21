from scrapy.spiders import SitemapSpider
import re
from scrapy import Request
import scrapy


class NdureSpider(SitemapSpider):

    name = 'ndure'
    sitemap_urls = ['https://www.ndure.com/sitemap_collections_1.xml']
    sitemap_rules = [('/collections/', 'parse_product_shelf')]

    def start_requests(self):
        yield Request('https://www.ndure.com/collections/winter-collection-2022-men', callback=self.parse_product_shelf)

    def parse(self, response, **kwargs):

        type_list = response.css('div.slide-content a')
        yield from response.follow_all(type_list, callback=self.parse_categories)

    def parse_categories(self, response):

        category_list = response.css('.site-nav li a')
        yield from response.follow_all(category_list, callback=self.parse_product_shelf)

    def parse_product_shelf(self, response):

        shelf_products = response.css('.product-image a')
        if shelf_products:
            yield from response.follow_all(shelf_products, callback=self.parse_items)

            next_page_url = response.url
            page_number = re.findall(r'\?page=(\d+)', next_page_url)
            page_number = ''.join(page_number)

            if not page_number:
                page_number = '?page=1'
                next_page = f'{next_page_url}{page_number}'

            else:
                current_page = int(page_number) + 1
                previous_page = re.sub(r'\?page=(\d+)', '', next_page_url)
                making_url = f"{previous_page}{'?page='}"
                next_page = f'{making_url}{current_page}'

            yield scrapy.Request(
                url=next_page,
                callback=self.parse_product_shelf
            )

    def parse_items(self, response):

        yield {
            'name': response.css('.product-title span::text').get().strip(),
            'sku': response.css('div .sku-product span::text').get(),
            'old_price': response.css('span.compare-price::text').get(),
            'new_price': response.css('span.on-sale::text').get(),
            'description': response.css('.tab-content div p::text').get(),
            'url': response.url
        }
