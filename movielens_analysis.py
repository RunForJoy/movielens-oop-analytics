import json
import os
import re
from collections import Counter, OrderedDict
from typing import Literal

import requests

IMDB_FIELDS = Literal[
	"Actors",
	"Awards",
	"BoxOffice",
	"Country",
	"DVD",
	"Director",
	"Genre",
	"Language",
	"Metascore",
	"Plot",
	"Poster",
	"Production",
	"Rated",
	"Ratings",
	"Released",
	"Response",
	"Runtime",
	"Title",
	"Type",
	"Website",
	"Writer",
	"Year",
	"imdbID",
	"imdbRating",
	"imdbVotes",
]


class ImdbRequester:
	DIR: str = f"/home/{os.environ['USER']}/.cache/q_imdb"

	def __init__(self):
		try:
			os.makedirs(self.DIR)
		except FileExistsError:
			pass

	def request(self, movie_id: str) -> dict[IMDB_FIELDS, str]:
		movie_cache_path = os.path.join(self.DIR, movie_id)
		if os.path.exists(movie_cache_path):
			with open(movie_cache_path, "r") as f:
				return json.load(f)
		params = {
			"apikey": os.environ["OMDB_API_KEY"],
			"i": f"tt{movie_id}",
		}
		response = requests.get("https://www.omdbapi.com", params=params)
		response.raise_for_status()
		with open(movie_cache_path, "w") as f:
			f.write(response.text)
		return response.json()


class Links:
	"""
	Analyzing data from links.csv
	"""

	class Link:
		movie_id: int
		imdb_id: str
		tmdb_id: int

		def __init__(self, movie_id: int, imdb_id: str, tmdb_id: int):
			self.movie_id = movie_id
			self.imdb_id = imdb_id
			self.tmdb_id = tmdb_id

	data: dict[int, Link] = {}
	reqr = ImdbRequester()

	def __init__(self, path_to_the_file: str):
		# movieId,imdbId,tmdbId
		with open(path_to_the_file, "r") as f:
			f.readline()
			for line in f:
				mid, iid, tid = _split_line(line.strip())
				mid = int(mid)
				self.data[mid] = Links.Link(mid, iid, int(tid))

	def get_imdb(
		self, list_of_movies: list[int], list_of_fields: list[IMDB_FIELDS]
	) -> list[list[str]]:
		res: list[list[str]] = []
		list_of_movies = sorted(list_of_movies, reverse=True)
		for movie_id in list_of_movies:
			if movie_id not in self.data:
				raise ValueError(f"movie with id({movie_id}) is undefined")
		for movie_id in list_of_movies:
			response = self.reqr.request(self.data[movie_id].imdb_id)
			movie = [movie_id, *[response[key] for key in list_of_fields]]
			res.append(movie)
		return res

	def top_directors(self, n: int | None) -> dict[str, int]:
		counter = Counter(
			self.reqr.request(movie.imdb_id)["Director"]
			for movie in self.data.values()
		)
		return OrderedDict(counter.most_common(n))

	def most_expensive(self, n: int | None) -> dict[str, int]:
		most_expensive = []
		for movie in self.data.values():
			data = self.reqr.request(movie.imdb_id)
			most_expensive.append(
				(data["Title"], 0)
			)  # omdb not supports budget
		most_expensive.sort(key=lambda cell: cell[1], reverse=True)
		return OrderedDict(most_expensive[:n])

	def most_profitable(self, n: int | None) -> dict[str, int]:
		most_profitable = []
		for movie in self.data.values():
			data = self.reqr.request(movie.imdb_id)
			most_profitable.append(
				(data["Title"], int(data["BoxOffice"][1:].replace(",", "")) - 0)
			)  # omdb not supports budget
		most_profitable.sort(key=lambda cell: cell[1], reverse=True)
		return OrderedDict(most_profitable[:n])

	def longest(self, n: int | None) -> dict[str, int]:
		longest = []
		for movie in self.data.values():
			data = self.reqr.request(movie.imdb_id)
			longest.append((data["Title"], int(data["Runtime"][:-4])))
		longest.sort(key=lambda cell: cell[1], reverse=True)
		return OrderedDict(longest[:n])

	def top_cost_per_minute(self, n: int) -> dict[str, float]:
		"""
		The method returns a dict with top-n movies where the keys are movie titles and
		the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it.
		The values should be rounded to 2 decimals. Sort it by the division descendingly.
		"""
		cpm = []
		for movie in self.data.values():
			data = self.reqr.request(movie.imdb_id)
			cpm.append(
				(data["Title"], 0 / int(data["Runtime"][:-4]))
			)  # omdb not supports budget
		cpm.sort(key=lambda cell: cell[1], reverse=True)
		return OrderedDict(cpm[:n])


