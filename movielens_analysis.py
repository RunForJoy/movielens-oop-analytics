import re
from collections import Counter, OrderedDict
from enum import unique


class Links:
	"""
	Analyzing data from links.csv
	"""

	def __init__(self, path_to_the_file):
		"""
		Put here any fields that you think you will need.
		"""

	def get_imdb(list_of_movies, list_of_fields):
		"""
		The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
				For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
				The values should be parsed from the IMDB webpages of the movies.
			 Sort it by movieId descendingly.
		"""
		return imdb_info

	def top_directors(self, n):
		"""
		The method returns a dict with top-n directors where the keys are directors and
		the values are numbers of movies created by them. Sort it by numbers descendingly.
		"""
		return directors

	def most_expensive(self, n):
		"""
		The method returns a dict with top-n movies where the keys are movie titles and
		the values are their budgets. Sort it by budgets descendingly.
		"""
		return budgets

	def most_profitable(self, n):
		"""
		       The method returns a dict with top-n movies where the keys are movie titles and
		       the values are the difference between cumulative worldwide gross and budget.
		Sort it by the difference descendingly.
		"""
		return profits

	def longest(self, n):
		"""
		       The method returns a dict with top-n movies where the keys are movie titles and
		       the values are their runtime. If there are more than one version – choose any.
		Sort it by runtime descendingly.
		"""
		return runtimes

	def top_cost_per_minute(self, n):
		"""
				The method returns a dict with top-n movies where the keys are movie titles and
		the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it.
			 The values should be rounded to 2 decimals. Sort it by the division descendingly.
		"""
		return costs


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

	def __init__(self, path_to_the_file):
		"""
		Put here any fields that you think you will need.
		"""

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
