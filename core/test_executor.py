import unittest
import executor


class TestExecutor(unittest.TestCase):

    def test__execute(self):

        ex = executor.Executor(
            pattern_path="/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/example_templates/template.xml",
            configs_out_dir="/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/example_templates/",
            news_min_after=0,
            news_min_before=0,
            rollover_rules="",
            whitelist_file="whitelist.txt",
            blacklist_file="blacklist.txt",
            timelimit=400)

        ex.execute("someexe.py", "strategy_logs_dir", "config", "20191101+10", "20")


    def test__parse_info_json(self):

        ex = executor.Executor(
            pattern_path="/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/example_templates/template.xml",
            configs_out_dir="/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/example_templates/",
            news_min_after=0,
            news_min_before=0,
            rollover_rules="",
            whitelist_file="whitelist.txt",
            blacklist_file="blacklist.txt",
            timelimit=400)

        results = ex.parse_info_json("/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/info_examples/stats_opt.json", 1)
        print results