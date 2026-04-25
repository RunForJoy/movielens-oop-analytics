import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from movielens_analysis import Movies, Tags, _split_line


class TestMovies:
	def setup_class(self):
		self.mvs = Movies("test/datasets/movies.csv")

	def test_init(self):
		mvs = self.mvs
		assert len(mvs.data) == 5
		first = mvs.data[1]
		assert len(first.genres) == 2
		assert all(x in first.genres for x in ["Adventure", "Animation"])

	def test_dist_by_release(self):
		dist = self.mvs.dist_by_release()
		assert len(dist) == 2
		items = list(dist.items())
		assert items[0] == (1995, 3)
		assert items[1] == (1993, 2)

	def test_dist_by_genres(self):
		dist = self.mvs.dist_by_genres()
		assert len(dist) == 4
		items = list(dist.items())
		assert items[0] == ("Adventure", 3)
		assert items[1] == ("rofl", 1)
		assert items[2] == ("Animation", 1)
		assert items[3] == ("", 1)

	def test_most_genres(self):
		most = self.mvs.most_genres(2)
		assert len(most) == 2
		items = list(most.items())
		assert items[0][0] == "Toy Story (1995)"
		assert items[0][1] == 2

		most = self.mvs.most_genres(6)
		assert len(most) == 5
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
