

## Install
1. ```
pip install -r  requirements.txt
```

2. Создать с .env DATABASE_URL с url к базе

3. ```
./manage.py makemigrations
```

4. ```
./manage.py migrate
```

## Deploy
1. Загрузить данные в базу:
```
./manage.py import_xlsx_file --file ../data.xlsx
```
2.
```
./manage.py scrapy runspider spiders/wildberries.py
```

## доступ по API
1. /api/v1/products/?format=json получить список продуктов в формате json
2. /api/v1/products/46534885/?format=json получить по артиклу
