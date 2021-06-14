
## Методы сбора и обработки данных из сети Интернет.


### Урок 1. Основы клиент-серверного взаимодействия. Парсинг API.


**Задание:**

Организовать сбор данных с сайта https://5ka.ru/special_offers/:

* Необходимо реализовать метод сохранения данных в .json файлы.
* Данные скачиваются с источника, при вызове метода/функции сохранения в файл.
* Для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.

Пример структуры данных для файла:

{

"name": "имя категории",

"code": "Код соответсвующий категории (используется в запросах)",

"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории

}


**Примечание:**

>_Нейминг ключей можно делать отличным от примера._

### Урок 2. Парсинг HTML. BeautifulSoup, MongoDB

#### Задание:

Необходимо обойти все записи в блоге:https://gb.ru/posts/ и извлеч из них информацию следующих полей:

* url страницы материала;
* заголовок материала;
* первое изображение материала (ссылка);
* дата публикации (в формате datetime);
* имя автора материала;
* ссылка на страницу автора материала;
* комментарии в виде (автор комментария и текст комментария).

Структуру сохранить в MongoDB.

### Урок 3. Системы управления базами данных MongoDB и SQLite в Python.

#### Задание:
* Продолжить работу с парсером блога GB;
* Реализовать SQL базу данных посредствам SQLAlchemy;
* Реализовать реалиционные связи между: Постом и Автором, Постом и Тегом, Постом и комментарием, Комментарием и комментарием;

### Урок 4. Парсинг HTML. XPath.

#### Задание.

Источник https://auto.youla.ru/

Обойти все марки авто и зайти на странички объявлений. Собрать след стуркутру и сохранить в БД Монго:

* Название объявления;
* Список фото объявления (ссылки);
* Список характеристик;
* Описание объявления;
* Ссылка на автора объявления;
* Дополнительно попробуйте вытащить номер телефона.

### Урок 5. Scrapy.

#### Задание.
Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
вакансии удаленной работы.

Задача: Обойти с точки входа все вакансии и собрать след данные:

* название вакансии;
* оклад (строкой от до или просто сумма);
* oписание вакансии;
* ключевые навыки - в виде списка названий;
* ссылка на автора вакансии.


Перейти на страницу автора вакансии,
собрать данные:
* название;
* сайт ссылка (если есть);
* сферы деятельности (списком);
* описание.
 
Обойти и собрать все вакансии данного автора.
