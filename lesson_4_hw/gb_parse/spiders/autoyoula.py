import scrapy
from urllib.parse import unquote
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.css(selector_str):
            url = a_link.attrib.get('href')
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            '.TransportMainFilters_brandsList__2tIkv a.blackLink',
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            'a.SerpSnippet_name__3F7Yu',
            self.car_parse
        )

    def car_parse(self, response):
        advert_data = {
            'advert_title': response.css('.AdvertCard_advertTitle__1S1Ak::text').extract_first(),
            'advert_image_links': [
                el.attrib.get('src')
                for el in response.css('.PhotoGallery_block__1ejQ1 img.PhotoGallery_photoImage__2mHGn')
            ],
            'description': response.css(
                '.AdvertCard_description__2bVlR div.AdvertCard_descriptionInner__KnuRi::text'
            ).extract_first(),
            'seller_data': self._get_seller_data(response)

        }

    def _get_seller_data(self, response) -> dict:
        sub_string = 'window.transitState = decodeURIComponent'
        id_pattern = r'"youlaId","(\w+)","avatar"'
        for selector in response.css('script'):
            if sub_string in selector.extract():
                component = unquote(selector.extract())
                seller_id = re.findall(id_pattern, component)[0]
                seller_url = f'https://youla.ru/user/{seller_id}'
                print(1)