class Movies:
	"""
	Analyzing data from movies.csv
	"""

	class Movie:
		id: int
		title: str
		genres: list[str] = []

		def __init__(self, id: int, title: str, genres: list[str]):
			self.id = id
			self.title = title
			self.genres = genres

	data: dict[int, Movie] = {}

	def __init__(self, path_to_the_file: str):
		with open(path_to_the_file, "r") as f:
			f.readline()
			for line in f:
				id_str, name, genres_str = _split_line(line.strip())
				id = int(id_str)
				self.data[id] = Movies.Movie(id, name, genres_str.split("|"))

	def dist_by_release(self) -> dict[int, int]:
		pattern = re.compile(r"\((\d{4})\)")
		counter = Counter(
			int(pattern.findall(movie.title)[-1])
			for movie in self.data.values()
		)
		return OrderedDict(counter.most_common())

	def dist_by_genres(self):
		counter = Counter(g for m in self.data.values() for g in m.genres)
		return OrderedDict(counter.most_common())

	def most_genres(self, n: int | None):
		counter = Counter(
			{movie.title: len(movie.genres) for movie in self.data.values()}
		)
		return OrderedDict(counter.most_common(n))


class Tags:
	"""
	Analyzing data from tags.csv
	"""

	class Tag:
		user_id: int
		movie_id: int
		tag: str
		timestamp: int

		def __init__(
			self, user_id: int, movie_id: int, tag: str, timestamp: int
		):
			self.user_id = user_id
			self.movie_id = movie_id
			self.tag = tag
			self.timestamp = timestamp

	data: list[Tag] = []

	def __init__(self, path_to_the_file: str):
		with open(path_to_the_file, "r") as f:
			f.readline()
			for line in f:
				uid, mid, tag, timestamp = _split_line(line.strip())
				self.data.append(
					Tags.Tag(int(uid), int(mid), tag, int(timestamp))
				)

	def most_words(self, n: int | None) -> dict[str, int]:
		counter = Counter({tag.tag: len(tag.tag.split()) for tag in self.data})
		return OrderedDict(counter.most_common(n))

	def longest(self, n: int | None) -> list[str]:
		return sorted(
			(tag for tag in set(tag.tag for tag in self.data)),
			key=lambda val: len(val),
			reverse=True,
		)[:n]

	def most_words_and_longest(self, n: int | None) -> list[str]:
		return list(
			set(set(tag for tag in self.most_words(n))) & set(self.longest(n))
		)

	def most_popular(self, n: int | None) -> dict[str, int]:
		counter = Counter(tag.tag for tag in self.data)
		return OrderedDict(counter.most_common(n))

	def tags_with(self, word: str) -> list[str]:
		return list(
			set(tag.tag for tag in self.data if word in tag.tag.split())
		)


class Ratings:
	"""
	Analyzing data from ratings.csv
	"""

	class Rating:
		user_id: int
		movie_id: int
		rating: float
		timestamp: int

		def __init__(
			self, user_id: int, movie_id: int, rating: float, timestamp: int
		):
			self.user_id = user_id
			self.movie_id = movie_id
			self.rating = rating
			self.timestamp = timestamp

	data: list[Rating] = []

	def __init__(self, path_to_the_file):
		with open(path_to_the_file, "r") as f:
			f.readline()
			for line in f:
				uid, mid, rating, timestamp = _split_line(line.strip())
				self.data.append(
					Ratings.Rating(
						int(uid), int(mid), float(rating), int(timestamp)
					)
				)

	class Movies:
		def dist_by_year(self):
			"""
			The method returns a dict where the keys are years and the values are counts.
			Sort it by years ascendingly. You need to extract years from timestamps.
			"""
			return ratings_by_year

		def dist_by_rating(self):
			"""
			The method returns a dict where the keys are ratings and the values are counts.
			Sort it by ratings ascendingly.
			"""
			return ratings_distribution

		def top_by_num_of_ratings(self, n):
			"""
			The method returns top-n movies by the number of ratings.
			It is a dict where the keys are movie titles and the values are numbers.
			Sort it by numbers descendingly.
			"""
			return top_movies

		# def top_by_ratings(self, n, metric=average):
		def top_by_ratings(self, n, metric):
			"""
			The method returns top-n movies by the average or median of the ratings.
			It is a dict where the keys are movie titles and the values are metric values.
			Sort it by metric descendingly.
			The values should be rounded to 2 decimals.
			"""
			return top_movies

		def top_controversial(self, n):
			"""
			The method returns top-n movies by the variance of the ratings.
			It is a dict where the keys are movie titles and the values are the variances.
			Sort it by variance descendingly.
			The values should be rounded to 2 decimals.
			"""
			return top_movies

	class Users:
		"""
		In this class, three methods should work.
		The 1st returns the distribution of users by the number of ratings made by them.
		The 2nd returns the distribution of users by average or median ratings made by them.
		The 3rd returns top-n users with the biggest variance of their ratings.
		Inherit from the class Movies. Several methods are similar to the methods from it.
		"""


def _split_line(line: str) -> tuple[str, ...]:
	res: list[str] = []
	merge: list[str] = []
	for col in line.split(","):
		start = col.startswith('"')
		end = col.endswith('"')

		if (start and end) or (len(merge) == 0 and not start):
			res.append(col.strip('"'))
		elif end:
			merge.append(col)
			res.append(",".join(merge).strip('"'))
			merge = []
		else:
			merge.append(col)
	return (*res,)
