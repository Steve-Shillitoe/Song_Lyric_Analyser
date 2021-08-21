import unittest
from LyricFinder import LyricFinder


class Test_testLyricFinder(unittest.TestCase):
    def test_word_count(self):
        self.assertAlmostEqual(LyricFinder.word_count(self,"one two three 4"), 4)
        self.assertAlmostEqual(LyricFinder.word_count(self,None), 0)
        self.assertAlmostEqual(LyricFinder.word_count(self,), 0)
        self.assertAlmostEqual(LyricFinder.word_count(self,"one"), 1)
        self.assertAlmostEqual(LyricFinder.word_count(self,"o n e"), 3)


if __name__ == '__main__':
    unittest.main()
