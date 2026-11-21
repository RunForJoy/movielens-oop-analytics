# MovieLens Analytics: Modular OOP Library & Data Storytelling Report

[English](#english) | [Русский](#русский)

---

## English

An end-to-end data analysis project built around the **MovieLens** dataset using pure **Python 3** standard libraries and web scraping tools (without `pandas` or `numpy`). The project consists of a reusable Object-Oriented analytics module (`movielens_analysis.py`), a comprehensive `pytest` test suite, and an interactive **Jupyter Notebook** storytelling report (`movielens_report.ipynb`) with execution time benchmarks (`%timeit`) on every analytical step.

###  Tech Stack & Tools
* **Language:** Python 3 (standard library: `os`, `sys`, `collections`, `functools`, `datetime`, `re`, `json`, `urllib`)
* **Web Scraping:** `requests`, `BeautifulSoup4` (IMDb metadata enrichment)
* **Testing & Benchmarking:** `pytest`, Jupyter Notebook (`%timeit`)

###  Project Structure (`src/`)

* **`movielens_analysis.py`** — Core OOP module implementing four domain-specific analytical classes (`Ratings`, `Tags`, `Movies`, `Links`) and a `Tests` suite:
  * **`Ratings`:** Analyzes rating distributions by release year, user activity, rating scores, and computes top movies by rating count, average/median scores, and rating variance (controversial films).
  * **`Tags`:** Extracts tag statistics, identifies the longest and most popular tags, and performs keyword-based tag searches.
  * **`Movies`:** Parses movie titles and release years, calculates yearly release dynamics, genre distributions, and identifies multi-genre films.
  * **`Links`:** Enriches MovieLens records with external IMDb metadata (directors, budgets, gross revenue, runtime) via web scraping and ranks top-performing movies and directors.
  * **`Tests`:** Automated `pytest` suite validating return types, element types, sorting order, and calculation accuracy across all module methods.
* **`movielens_report.ipynb`** — Interactive data storytelling report structured in a Q&A format, relying exclusively on the custom `movielens_analysis` module and profiling every analytical query with `%timeit`.

###  Usage Examples
* Run the automated test suite: `pytest src/movielens_analysis.py`
* Open the interactive report: `jupyter notebook src/movielens_report.ipynb`

---

## Русский

Сквозной аналитический проект на базе датасета **MovieLens**, реализованный на чистом **Python 3** и инструментах веб-скрейпинга (без использования `pandas` и `numpy`). Проект включает переиспользуемую объектно-ориентированную библиотеку (`movielens_analysis.py`), набор модульных тестов `pytest` и интерактивный отчёт в формате дата-сторителлинга в **Jupyter Notebook** (`movielens_report.ipynb`) с замером времени выполнения (`%timeit`) для каждого аналитического запроса.

###  Стек и инструменты
* **Язык:** Python 3 (стандартная библиотека: `os`, `sys`, `collections`, `functools`, `datetime`, `re`, `json`, `urllib`)
* **Веб-скрейпинг:** `requests`, `BeautifulSoup4` (обогащение данных информацией с IMDb)
* **Тестирование и бенчмаркинг:** `pytest`, Jupyter Notebook (`%timeit`)

###  Структура проекта (`src/`)

* **`movielens_analysis.py`** — Основной ООП-модуль с четырьмя прикладными аналитическими классами (`Ratings`, `Tags`, `Movies`, `Links`) и классом тестирования `Tests`:
  * **`Ratings`:** Анализ распределения оценок по годам, активности пользователей и баллам; поиск топ-фильмов по количеству оценок, среднему/медианному рейтингу и дисперсии оценок (самые неоднозначные фильмы).
  * **`Tags`:** Статистика пользовательских тегов, поиск самых длинных и популярных тегов, а также фильтрация тегов по ключевым словам.
  * **`Movies`:** Парсинг названий фильмов и годов выпуска, анализ динамики выхода картин по годам, распределение по жанрам и поиск фильмов с наибольшим числом жанров.
  * **`Links`:** Обогащение записей MovieLens внешними метаданными с IMDb (режиссёры, бюджеты, кассовые сборы, хронометраж) с помощью парсинга и построение рейтингов самых успешных фильмов и режиссёров.
  * **`Tests`:** Набор тестов на `pytest`, проверяющий типы возвращаемых структур и элементов, корректность сортировки и точность вычислений всех методов модуля.
* **`movielens_report.ipynb`** — Интерактивный аналитический отчёт в формате «вопрос–ответ», построенный исключительно на методах модуля `movielens_analysis` с замером производительности каждой ячейки через `%timeit`.

###  Примеры запуска
* Запуск модульных тестов: `pytest src/movielens_analysis.py`
* Открытие интерактивного отчёта: `jupyter notebook src/movielens_report.ipynb`
