# web-graphs
============

# install
- virtualenv venv
- source venv/bin/activate
- pip install -r requirements.txt

# run
- ./app/web.py --debug=1
- ./app/dealer.py
- ./app/crawler.py --debug=1
- ./app/parser.py --debug=1
- curl http://localhost:8888/

# shortcuts
- sudo supervisorctl update
- sudo supervisorctl start web-graph:*
- sudo rabbitmqctl list_queues

# desc
Парсим по одному разу всё что найдём на добавленных вручную и автоматом сайтах.
Если сайт не отпарсился, то записываем ошибку и забиваем на него.
Когда наткнёмся снова на ссылку на него - добавим и попробуем обновить.
Средняя периодичность апдейта - месяц. Надо эксперементировать со скоростью наполнения базы. Изначально надо накопить базу, а уже потом обновлять.
Первоначальный массив доменов ru зоны взят с r01, через их партнёрскую дырку стародавнюю. Остальные домены идут линками с начальных или добавляются вручную через сайт.


# relation types description
TODO