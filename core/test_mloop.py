import unittest
import mloop

class TestMloop(unittest.TestCase):

    @staticmethod
    def callback(itr, idx_array, arrays):
        for i in range(0, len(arrays)):
            print idx_array[i], "->", arrays[i][int(idx_array[i])]
        print "-----------------------------"

    def test__mloop(self):
        a1 = [1, 2, 3]
        a2 = [4, 5, 6, 7]
        a3 = [9, 10]

        ml = mloop.Mloop([a1, a2, a3], self.callback)
        print ml.number_of_itr()

        ml.loop()


