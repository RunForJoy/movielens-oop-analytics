#!/usr/bin/env python3
import re
from collections import Counter
from datetime import datetime, timezone

import requests


def average(data):
    return sum(data) / len(data) if data else 0


def median(data):
    if not data:
        return 0
    srtd = sorted(data)
    n = len(srtd)
    mid = n // 2
    return srtd[mid] if n % 2 != 0 else (srtd[mid - 1] + srtd[mid]) / 2


def variance(data):
    avg = average(data)
    return sum((x - avg) ** 2 for x in data) / len(data) if data else 0


def get_year_from_ts(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).year
    except Exception:
        return None


###################################################################################


class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file):
        """Put here any fields that you think you will need."""
        self.path_to_the_file = path_to_the_file
        self.movies_list = []

        base_pattern = r"(?:\".*?\"|[^,\",\n]+)(?=\s*,|\s*$)"

        try:
            with open(self.path_to_the_file, encoding="UTF-8") as f:
                next(f)

                for i, line in enumerate(f):
                    if i == 1000:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    raw_data = re.findall(base_pattern, line)
                    cleaned_data = [field.strip('"') for field in raw_data]

                    if len(cleaned_data) != 3:
                        continue

                    try:
                        movie_id = int(cleaned_data[0])
                    except ValueError:
                        continue

                    title = cleaned_data[1]
                    year_match = re.search(r"\((\d{4})\)$", title)
                    year = int(year_match.group(1)) if year_match else None

                    self.movies_list.append(
                        {
                            "movieId": movie_id,
                            "title": title,
                            "year": year,
                            "genres": cleaned_data[2],
                        }
                    )

        except Exception:
            pass

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years
        and the values are counts that are sorted by counts descendingly.
        """

        counted_years = Counter(
            dct["year"] for dct in self.movies_list if dct["year"] is not None
        )
        return dict(
            sorted(counted_years.items(), key=lambda x: x[1], reverse=True)
        )

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts
        that are sorted by counts descendingly.
        """

        list_of_genres = [dct["genres"].split("|") for dct in self.movies_list]

        distinct_genres = []
        for genre in list_of_genres:
            distinct_genres.extend(genre)

        # genres = [g for dct in self.movies_list for g in dct['genres'].split('|')]
        counted_genres = Counter(distinct_genres)
        return dict(
            sorted(counted_genres.items(), key=lambda x: x[1], reverse=True)
        )

    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the number of genres of the movie sorted by numbers descendingly.
        """
        ordered = sorted(
            [
                (dct["title"], len(dct["genres"].split("|")))
                for dct in self.movies_list
            ],
            key=lambda x: x[1],
            reverse=True,
        )
        return dict(ordered[:n])


###################################################################################


class Ratings:
    """Анализ данных из ratings.csv"""

    def __init__(self, path_to_the_file):
        self.path_to_the_file = path_to_the_file
        self.ratings_list = []

        try:
            with open(self.path_to_the_file, encoding="UTF-8") as f:
                next(f)
                for i, line in enumerate(f):
                    if i == 1000:
                        break
                    line = line.strip()

                    parts = line.split(",")
                    if len(parts) == 4:
                        try:
                            self.ratings_list.append(
                                {
                                    "userId": int(parts[0]),
                                    "movieId": int(parts[1]),
                                    "rating": float(parts[2]),
                                    "timestamp": int(parts[3]),
                                }
                            )

                        except ValueError:
                            continue
        except Exception:
            pass

    class Movies:
        def __init__(self, ratings, titles_dict=None):
            self.ratings = ratings
            self.titles_dict = titles_dict if titles_dict else {}
            self.id_rating_dct = {}
            try:
                for dct in self.ratings:
                    m_id = dct.get("movieId")
                    if m_id is not None:
                        self.id_rating_dct.setdefault(m_id, []).append(
                            dct["rating"]
                        )
            except Exception:
                pass

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts.
            sorted by years ascendingly. You need to extract years from timestamps.
            """
            try:
                years = [get_year_from_ts(d["timestamp"]) for d in self.ratings]
                return dict(sorted(Counter(years).items()))
            except Exception:
                return {}

        def dist_by_rating(self):
            from collections import Counter

            try:
                ratings = [d["rating"] for d in self.ratings]
                return dict(sorted(Counter(ratings).items()))
            except Exception:
                return {}

        def top_by_num_of_ratings(self, n):
            from collections import Counter

            try:
                counts = Counter([d["movieId"] for d in self.ratings])
                top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[
                    :n
                ]
                return {self.titles_dict.get(k, str(k)): v for k, v in top}
            except Exception:
                return {}

        def top_by_ratings(self, n, metric=average):
            try:
                res = []
                for m_id, scores in self.id_rating_dct.items():
                    res.append(
                        (
                            self.titles_dict.get(m_id, str(m_id)),
                            round(metric(scores), 2),
                        )
                    )
                return dict(sorted(res, key=lambda x: x[1], reverse=True)[:n])
            except Exception:
                return {}

        def top_controversial(self, n):
            try:
                res = []
                for m_id, scores in self.id_rating_dct.items():
                    res.append(
                        (
                            self.titles_dict.get(m_id, str(m_id)),
                            round(variance(scores), 2),
                        )
                    )
                return dict(sorted(res, key=lambda x: x[1], reverse=True)[:n])
            except Exception:
                return {}

    class Users(Movies):
        """
        In this class, three methods should work.
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
        Inherit from the class Movies. Several methods are similar to the methods from it.
        """

        def __init__(self, ratings):
            super().__init__(ratings, titles_dict=None)
            self.id_rating_dct = {}
            try:
                for dct in self.ratings:
                    u_id = dct.get("userId")
                    rat = dct.get("rating")
                    if u_id is not None and rat is not None:
                        self.id_rating_dct.setdefault(u_id, []).append(rat)
            except Exception:
                pass

        def dist_by_num_of_ratings(self):
            """Returns the distribution of users by the number of ratings made by them."""

            try:
                counts = [len(v) for v in self.id_rating_dct.values()]
                dist = Counter(counts)
                return dict(sorted(dist.items()))
            except Exception:
                return {}

        def dist_by_ratings(self, metric=average):
            """Returns the distribution of users by average or median ratings made by them."""
            try:
                user_metrics = [
                    round(metric(scores), 2)
                    for scores in self.id_rating_dct.values()
                ]
                dist = Counter(user_metrics)
                return dict(sorted(dist.items()))
            except Exception:
                return {}

        def top_controversial(self, n):
            """
            The method returns top-n users with the biggest variance of their ratings.
            Inherited from Movies.
            """
            return super().top_controversial(n)


