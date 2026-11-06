# Как развернуть сайт лабы (для Тихона)

Папка `showcase/` — это **статический сайт**. Бэкенд/Python на сервере НЕ нужен — только раздать файлы по HTTP(S).

## Что внутри
- `index.html` — хаб (главная, три кнопки).
- `s1.html` — кофейный блокнот (тёмный).
- `s2.html` — наш блокнот HoReCa (тёмный).
- `generator.html` — интерактивный генератор (marimo WASM, ползунки работают в браузере).

Открывается с `index.html`. Все ссылки относительные — папку можно переносить целиком.

## Требование к зрителю (преподу)
Нужен только **интернет у зрителя**: генератор (Pyodide/marimo) и формулы (MathJax) подтягивают библиотеки с CDN `jsdelivr`. Сам сайт статичен, серверной логики нет.

## Способ 1 — на свой сервер (nginx), рекомендую
Скопировать папку в корень сайта и отдать статику:
```
scp -r showcase/ user@СЕРВЕР:/var/www/coffee-stat/
```
Блок nginx:
```
server {
    listen 80;
    server_name coffee.ТВОЙ-ДОМЕН;
    root /var/www/coffee-stat;
    index index.html;
}
```
Готово: `http://coffee.ТВОЙ-ДОМЕН/` → хаб. (Для https — обычный certbot.)

## Способ 2 — быстро, любой хостинг статики
Залить папку `showcase/` как есть на любой статический хостинг: **Netlify** (перетащить папку в drag-and-drop), **Vercel**, **GitHub Pages**, Caddy `file_server`, Apache — что угодно, что отдаёт файлы. Корень = `index.html`.

## Способ 3 — вообще без своего сервера: GitHub Pages
1. Скопировать содержимое `showcase/` в папку `docs/` в репозитории (или в ветку `gh-pages`).
2. В настройках репо → Pages → Source: `main /docs`.
3. Получите URL вида `https://mironiks007.github.io/fifty-shades-of-coffee-stat/` — даёте преподу, ноль серверной возни.
(Нужны права в репозитории инфохимиков — согласовать.)

## Проверка после заливки
Открыть `index.html`, кликнуть три кнопки. Генератор грузится ~10–40 сек (качает Pyodide с CDN) — это нормально, нужен интернет.

## Если меняли блокноты и надо пересобрать страницы
В рабочей копии проекта (где есть venv `.venv-s2`):
```
# тёмные страницы блокнотов
python3 render_dark.py stat-lab1-s1.ipynb  showcase/s1.html     # s1_dark.ipynb для кофе
python3 render_dark.py stat-lab1-s2.ipynb  showcase/s2.html
# интерактивный генератор (WASM)
.venv-s2/bin/marimo export html-wasm marimo_generator.py -o showcase/generator.html --single-file --mode run -f
```
`index.html` правится руками (обычная HTML-страница).
