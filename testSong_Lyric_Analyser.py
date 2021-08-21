import unittest
from Song_Lyric_Analyser import MainWindow

class Test_testSong_Lyric_Analyser(unittest.TestCase):
    def test_calculate_list_average(self):
        self.assertAlmostEqual(MainWindow.calculate_list_average(self,[2,2,2,2]), 2)
        self.assertAlmostEqual(MainWindow.calculate_list_average(self,[1,1,1]), 1)
        self.assertAlmostEqual(MainWindow.calculate_list_average(self,None), 0)
        self.assertAlmostEqual(MainWindow.calculate_list_average(self,), 0)

if __name__ == '__main__':
    unittest.main()
