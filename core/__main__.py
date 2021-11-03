import logging
import datetime
import numpy
import mloop
import executor
import os
import gridutils
import arguments
import json
import time
import pandas
import glob
import ntpath


def core_fn(Itr_, iArr_, grid_arrays, write_config):
    """
    Creates configs for each iteration
    """
    # Define current config params
    x = []
    for idx, val in enumerate(iArr_):
        x.append(grid_arrays[int(idx)][int(val)])
    return executor.create_config(x, Itr_, str(Itr_), write_config)


if __name__ == "__main__":

    # Script abs directory:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir.replace("grid.zip", "")
    print "Script location =", script_dir

    configs_out_dir = script_dir + "/configs"
    itr_logs_dir = script_dir + "/logs"
    iterations_dir = script_dir + "/iterations"

    # Create necessary dirs if not exist yet:
    os.system("mkdir -p " + configs_out_dir)
    os.system("mkdir -p " + itr_logs_dir)
    os.system("mkdir -p " + iterations_dir)

    # Arguments:
    args, common = arguments.arguments().parse_known_args()

    # dot accessing to dict accessing
    args = vars(args)

    start_from_itr = 0

    # Writing down argument in a json file (in start mode)
    if not args["resume"]:
        if args["pattern"] == "":
            print "arguement: --pattern (or -p) is required"
            exit(1)

        args_to_write = args.copy()
        del args_to_write["resume"]

        f_json_args = open(script_dir + "/args.json", "w")
        f_json_args.write(json.dumps(args_to_write, indent=4))
        f_json_args.close()

        # Copying pattern file to configs:
        os.system("cp " + args["pattern"] + " " + configs_out_dir)
    else:
        # continue mode:
        f_json_args = open(script_dir + "/args.json", "r")
        args = json.loads(f_json_args.read())
        f_json_args.close()
        start_from_itr = args["last_itr"]
        args["resume"] = True
        # rename logs of the itr paused earlier:
        os.system("mv " + itr_logs_dir + "/logs-" + str(start_from_itr) + " " + itr_logs_dir + "/paused-logs-" + str(
            start_from_itr))
        print "\n[debug]: args in 'resume' mode:"
        print json.dumps(args, indent=4)
        print "\n"

    # grid settings:
    f = open(script_dir + "/settings.json", "r")
    contents = f.read()
    f.close()
    settings = json.loads(contents)

    executor = executor.Executor(pattern_path=args["pattern"],
                                 configs_out_dir=configs_out_dir,
                                 news_min_before=args["before"],
                                 news_min_after=args["after"],
                                 # rollover_rules=args["e"],
                                 whitelist_file=args["whitelist"],
                                 blacklist_file=args["blacklist"],
                                 timelimit=args["timelimit"],
                                 parts=args["parts"])

    grid = gridutils.define_grid(executor.config_creator.vars)
    mloop = mloop.Mloop(grid, core_fn, write_config=(not args["resume"]))

    logging.basicConfig(filename=settings["grid_log_file"], level=logging.INFO)

    if not args["resume"]:
        # Logging settings:
        if args["dates"] is "" and args["whitelist"] is not "":
            logging.info("Daterange: " + args["whitelist"])
        else:
            logging.info("Daterange: " + args["dates"])
        # logging.info("Rollover rules: " + args["e"])
        logging.info("News before: " + str(args["before"]) + "min")
        logging.info("News after: " + str(args["after"]) + "min")
        logging.info("Blacklist file: " + args["blacklist"])
        logging.info("Number of iterations = " + str(mloop.number_of_itr()))
        logging.info("==================================================================")

    # Main loop:
    # loop() will generate configs with all the possible parameters combinations
    mloop.loop()
    params_and_configs = mloop.params_and_configs
    leg_results_dict = []

    if args["resume"]:
        print "Resuming grid. itr = " + str(start_from_itr) + " / " + str(len(params_and_configs))
    else:
        print "Iterations = ", mloop.number_of_itr()

    # executions:
    subprocess_number = args["sub_num"]
    if subprocess_number < 1:
        subprocess_number = 1

    number_of_running = 0
    process_pool_map = dict()

    # this is needed to meausure time of each subprocess
    process_time_map = dict()

    # Starting simulations:
    for i in range(start_from_itr, len(params_and_configs)):
        print "starting:", params_and_configs[i][1]
        process = executor.execute(executable_path=settings["executable"],
                                   strategy_logs_dir=itr_logs_dir + "/logs-" + str(i),
                                   config_path=params_and_configs[i][1],
                                   daterange=args["dates"],
                                   score=args["score"],
                                   stdout_log_path=script_dir + "/stdout." + str(i) + ".log")

        # overwriting "last_run" field in args.json:
        f_json_args = open(script_dir + "/args.json", "r")
        args_in_file = json.loads(f_json_args.read())
        f_json_args.close()
        args_in_file["last_itr"] = i
        f_json_args = open(script_dir + "/args.json", "w")
        f_json_args.write(json.dumps(args_in_file, indent=4))
        f_json_args.close()

        # todo: refactor this bulky structure:
        process_pool_map[process] = (i, params_and_configs[i])
        process_time_map[process] = time.time()  # just put current time as a start time
        number_of_running = number_of_running + 1

        end_flag = (i == len(params_and_configs) - 1 and bool(process_pool_map))

        # Waiting while some process in the pool will have finished before starting next:
        while number_of_running >= subprocess_number or end_flag:
            # updating status of all the processes
            if i == len(params_and_configs) - 1:
                end_flag = True
                if not process_pool_map:
                    break

            for p, v in process_pool_map.items():
                # poll() is not None = process finished
                if p.poll() is not None:

                    # Calculating time taken by the process
                    time_taken = time.time() - process_time_map[p]

                    logging.info("------------------------------------------------------------------")
                    logging.info("Iteration = " + str(v[0]) + " / " + str(mloop.number_of_itr() - 1))

                    # Logging variables which have been generated for the current iteration:
                    logging.info("Params:")
                    for param_name, param_value in v[1][0].iteritems():
                        logging.info("\t" + param_name + " = " + str(param_value))

                    json_object_params = json.loads(v[1][0].to_json())

                    logging.info("Results:")
                    leg_results_dict = executor.parse_info_json(
                        itr_logs_dir + "/logs-" + str(v[0]) + "/")

                    # json_object_results = json.loads(leg_results_dict.to_json())

                    # writing iteration json :
                    # TODO: create N different jsons with own leg-name

                    for leg_name, lr_item in leg_results_dict.iteritems():
                        iteration_info_json = dict()
                        iteration_info_json["params"] = json_object_params
                        iteration_info_json["results"] = lr_item
                        iteration_info = json.dumps(iteration_info_json, indent=4)
                        file_itr = open(iterations_dir + "/" + str(v[0]) + "." + leg_name + ".json", "w")
                        file_itr.write(iteration_info)
                        file_itr.close()

                    # iteration_info_json = dict()
                    # iteration_info_json["params"] = json_object_params
                    # iteration_info_json["results"] = json_object_results
                    # iteration_info = json.dumps(iteration_info_json, indent=4)
                    # file_itr = open(iterations_dir + "/" + str(v[0]) + ".json", "w")
                    # file_itr.write(iteration_info)
                    # file_itr.close()

                    logging.info("iteration time = " + str(time_taken) + " seconds")

                    # removing finished process from the pool
                    process_pool_map.pop(p)
                    process_time_map.pop(p)
                    print "\n-----------------------------------------------------------"
                    print "COMPLETE:", params_and_configs[v[0]][1]
                    print "-----------------------------------------------------------\n"

                    # Zipping logs:
                    logging.info("zipping logs...")
                    zip_start_time = time.time()
                    print "[DEBUG]: zip cmd:"
                    print "zip -jr " + itr_logs_dir + "/logs-" + str(v[0]) + ".zip " + itr_logs_dir + "/logs-" + str(v[0]) + "/*"

                    os.system("zip -jr " + itr_logs_dir + "/logs-" + str(
                        v[0]) + ".zip " + itr_logs_dir + "/logs-" + str(v[0]) + "/*")
                    os.system("yes | rm -r " + itr_logs_dir + "/logs-" + str(v[0]))
                    logging.info(
                        "zipping and removing have finished in " + str(int(time.time() - zip_start_time)) + " sec")

                    # decreasing number of currently running:
                    number_of_running = number_of_running - 1

    # # Parsing all files in 'iterations/' to create tables:
    # itr_json_files = glob.glob(iterations_dir + "/*.json")
    # df_params = pandas.DataFrame(columns=["itr"])
    # df_results = pandas.DataFrame(columns=["itr",
    #                                        "days",
    #                                        "pnl",
    #                                        "positive_days",
    #                                        "negative_days",
    #                                        "zero_days",
    #                                        "average_daily_pnl",
    #                                        "median_daily_pnl",
    #                                        "sharpe",
    #                                        "sortino",
    #                                        "average_daily_volume",
    #                                        "avg_holding_time_median",
    #                                        "avg_holding_time_overall"])
    #
    # for f in itr_json_files:
    #     fhandler = open(f, "r")
    #     json_str = fhandler.read()
    #     fhandler.close()
    #
    #     basename = ntpath.basename(f)
    #     itr_num = basename.replace(".json", "")
    #
    #     json_obj = json.loads(json_str)
    #     params_node = json_obj["params"]
    #     params_series = pandas.Series()
    #     params_series["itr"] = int(itr_num)
    #     for k,v in params_node.iteritems():
    #         params_series[k] = v
    #     df_params = df_params.append(params_series, ignore_index=True)
    #
    #     results_node = json_obj["results"]
    #     results_series = pandas.Series()
    #     results_series["itr"] = int(itr_num)
    #     for k,v in results_node.iteritems():
    #         results_series[k] = v
    #     df_results = df_results.append(results_series, ignore_index=True)
    #
    # df_params = df_params.sort_values(by="itr")
    # df_results = df_results.sort_values(by="itr")

    # # params table:
    # df_params.to_csv(script_dir + "/opt-params.csv", index=None)
    #
    # # results table:
    # df_results.to_csv(script_dir + "/opt-results.csv", index=None)

    # Iterating through executor.leg_names:
    leg_names = executor.leg_names
    for leg in leg_names:
        itr_json_files = glob.glob(iterations_dir + "/*" + leg + "*.json")
        df_params = pandas.DataFrame(columns=["itr"])
        df_results = pandas.DataFrame(columns=["itr",
                                               "days",
                                               "pnl",
                                               "positive_days",
                                               "negative_days",
                                               "zero_days",
                                               "avg_pnl",
                                               "median_pnl",
                                               "sharpe",
                                               "sortino",
                                               "avg_daily_turnover",
                                               "median_daily_holding_time",
                                               "average_daily_holding_time"])
        for f in itr_json_files:
            f_handler = open(f, "r")
            json_str = f_handler.read()
            f_handler.close()

            basename = ntpath.basename(f)
            itr_num = basename.replace("." + leg + ".json", "")

            json_obj = json.loads(json_str)
            params_node = json_obj["params"]
            params_series = pandas.Series()
            params_series["itr"] = int(itr_num)
            for k, v in params_node.iteritems():
                params_series[k] = v
            df_params = df_params.append(params_series, ignore_index=True)

            results_node = json_obj["results"]
            results_series = pandas.Series()
            results_series["itr"] = int(itr_num)
            for k, v in results_node.iteritems():
                results_series[k] = v
            df_results = df_results.append(results_series, ignore_index=True)

        df_params = df_params.sort_values(by="itr")
        df_results = df_results.sort_values(by="itr")

        df_params.to_csv(script_dir + "/opt-params.csv", index=None)

        if leg == "":
            df_results.to_csv(script_dir + "/opt-results.csv", index=None)
        else:
            df_results.to_csv(script_dir + "/" + leg + ".opt-results.csv", index=None)

    # Create directory last-run and move all necessary info
    last_run_dir = script_dir + "/last-run"
    os.system("mkdir " + last_run_dir)
    os.system("mv " + configs_out_dir + " " + last_run_dir)
    os.system("mv " + iterations_dir + " " + last_run_dir)
    os.system("mv " + itr_logs_dir + " " + last_run_dir)
    os.system("mv " + script_dir + "/*.csv " + last_run_dir)

    os.system("mv " + script_dir + "/stdout*.log " + last_run_dir)
    os.system("mv " + script_dir + "/grid.log " + last_run_dir)
    os.system("mv " + script_dir + "/args.json " + last_run_dir)

    # Create all moved data for clean next run:
    os.system("mkdir -p " + configs_out_dir)
    os.system("mkdir -p " + itr_logs_dir)
    os.system("mkdir -p " + iterations_dir)

    # Zipping results to single archive
    datetimenow = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d-%H:%M:%S")
    os.system("cd last-run; zip -r ../" + datetimenow + ".zip *")

    logging.info("==================================================================")
    logging.info("Finished at " + datetimenow)
