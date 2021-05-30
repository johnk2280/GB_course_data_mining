import typing
import time
import requests
from urllib.parse import urljoin
import bs4
import lxml
import pymongo


class GbBlogParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
    }
    __parse_time = 0

    def __init__(self, start_url, db, delay=1.0):
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())

            response = requests.get(url, headers=self.headers)
            print(f'RESPONSE: {response.url}')
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response

    def get_task(self, url, callback: typing.Callable) -> typing.Callable:
        def task():
            response = self._get_response(url)
            return callback(response)

        return task

    def tasks_creator(self, urls: set, callback: typing.Callable):
        urls_set = urls - self.done_urls
        for url in urls_set:
            self.tasks.append(
                self.get_task(url, callback)
            )
            self.done_urls.add(url)

    def run(self):

        while True:
            try:
                task = self.tasks.pop(0)
                task()
            except IndexError:
                break

    def parse_feed(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        ul_paginations = soup.find('ul', attrs={'class': 'gb__pagination'})
        pagination_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in ul_paginations.find_all('a') if itm.attrs.get('href')
            )
        self.tasks_creator(pagination_links, self.parse_feed)
        post_wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        post_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in post_wrapper.find_all('a', attrs={'class': 'post-item__title'}) if itm.attrs.get('href')
        )
        self.tasks_creator(post_links, self.parse_post)

    def parse_post(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        author_name_tag = soup.find('div', attrs={'itemprop': 'author'})
        data = {
            'url': response.url,
            'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            'author': {
                'url': urljoin(response.url, author_name_tag.parent.attrs['href']),
                'name': author_name_tag.text
            }
        }
        self._save_data(data)

    def _save_data(self, data: dict):
        collection = self.db['gb_blog_parse']
        collection.insert_one(data)


if __name__ == '__main__':
    client_db = pymongo.MongoClient('mongodb://localhost:27017')
    db = client_db['data_mining']
    url = 'https://gb.ru/posts'
    parser = GbBlogParse(url, db)
    parser.run()
