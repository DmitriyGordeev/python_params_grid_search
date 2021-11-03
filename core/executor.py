import pandas
import logging
import json
import config_creator
import os
import subprocess
import glob
import ntpath


class MetricsObject:
    def __init__(self, leg_name, json_dict):
        self.leg_name = leg_name
        self.json_dict = json_dict


class Executor:
    def __init__(self,
                 pattern_path,
                 configs_out_dir,
                 news_min_before,
                 news_min_after,
                 # rollover_rules,
                 whitelist_file,
                 blacklist_file,
                 timelimit,
                 parts):
        self.config_creator = config_creator.ConfigCreator(pattern_path, configs_out_dir)
        self.news_min_before = news_min_before
        self.news_min_after = news_min_after
        # self.rollover_rules = rollover_rules
        self.whitelist_file = whitelist_file
        self.blacklist_file = blacklist_file
        self.timelimit = timelimit
        self.parts = parts
        self.FNULL = open(os.devnull, 'w')

        self.leg_names = set()

        # param_columns = self.config_creator.params_table.columns.tolist()
        # self.results_table = pandas.DataFrame(columns=param_columns)  # empty dataframe to store results for each iteration at the end
        # self.current_results = pandas.Series()


    def create_config(self, x, number_of_itr, suffix, write_config=True):
        return self.config_creator.create_config(x, number_of_itr, suffix, write_config)


    def execute(self,
                executable_path,
                strategy_logs_dir,
                config_path,
                daterange,
                score,
                stdout_log_path):

        stdout_log_file = open(stdout_log_path, "w")

        # rollover_rules = self.rollover_rules
        # if self.rollover_rules is "":
        #     rollover_rules = "\'\'"

        argument_list = ['python',
                         executable_path,
                         '-c', config_path,
                         '--before', str(self.news_min_before),
                         '--after', str(self.news_min_after),
                         # '-e', rollover_rules,
                         '--log_dir', strategy_logs_dir,
                         '-tl', str(self.timelimit),
                         '--score', str(score),
                         '--parts', str(self.parts),
                         '-np']

        if daterange != "":
            argument_list = argument_list + ['-d', str(daterange)]
        if self.whitelist_file != "":
            argument_list = argument_list + ['-wl', str(self.whitelist_file)]
        if self.blacklist_file != "":
            argument_list = argument_list + ['-bl', str(self.blacklist_file)]

        return subprocess.Popen(argument_list,
                         close_fds=True,
                         stdout=stdout_log_file,
                         stderr=subprocess.STDOUT)


    def parse_info_json(self, location):

        leg_result_dict = dict()

        metrics_obj_array = self.collect_info_files(location)

        for mo in metrics_obj_array:

            current_results = dict()

            # parse info.json and log every metric:
            logging.info(mo.leg_name + "Days = " + str(mo.json_dict["days"]))

            # Pnl
            p = float(mo.json_dict["pnl"])
            logging.info(mo.leg_name + "pnl = " + str(p))

            # Sharpe ratio
            s = float(mo.json_dict["sharpe"])
            logging.info(mo.leg_name + "sharpe = " + str(s))

            # Sharpe (median):
            sm = float(mo.json_dict["sharpe_median"])
            logging.info(mo.leg_name + "sharpe_median = " + str(sm))

            # Sortino ratio
            sor = float(mo.json_dict["sortino"])
            logging.info(mo.leg_name + "sortino = " + str(sor))

            # Sortino (median)
            som = float(mo.json_dict["sortino_median"])
            logging.info(mo.leg_name + "sortino_median = " + str(som))

            # Positive days:
            pos = float(mo.json_dict["positive_days"])

            # Negative days:
            neg = float(mo.json_dict["negative_days"])

            # Days ratio
            pn = float(pos) / float(neg + 1)
            pninfo = "positive_days = " + str(pos) + \
                     ", negative_days = " + str(neg) + ", pos / (neg + 1) = " + str(pn)
            logging.info(pninfo)

            # Zero days
            zd = int(mo.json_dict["zero_days"])
            logging.info(mo.leg_name + "zero_days = " + str(zd))

            # Average daily pnl
            a = float(mo.json_dict["avg_pnl"])
            logging.info(mo.leg_name + "average_daily_pnl = " + str(a))

            # Median daily pnl
            med = float(mo.json_dict["median_pnl"])
            logging.info(mo.leg_name + "median_daily_pnl = " + str(med))

            # Min daily pnl
            m = float(mo.json_dict["min_pnl"])
            logging.info(mo.leg_name + "min_daily_pnl = " + str(m))

            # Std(daily pnl):
            stdp = float(mo.json_dict["std_pnl"])
            logging.info(mo.leg_name + "std daily pnl = " + str(stdp))

            # Max drawdown
            mdd = float(mo.json_dict["max_drawdown"])
            logging.info(mo.leg_name + "mdd = " + str(mdd))

            # Calmar ratio
            calmar = float(mo.json_dict["calmar"])
            logging.info(mo.leg_name + "calmar = " + str(calmar))

            # LSE slope:
            slope = float(mo.json_dict["slope"])
            logging.info(mo.leg_name + "slope = " + str(slope))

            # LSE fitting error:
            fe = float(mo.json_dict["fitting_error"])
            logging.info(mo.leg_name + "fitting_error = " + str(fe))

            # ==============================================================================================================
            if mo.leg_name != "global__":

                # Market share
                msh = float(mo.json_dict["market_share"])
                logging.info(mo.leg_name + "market_share = " + str(msh))

                # Average turnover
                t = float(mo.json_dict["avg_daily_turnover"])
                logging.info(mo.leg_name + "average_daily_volume = " + str(t))

                # Score ratio
                sc = float(mo.json_dict["avg_daily_score"])
                logging.info(mo.leg_name + "average_daily_score = " + str(sc))

                # Confidence interval
                ci = float(mo.json_dict["confidence_interval"])
                logging.info(mo.leg_name + "confidence_interval = " + str(ci))

                # Average holding time (average across all the days)
                aht = float(mo.json_dict["average_daily_holding_time"])
                logging.info(mo.leg_name + "average_daily_holding_time = " + str(aht))

                # Average holding time (median)
                mht = float(mo.json_dict["median_daily_holding_time"])
                logging.info(mo.leg_name + "median_daily_holding_time = " + str(mht))

                # avg intraday pnl slope (with log_level 3 only)
                aps = float(mo.json_dict["intraday_mean_pnl_slope"])
                logging.info(
                    mo.leg_name + "intraday_mean_pnl_slope = " + str(aps) + " (run with --short to make it non zero)")

                # avg intraday pnl fitting error (with log_level 3 only)
                apfe = float(mo.json_dict["intraday_mean_pnl_fe"])
                logging.info(
                    mo.leg_name + "intraday_mean_pnl_fe = " + str(apfe) + " (run with --short to make it non zero)")

                # Daily trading cycles (with log_level 3 only)
                if "daily_trading_cycles" in mo.json_dict:
                    dtc = float(mo.json_dict["daily_trading_cycles"])
                    logging.info(
                        mo.leg_name + "daily_trading_cycles = " + str(dtc) + " (run with --short to make it non zero)")
                else:
                    logging.info(mo.leg_name + "daily_trading_cycles = 0 (run with --short to make it non zero)")

                # Total trading cycles (with log_level 3 only)
                if "total_trading_cycles" in mo.json_dict:
                    ttc = float(mo.json_dict["total_trading_cycles"])
                    logging.info(
                        mo.leg_name + "total_trading_cycles = " + str(ttc) + " (run with --short to make it non zero)")
                else:
                    logging.info(mo.leg_name + "total_trading_cycles = 0 (run with --short to make it non zero)")


            # Copy every metrics into current_result series:
            for key, value in mo.json_dict.iteritems():
                current_results[key] = value

            # Adding filled current_result series to leg_results_dict:
            leg_result_dict[mo.leg_name] = current_results

        return leg_result_dict




    def get_lowers(self):
        return self.config_creator.get_lowers()


    def get_uppers(self):
        return self.config_creator.get_uppers()


    def get_types(self):
        return self.config_creator.get_types()


    def get_params_table(self):
        return self.config_creator.get_params_table()


    def collect_info_files(self, location):
        info_files = glob.glob(location + "/*info.json")

        if len(info_files) == 0:
            return []
        else:
            metric_obj_array = []
            for info_file in info_files:
                f = open(info_file, "r")
                json_dict = json.loads(f.read())
                f.close()

                info_file_basename = ntpath.basename(info_file)
                leg_name = info_file_basename.replace("info.json", "")
                leg_name = leg_name.replace(".", "__")
                self.leg_names.add(leg_name)
                print "[D]: leg_name =", leg_name
                mo = MetricsObject(leg_name, json_dict)
                metric_obj_array.append(mo)
            return metric_obj_array


