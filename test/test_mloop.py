import unittest

from src.mloop import Mloop


class TestMloop(unittest.TestCase):

    @staticmethod
    def callback(itr, idx_array, arrays):
        for i in range(0, len(arrays)):
            print(idx_array[i], "->", arrays[i][int(idx_array[i])])

    def test__mloop(self):
        a1 = [1, 2, 3]
        a2 = [4, 5, 6, 7]
        a3 = [9, 10]

        ml = Mloop([a1, a2, a3], self.callback, "")
        print(ml.number_of_itr())
        ml.loop()
