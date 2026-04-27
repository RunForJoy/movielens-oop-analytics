import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from movielens_analysis import (
	IMDB_FIELDS,
	ImdbRequester,
	Links,
	Movies,
	Ratings,
	Tags,
	_avarage,
	_median,
	_split_line,
)


class TestMovies:
	def setup_class(self):
		self.mvs = Movies("test/datasets/movies.csv")

	def test_init(self):
		mvs = self.mvs
		assert len(mvs.data) == 7
		first = mvs.data[1]
		assert len(first.genres) == 2
		assert all(x in first.genres for x in ["Adventure", "Animation"])

	def test_dist_by_release(self):
		dist = self.mvs.dist_by_release()
		assert len(dist) == 4
		items = list(dist.items())
		assert items[0] == (1995, 3)
		assert items[1] == (1993, 2)

	def test_dist_by_genres(self):
		dist = self.mvs.dist_by_genres()
		assert len(dist) == 4
		items = list(dist.items())
		assert items[0] == ("Adventure", 3)
		assert items[1] == ("", 3)
		assert items[2] == ("rofl", 1)
		assert items[3] == ("Animation", 1)

	def test_most_genres(self):
		most = self.mvs.most_genres(2)
		assert len(most) == 2
		items = list(most.items())
		assert items[0][0] == "Toy Story (1995)"
		assert items[0][1] == 2

		most = self.mvs.most_genres(10)
		assert len(most) == 7
		items = list(most.items())
		assert items[0][0] == "Toy Story (1995)"
		assert items[0][1] == 2


class TestTags:
	def setup_class(self):
		self.tags = Tags("test/datasets/tags.csv")

	def test_init(self):
		t = self.tags
		assert len(t.data) == 6
		d = t.data[2]
		assert d.user_id == 2
		assert d.movie_id == 60756
		assert d.tag == "will ferrell"
		assert d.timestamp == 1445714992

	def test_most_words(self):
		most = self.tags.most_words(3)
		assert len(most) == 3
		items = list(most.items())
		assert items[0][0] == "Highly quotable"
		assert items[0][1] == 2

		most = self.tags.most_words(None)
		assert len(set(tag for tag in most)) == len(most)

	def test_longest(self):
		longest = self.tags.longest(3)
		assert len(longest) == 3
		assert len(longest[0]) == 15

		longest = self.tags.most_words(None)
		assert len(set(longest)) == len(longest)

	def test_most_words_and_longest(self):
		data = self.tags.most_words_and_longest(3)
		assert len(data) == 3
		assert sorted(data) == sorted(
			["Boxing story", "will ferrell", "Highly quotable"]
		)

		data = self.tags.most_words_and_longest(None)
		assert len(set(data)) == len(data)

	def test_most_popular(self):
		data = self.tags.most_popular(3)
		assert len(data) == 3
		items = list(data.items())
		assert items[0][0] == "Boxing story"
		assert items[0][1] == 2

		data = self.tags.most_popular(None)
		assert len(set(tag for tag in data)) == len(data)

	def test_tags_with(self):
		data = self.tags.tags_with("will")
		assert len(data) == 1
		assert data[0] == "will ferrell"

		data = self.tags.tags_with("story")
		assert len(set(data)) == len(data)


class TestLinks:
	def setup_class(self):
		self.links = Links("test/datasets/links.csv")

	def test_init(self):
		links = self.links
		assert len(links.data) == 4
		first: Links.Link = links.data[1]
		assert first.movie_id == 1
		assert first.imdb_id == "0114709"
		assert first.tmdb_id == 862

	def test_get_imdb(self):
		movies = [1, 3, 4]
		fields: list[IMDB_FIELDS] = [
			"Director",
			"Runtime",
			"Actors",
		]
		data = self.links.get_imdb(movies, fields)
		assert len(data) == 3

	def test_top_directors(self):
		data = self.links.top_directors(3)
		assert data == {
			"John Lasseter": 1,
			"Joe Johnston": 1,
			"Howard Deutch": 1,
		}
		assert data["John Lasseter"] == 1

	def test_most_expensive(self):
		data = self.links.most_expensive(3)
		assert len(data) == 3
		items = list(data.values())
		assert items[0] >= items[1]

	def test_most_profitable(self):
		data = self.links.most_profitable(3)
		assert len(data) == 3
		items = list(data.values())
		assert items[0] >= items[1]

	def test_longest(self):
		data = self.links.longest(3)
		assert len(data) == 3
		items = list(data.values())
		assert items[0] >= items[1]

	def test_top_cost_per_minute(self):
		data = self.links.top_cost_per_minute(3)
		assert len(data) == 3
		items = list(data.values())
		assert items[0] >= items[1]


