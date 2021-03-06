import typing
import time
import requests
from urllib.parse import urljoin
import bs4
import pymongo
from datetime import datetime
from database.database import Database


class GbBlogParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
    }
    __parse_time = 0

    def __init__(self, start_url, db: Database, delay=1.0):
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url, params=None):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())

            response = requests.get(url, params=params, headers=self.headers)
            print(f'RESPONSE: {response.url}')
            self.__parse_time = time.time()
            if response.status_code in (200, 206):
                return response

            return f'Something went wrong', response.status_code

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
        author_url = author_name_tag.parent.attrs['href']
        try:
            img_link = soup.find('div', attrs={'class': 'blogpost-content'}).find('img').get('src')
        except AttributeError:
            img_link = 'No img link'

        post_date = datetime.strptime(
            soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').get('datetime'),
            '%Y-%m-%dT%H:%M:%S%z'
        )
        data = {
            'post_data': {
                'url': response.url,
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'id': int(soup.find('comments').attrs.get('commentable-id')),
                'img_link': img_link,
                'post_date': post_date
            },
            'author_data': {
                'url': urljoin(response.url, author_url),
                'name': author_name_tag.text,
                'gb_id': int(author_url.split('/')[-1])
            },
            'comments_data': self._get_comments(soup.find('comments')),
            'tag_data': [
                {'url': urljoin(response.url, el.attrs.get('href')),
                 'name': el.text} for el in soup.find_all('a', attrs={'class': 'small'})
            ]
        }
        self._save_data(data)

    def _get_comments(self, tag: bs4.element.Tag) -> list:
        url = 'https://gb.ru/api/v2/comments'
        params = {
            'commentable_type': tag.get('commentable-type'),
            'commentable_id': tag.get('commentable-id'),
            'order': tag.get('order')
        }
        response = self._get_response(url, params=params)
        return response.json()

    def _save_data(self, data: dict):
        self.db.add_post(data)


if __name__ == '__main__':
    # client_db = pymongo.MongoClient('mongodb://localhost:27017')
    orm_database = Database('sqlite:///gb_blog_parse.db')
    # db = client_db['data_mining']
    url = 'https://gb.ru/posts'
    parser = GbBlogParse(url, orm_database)
    parser.run()
