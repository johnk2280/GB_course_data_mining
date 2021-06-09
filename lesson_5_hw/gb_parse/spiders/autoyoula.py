import scrapy
from urllib.parse import unquote
import re
import pymongo


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super(AutoyoulaSpider, self).__init__(*args, **kwargs)
        self.client_db = pymongo.MongoClient('mongodb://localhost:27017')
        self.db = self.client_db['data_mining']

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.xpath(selector_str):
            yield response.follow(a_link, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            '//div[contains(@class, "TransportMainFilters_brandsList")]//a[@data-target="brand"]/@href',
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            '//div[contains(@class, "Paginator_block")]//a[@data-target-id="button-link-serp-paginator"]/@href',
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            '//article[@data-target="serp-snippet"]//a[contains(@class, "SerpSnippet_name")]/@href',
            self.car_parse
        )

    def car_parse(self, response):
        advert_data = {
            'advert_title': response.xpath(
                '//div[contains(@class, "AdvertCard_advertTitle")]/text()'
            ).extract_first(),
            'advert_price': float(response.xpath(
                '//div[contains(@class, "AdvertCard_price")]/text()'
            ).extract_first().replace('\u2009', '')),
            'advert_image_links': response.xpath(
                '//div[contains(@class, "PhotoGallery_block")]//img[contains(@class, "PhotoGallery_photoImage")]/@src'
            ).extract(),
            'description': response.xpath(
                '//div[contains(@class, "AdvertCard_descriptionInner")]/text()'
            ).extract_first(),
            'seller_data': self._get_seller_data(response)
        }
        self._save(advert_data)

    def _save(self, data):
        collection = self.db['autoyoula_parse']
        collection.insert_one(data)

    def _get_seller_data(self, response) -> dict:
        sub_string = 'window.transitState = decodeURIComponent'
        id_pattern = r'"youlaId","(\w+)","avatar"'
        phone_pattern = r'"phone","(\w+)==","time"'
        try:
            for selector in response.css('script'):
                if sub_string in selector.extract():
                    component = unquote(selector.extract())
                    seller_id = re.findall(id_pattern, component)[0]
                    seller_phone = re.findall(phone_pattern, component)[0]
                    seller_url = f'https://youla.ru/user/{seller_id}'
                    return {'seller_id': seller_id, 'seller_url': seller_url, 'seller_phone': seller_phone}
        except (TypeError, IndexError) as err:
            pass