##################################################################################################


class Tags:
    """
    Analyzing data from tags.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """

        self.path_to_the_file = path_to_the_file
        self.tags_list = []

        try:
            with open(self.path_to_the_file, encoding="UTF-8") as f:
                next(f)

                for i, line in enumerate(f):
                    if i == 1000:
                        break

                    line = line.strip()
                    parts = line.split(",")

                    if len(parts) != 4:
                        continue
                    else:
                        self.tags_list.append(parts[2])

        except Exception:
            pass

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        try:
            unique_tags = set(self.tags_list)
            tag_pattern = r"\b[\w\-']+\b"
            tags_data = [
                (tag, len(re.findall(tag_pattern, tag))) for tag in unique_tags
            ]
            return dict(sorted(tags_data, key=lambda x: x[1], reverse=True)[:n])
        except Exception:
            return {}

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        try:
            return sorted(set(self.tags_list), key=len, reverse=True)[:n]
        except Exception:
            return []

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        try:
            most_words_set = set(self.most_words(n).keys())
            longest_set = set(self.longest(n))
            return list(most_words_set & longest_set)
        except Exception:
            return []

    def most_popular(self, n):
        """
        The method returns the most popular tags.
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        try:
            return dict(Counter(self.tags_list).most_common(n))
        except Exception:
            return {}

    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        try:
            tags_with_word = [
                t for t in set(self.tags_list) if word.lower() in t.lower()
            ]
            return sorted(tags_with_word)
        except Exception:
            return []


#######################################################################################


class Links:
    """
    Analyzing data from links.csv using IMDB GraphQL API.
    """

    def __init__(self, path_to_the_file):
        self.path = path_to_the_file
        self.movies_data = []
        self.id_map = self._load_links()

    def _load_links(self):
        """Считывает links.csv и создает мапу {movieId: imdbId}"""
        mapping = {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                next(f)
                for line in f:
                    line = line.strip().replace('"', "")
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) >= 2:
                        try:
                            m_id = int(parts[0])
                            mapping[m_id] = "tt" + parts[1].zfill(7)
                        except (ValueError, IndexError):
                            continue
        except Exception:
            pass
        return mapping

    def _fetch_movie(self, imdb_id):
        """Ваш метод запроса к GraphQL API"""
        url = "https://api.graphql.imdb.com/"

        query = """
        query GetMovieData($id: ID!) {
          title(id: $id) {
            titleText { text }
            productionBudget { budget { amount currency } }
            lifetimeGross(boxOfficeArea: WORLDWIDE) { total { amount currency } }
            runtime { seconds }
            principalCredits {
              category { id }
              credits { name { nameText { text } } }
            }
          }
        }
        """

        payload = {"query": query, "variables": {"id": imdb_id}}
        headers = {"Content-Type": "application/json"}  # Критично для GraphQL

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            r.raise_for_status()
        except requests.RequestException:
            return None

        data = r.json().get("data", {}).get("title", {})
        if not data:
            return None

        title = data.get("titleText", {}).get("text", "N/A")

        pb = data.get("productionBudget") or {}
        budget = (pb.get("budget") or {}).get("amount", 0) or 0

        lg = data.get("lifetimeGross") or {}
        gross = (lg.get("total") or {}).get("amount", 0) or 0

        rt = data.get("runtime") or {}
        runtime = (rt.get("seconds") or 0) // 60

        directors = []
        for section in data.get("principalCredits", []):
            if section.get("category", {}).get("id") == "director":
                for credit in section.get("credits", []):
                    name = (
                        credit.get("name", {}).get("nameText", {}).get("text")
                    )
                    if name:
                        directors.append(name)

        return {
            "imdb_id": imdb_id,
            "title": title,
            "budget": budget,
            "gross": gross,
            "runtime": runtime,
            "directors": directors,
        }

    def get_imdb(self, list_of_movies, list_of_fields):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies. Sort it by movieId descendingly.
        """
        imdb_info = []
        for movie_id in list_of_movies:
            imdb_id = self.id_map.get(movie_id)
            if not imdb_id:
                continue

            res = self._fetch_movie(imdb_id)
            if not res:
                continue

            main_director = res["directors"][0] if res["directors"] else "N/A"

            field_map = {
                "Director": main_director,
                "Budget": res["budget"],
                "Cumulative Worldwide Gross": res["gross"],
                "Runtime": res["runtime"],
            }

            row = [movie_id]
            for field in list_of_fields:
                row.append(field_map.get(field, "N/A"))

            imdb_info.append(row)
            self.movies_data.append(res)

        return sorted(imdb_info, key=lambda x: x[0], reverse=True)

    def top_directors(self, n):
        """
        The method returns a dict with top-n directors where the keys are directors and
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        counts = {}
        for m in self.movies_data:
            for d in m["directors"]:
                counts[d] = counts.get(d, 0) + 1
        return dict(
            sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
        )

    def most_expensive(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        """
        data = {m["title"]: m["budget"] for m in self.movies_data}
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
        Sort it by the difference descendingly.
        """
        sorted_movies = sorted(
            self.movies_data,
            key=lambda m: m["gross"] - m["budget"],
            reverse=True,
        )
        return {
            m["title"]: (m["gross"] - m["budget"]) for m in sorted_movies[:n]
        }

    def longest(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
        Sort it by runtime descendingly.
        """
        sorted_movies = sorted(
            self.movies_data, key=lambda x: x["runtime"], reverse=True
        )
        return {m["title"]: m["runtime"] for m in sorted_movies[:n]}

    def top_cost_per_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it.
        The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """
        costs = {}
        for m in self.movies_data:
            if m["runtime"] > 0:
                costs[m["title"]] = round(m["budget"] / m["runtime"], 2)
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n])


##############################################################


class Tests:
    """
    По ТЗ тесты должны проверять:
    что методы возвращают данные корректных типов;
    что элементы списков имеют корректные типы;
    что возвращаемые данные отсортированы корректно.
    Запуск: pytest movielens_analysis.py
    """

    # --------------------- вспомогательные функции ---------------------------
    def test_average(self):
        assert average([1, 2, 3, 4, 5]) == 3.0
        assert average([]) == 0
        assert isinstance(average([1, 2]), float)

    def test_median(self):
        assert median([1, 2, 3]) == 2
        assert median([1, 2, 3, 4]) == 2.5
        assert median([]) == 0

    def test_variance(self):
        assert round(variance([1, 2, 3]), 2) == 0.67  # 0.666..
        assert variance([]) == 0

    def test_get_year_from_ts(self):
        # 964981247 - это 2000 год
        assert get_year_from_ts(964981247) == 2000
        assert get_year_from_ts("invalid") is None

    # ---------------------------Movies ------------------------------------
    def test_movies_init(self):
        m = Movies("movies.csv")
        assert len(m.movies_list) > 0, "Данные не загружены"
        assert len(m.movies_list) <= 1000, (
            "Ограничение в 1000 строк не сработало"
        )
        assert "title" in m.movies_list[0], "Структура данных в init неверна"

    def test_dist_by_release(self):
        m = Movies("movies.csv")
        res = m.dist_by_release()
        assert isinstance(res, dict)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True), (
            "Сортировка по количеству релизов неверна"
        )

    def test_dist_by_genres(self):
        m = Movies("movies.csv")
        res = m.dist_by_genres()
        assert isinstance(res, dict)
        assert all(isinstance(k, str) for k in res.keys())
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True), (
            "Сортировка по жанрам неверна"
        )

    def test_most_genres(self):
        m = Movies("movies.csv")
        res = m.most_genres(5)
        assert len(res) <= 5
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True), (
            "Сортировка в most_genres неверна"
        )

    # --------------------- Ratings и влож.кл. ---------------------------
    def test_ratings_init(self):
        r = Ratings("ratings.csv")
        assert len(r.ratings_list) > 0
        assert isinstance(r.ratings_list[0]["rating"], float)

    def test_ratings_movies_logic(self):
        r = Ratings("ratings.csv")
        m = Movies("movies.csv")
        titles = {mv["movieId"]: mv["title"] for mv in m.movies_list}
        rm = Ratings.Movies(r.ratings_list, titles_dict=titles)
        dist_year = rm.dist_by_year()
        assert isinstance(dist_year, dict), "Должен вернуться словарь"
        keys = [k for k in dist_year.keys() if k is not None]
        assert keys == sorted(keys), "Года должны идти по возрастанию (ASC)"

    def test_ratings_users_logic(self):
        r = Ratings("ratings.csv")
        ru = Ratings.Users(r.ratings_list)
        dist_num = ru.dist_by_num_of_ratings()
        assert isinstance(dist_num, dict)

        top_cont = ru.top_controversial(5)
        assert isinstance(top_cont, dict)
        if top_cont:
            assert all(isinstance(k, str) for k in top_cont.keys())
            vals = list(top_cont.values())
            assert vals == sorted(vals, reverse=True), (
                "Сортировка дисперсии неверна"
            )

    # ------------------------------Tags -----------------------------------
    def test_tags_init(self):
        t = Tags("tags.csv")
        assert isinstance(t.tags_list, list), (
            "Атрибут tags_list должен быть списком"
        )
        if t.tags_list:
            assert isinstance(t.tags_list[0], str)

    def test_tags_most_words(self):
        t = Tags("tags.csv")
        res = t.most_words(3)
        assert isinstance(res, dict)
        for tag, count in res.items():
            assert isinstance(tag, str)
            assert isinstance(count, int)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_tags_longest(self):
        t = Tags("tags.csv")
        res = t.longest(3)
        assert isinstance(res, list)
        assert len(res) == len(set(res))
        assert res == sorted(res, key=len, reverse=True)

    def test_tags_most_popular(self):
        t = Tags("tags.csv")
        res = t.most_popular(3)
        assert isinstance(res, dict)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_tags_with(self):
        t = Tags("tags.csv")
        res = t.tags_with("love")
        assert isinstance(res, list)
        assert res == sorted(res)

    # ------------------------------ Links ---------------------------------

    def test_links_init(self):
        l = Links("links.csv")
        assert isinstance(l.id_map, dict), "id_map должен быть словарем"
        if l.id_map:
            val = list(l.id_map.values())[0]
            assert val.startswith("tt")

    def test_links_get_imdb(self):
        l = Links("links.csv")
        if l.id_map:
            m_id = list(l.id_map.keys())[0]
            res = l.get_imdb([m_id], ["Director", "Runtime"])
            assert isinstance(res, list)
            if res:
                assert res[0][0] == m_id
                assert len(res[0]) == 3  # ID + 2 поля

    def test_links_top_directors(self):
        l = Links("links.csv")
        m_id = list(l.id_map.keys())[0] if l.id_map else 1
        l.get_imdb([m_id], ["Director"])

        res = l.top_directors(3)
        assert isinstance(res, dict)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_links_most_expensive(self):
        l = Links("links.csv")
        movie_ids = list(l.id_map.keys())[:3] if l.id_map else []
        l.get_imdb(movie_ids, ["Budget"])

        res = l.most_expensive(3)
        assert isinstance(res, dict)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_links_most_profitable(self):
        l = Links("links.csv")
        movie_ids = list(l.id_map.keys())[:3] if l.id_map else []
        l.get_imdb(movie_ids, ["Budget", "Cumulative Worldwide Gross"])

        res = l.most_profitable(3)
        assert isinstance(res, dict)
        assert all(isinstance(v, (int, float)) for v in res.values())
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_links_longest(self):
        l = Links("links.csv")
        movie_ids = list(l.id_map.keys())[:3] if l.id_map else []
        l.get_imdb(movie_ids, ["Runtime"])

        res = l.longest(3)
        assert isinstance(res, dict)
        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_links_top_cost_per_minute(self):
        l = Links("links.csv")
        movie_ids = list(l.id_map.keys())[:3] if l.id_map else []
        l.get_imdb(movie_ids, ["Budget", "Runtime"])

        res = l.top_cost_per_minute(3)
        assert isinstance(res, dict)
        for val in res.values():
            assert isinstance(val, float)
            assert round(val, 2) == val

        vals = list(res.values())
        assert vals == sorted(vals, reverse=True)

    def test_links_fetch_movie(self):
        l = Links("links.csv")
        res = l._fetch_movie("tt0114709")

        if res is not None:
            assert isinstance(res, dict), (
                "Метод _fetch_movie должен возвращать словарь при успехе"
            )
            assert res["title"] == "Toy Story", "Название фильма не совпадает"
            assert isinstance(res["directors"], list), (
                "Поле directors должно быть списком"
            )
            assert isinstance(res["budget"], int)
            assert isinstance(res["runtime"], int)
        else:
            print("Предупреждение: API IMDb недоступно или нет интернета")
