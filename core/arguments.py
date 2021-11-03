import argparse


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern',
                        nargs=None,
                        required=False,
                        help='TODO: help for --pattern')

    parser.add_argument('-d', '--dates',
                        nargs=None,
                        default="",
                        required=False,
                        help='TODO: help for --dates')

    parser.add_argument('-before', '--before', '-b',
                        nargs=None,
                        type=int,
                        default=0,
                        required=False,
                        help='specify minutes before closeout, example: "--before 15" for 15 minutes')

    parser.add_argument('-after', '--after', '-a',
                        nargs=None,
                        type=int,
                        default=0,
                        required=False,
                        help='specify minutes after closeout, example: "--after 15" for 15 minutes')

    parser.add_argument('-wl', '--whitelist',
                        nargs=None,
                        type=str,
                        default="",
                        required=False,
                        help='[TODO: add description] Days to run')

    parser.add_argument('-bl', '--blacklist',
                        nargs=None,
                        type=str,
                        default="",
                        required=False,
                        help='name of a file with blacklist days')

    # parser.add_argument('-e',
    #                     nargs=None,
    #                     type=str,
    #                     default="",
    #                     required=False,
    #                     help='Expiry rollover rules, example: -e "CL=0m,6E=1q"')

    parser.add_argument('-tl', '--timelimit',
                        nargs=None,
                        type=int,
                        default=7200,
                        required=False,
                        help='Number of points including lowest and highest')

    parser.add_argument('--score',
                        nargs=None,
                        type=int,
                        default=0,
                        required=False,
                        help="Messaging score limit above which penalty of 1000 will be applied, score = 0 (by default) no penalty will be applied")

    parser.add_argument('-s', '--sub_num',
                        nargs=None,
                        type=int,
                        default=1,
                        required=False,
                        help='How many iterations to start at a time, default = 1')

    parser.add_argument('--parts',
                        nargs=None,
                        type=int,
                        default=1,
                        required=False,
                        help='example: --parts 5, default is 1')

    parser.add_argument('-resume', '--resume',
                        action='store_true',
                        required=False,
                        help='')

    return parser
