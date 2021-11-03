import numpy
import unittest
import time
import pandas


class TestPool(unittest.TestCase):

    def test__pool(self):
        a = numpy.arange(0, 100, 1)
        portions = 5
        for i in range(0, len(a), portions):
            for j in range(i, i + portions):
                print a[j]
            print "--------------------------------------"
            time.sleep(2)


    def test__quick(self):
        s = pandas.Series()
        s["0"] = 0
        s["1"] = 1
        s["2"] = 2

        for i,v in s.iteritems():
            print i, "->", str(v)





