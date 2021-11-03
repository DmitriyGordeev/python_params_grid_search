import gridutils
import unittest

class TestGridUtils(unittest.TestCase):

    def test__define_grid(self):
        v1 = {"name": "edge", "min": 100, "max": 200, "step": 26, "type": "S"}
        v2 = {"name": "edge", "values": [110, 156, 89], "type": "E"}

        print gridutils.define_grid([v1, v2])