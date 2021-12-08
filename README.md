## Список рассматриваемых документоориентированных СУБД

 - MongoDB
 - ArangoDB
 - CouchDB
 - RavenDB
 - Cassandra
 - ~~Couchbase~~
 - ~~RealmDB~~
 - ~~RethinkDB~~
 - ~~DynamoDB~~
 - ~~IBM Cloudant~~


Выбирал я их по таким критериям:
1) Бесплатные (!).
2) Есть драйвер для питона.
3) Графический интерфейс (мне нужно, окей).
4) Масштабируемость. 
5) Документация.


## Как запустить

Требования: Python 3.9 and Poetry.

1) Выполнить `poetry install`, чтобы установить зависимости.
2) `docker-compose up`.
3) `python main.py DATABASE_NAME`, где возможные значения для DATABASE_NAME — mongo, arango, raven.
Необязательный флаг `--populate` начинает генерацию данных.

## Примечание

Для `RavenDB` база данных автоматически не создается, 
нужно сделать это вручную, перейдя по адресу `http://localhost:8080` после того как подняли контейнеры в докере.
При первом входе вас попросят:
1) Согласиться с лицензионным соглашением.
2) Выбрать настройки безопасности (жмем Unsecure).
3) Выбрать ip адрес для сервера. Пишем 0.0.0.0


### TODO:

- [ ] Add Cassandra.
- [ ] Add CouchDB.
- [ ] Look at the way you generate data.
- [ ] Better performance tests. Yandex Tank, etc.
- [ ] Programmatically create a database for RavenDB.
- [ ] Logging.
