import requests
from pathlib import Path
import json
import time


class Parse5ka:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
    }

    def __init__(self, start_url, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response

            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f'{product["id"]}.json')
            self._save(product, file_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data['next']
            for product in data['results']:
                yield product

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


class Parse5kaFromCategories(Parse5ka):
    def __init__(self, start_url, cat_url, save_path):
        super().__init__(start_url, save_path)
        # self.start_url = start_url
        # self.save_path = save_path
        self.cat_url = cat_url

    def get_categories(self):
        categories = self._get_response(self.cat_url)
        return categories.json()

    def run(self):
        for category in self.get_categories():
            data = {
                'name': category['parent_group_name'],
                'code': category['parent_group_code'],
                'product': []
            }
            new_url = self.start_url + '/?' + f'categories={category["parent_group_code"]}'

            for product in self._parse(new_url):
                data['product'].append(product)

            file_path = self.save_path.joinpath(f'{category["parent_group_name"]}.json')
            self._save(data, file_path)


def get_save_path(dir_name: str) -> Path:
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()

    return save_path


if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers'
    url1 = 'https://5ka.ru/api/v2/categories'
    product_path = get_save_path('products')
    parser = Parse5ka(url, product_path)
    parser_from_cat = Parse5kaFromCategories(url, url1, product_path)
    parser_from_cat.run()