class TestRatings:
	def setup_class(self):
		self.ratings = Ratings("test/datasets/ratings.csv")

	def test_init(self):
		data = self.ratings.data
		assert len(data) == 4
		f = data[1]
		assert f.user_id == 1
		assert f.movie_id == 3
		assert f.rating == 4.0
		assert f.timestamp == 964981247

	class TestMovies:
		def setup_class(self):
			self.movies = Ratings.Movies(
				Ratings("test/datasets/ratings.csv"),
				Movies("test/datasets/movies.csv"),
			)

		def test_dist_by_years(self):
			data = self.movies.dist_by_year()
			assert len(data) == 1
			assert data[2000] == 4

		def test_dist_by_rating(self):
			data = self.movies.dist_by_rating()
			assert len(data) == 2
			assert data == {5.0: 1, 4.0: 3}

		def test_top_by_num_of_ratings(self):
			data = self.movies.top_by_num_of_ratings(3)
			assert len(data) == 3
			assert data == {
				"Toy Story (1995)": 1,
				"Grumpier Old Men (1995)": 1,
				"Movie 6 (2006)": 1,
			}
			items = list(data.items())
			assert items == [
				("Toy Story (1995)", 1),
				("Grumpier Old Men (1995)", 1),
				("Movie 6 (2006)", 1),
			]

		def test_top_ratings(self):
			data = self.movies.top_by_ratings(3)
			assert data == {
				"Movie 47 (2047)": 5.0,
				"Toy Story (1995)": 4.0,
				"Grumpier Old Men (1995)": 4.0,
			}
			items = list(data.items())
			assert items[0][1] >= items[1][1]

		def test_top_controversial(self):
			data = self.movies.top_controversial(3)
			assert len(data) == 3
			items = list(data.items())
			assert items[0][1] >= items[1][1]


def test_split_line():
	line = '4,"Foo, Bar, Biz (1993)",Adventure'
	res = _split_line(line)
	assert isinstance(res, tuple)
	assert len(res) == 3
	assert res[1] == "Foo, Bar, Biz (1993)"

	line = "2,Jumanji (1995),Adventure|Children|Fantasy"
	res = _split_line(line)
	assert isinstance(res, tuple)
	assert len(res) == 3


class TestImdbRequester:
	def setup_class(self):
		self.imdb = ImdbRequester()

	def test_init(self):
		pass

	def test_request(self):
		data = self.imdb.request("0114709")
		expt_data = {
			"Title": "Toy Story",
			"Year": "1995",
			"Rated": "G",
			"Released": "22 Nov 1995",
			"Runtime": "81 min",
			"Genre": "Animation, Adventure, Comedy",
			"Director": "John Lasseter",
			"Writer": "Joss Whedon, Andrew Stanton, Joel Cohen",
			"Actors": "Tom Hanks, Tim Allen, Don Rickles",
			"Plot": "A cowboy doll is profoundly jealous when a new spaceman action figure supplants him as the top toy in a boy's bedroom. When circumstances separate them from their owner, the duo have to put aside their differences to return to him.",
			"Language": "English",
			"Country": "United States",
			"Awards": "Nominated for 3 Oscars. 29 wins & 24 nominations total",
			"Poster": "https://m.media-amazon.com/images/M/MV5BZTA3OWVjOWItNjE1NS00NzZiLWE1MjgtZDZhMWI1ZTlkNzYwXkEyXkFqcGc@._V1_SX300.jpg",
			"Ratings": [
				{"Source": "Internet Movie Database", "Value": "8.3/10"},
				{"Source": "Rotten Tomatoes", "Value": "100%"},
				{"Source": "Metacritic", "Value": "96/100"},
			],
			"Metascore": "96",
			"imdbRating": "8.3",
			"imdbVotes": "1,163,069",
			"imdbID": "tt0114709",
			"Type": "movie",
			"DVD": "N/A",
			"BoxOffice": "$229,947,062",
			"Production": "N/A",
			"Website": "N/A",
			"Response": "True",
		}
		assert expt_data == data


def test_median():
	mid = _median([1, 2, 3])
	assert mid == 2

	mid = _median([1, 2, 3, 4])
	assert mid == 2.5

	mid = _median([0.026])
	assert mid == 0.03


def test_avarage():
	av = _avarage([1, 2, 3])
	assert av == 2

	av = _avarage([0.026])
	assert av == 0.03
