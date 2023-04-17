import re
import unittest

from src.varparser import VarParser


class TestVarparser(unittest.TestCase):
    def test_parse(self):
        vp = VarParser()
        linspace_example = "{{edge, 1000, 2000, 100}}"
        enum_example = "blablabla [[ var : 1020, 1029.9]]dawdawd"

        core_linspace = re.findall("{{\s*[a-zA-Z_0-9-]+\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*}}",
                                   linspace_example)
        core_enum = re.findall("\[\[\s*[0-9A-Za-z_]+\s*:\s*[\s0-9.,-]+\s*\]\]", enum_example)
        print(vp.parse_linspace(core_linspace))
