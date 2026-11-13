# Лабораторная работа № 1 — Fifty Shades of Coffee

Комплект S1 и S2 с допзаданиями.

| Файл | Что в нём |
|---|---|
| [stat-lab1-s1.ipynb](stat-lab1-s1.ipynb) | Описание данных, выборки и статистические проверки |
| [stat-lab1-s2.ipynb](stat-lab1-s2.ipynb) | Основной генератор влажности и итоговые метрики |
| [stat-lab1-s2-bonus-alias.ipynb](stat-lab1-s2-bonus-alias.ipynb) | Псевдонимы, отбор с отклонением, суперпозиция и бета-распределение |
| [stat-lab1-s2-extra-dataset.ipynb](stat-lab1-s2-extra-dataset.ipynb) | Проверка профилей на дополнительной выгрузке CQI 2023 |
| [stat-lab1-s2-algorithms.ipynb](stat-lab1-s2-algorithms.ipynb) | Исследование восьми алгоритмов с запускаемыми примерами |
| [S2-RESULTS.md](S2-RESULTS.md) | Общая сводка метрик S2 |
| [AUTOTESTS.md](AUTOTESTS.md) · [tests/test_generators.py](tests/test_generators.py) | Инструкция и 10 автотестов |
| [.github/workflows/generator-tests.yml](.github/workflows/generator-tests.yml) | Запуск автотестов в GitHub Actions |
| [coffee_ratings.csv](coffee_ratings.csv) | Основной датасет: 1339 записей до отбора. [Источник](https://github.com/rfordatascience/tidytuesday/tree/main/data/2020/2020-07-07) |
| [coffee-cqi-2023.csv](coffee-cqi-2023.csv) | Дополнительная выгрузка: 207 записей до отбора. [Источник CSV](https://github.com/fatih-boyar/coffee-quality-data-CQI/blob/047db1c5c95e69b7ebad746a66bffd28e8186e3b/df_arabica_clean.csv) · [лицензия репозитория источника](CQI-2023-LICENSE.txt) |
| [requirements-lab.txt](requirements-lab.txt) · [requirements-autotests.txt](requirements-autotests.txt) | Зависимости для ноутбуков и отдельно для автотестов |

Для просмотра открываем ноутбуки по порядку: S1, S2, затем допзадания. В ноутбуках сохранены результаты. Для пересчёта запускаем все ячейки нужного ноутбука сверху вниз. Оба CSV оставляем рядом с ноутбуками.

Локальный запуск из распакованной папки с Python 3.12:

```sh
python -m pip install -r requirements-lab.txt
python -m jupyterlab
```

Запуск автотестов:

```sh
python -m unittest discover -s tests -v
```

При переносе в репозиторий сохраняем имена файлов, относительные пути и каталог `.github/workflows/`. Уже имеющийся README можно оставить: этот указатель называется `LAB01-START.md`.
