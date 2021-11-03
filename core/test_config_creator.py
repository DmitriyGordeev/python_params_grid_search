import config_creator
import unittest


class TestConfigCreator(unittest.TestCase):

    def test__create_config(self):

        configs_out = "/home/dima/Projects/PyCharmProjects/Grid/example_templates/"
        pattern_path = "/home/dima/Projects/PyCharmProjects/Grid/example_templates/template.xml"

        cc = config_creator.ConfigCreator(pattern_path=pattern_path,
                                          configs_out_dir=configs_out)

        print cc.create_config([11, 0.0145, 1500, 153], 0, "test")


