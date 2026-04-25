import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from movielens_analysis import Movies, _split_line


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
