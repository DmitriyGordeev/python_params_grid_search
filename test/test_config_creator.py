import unittest

from src.config_creator import ConfigCreator


class TestConfigCreator(unittest.TestCase):
    def test__create_config(self):
        configs_out = "./"
        pattern_path = "./template.xml"
        cc = ConfigCreator(pattern_path=pattern_path,
                           configs_out_dir=configs_out)
        print(cc.create_config([11, 0.0145, 1500, 153], 0, "test"))
