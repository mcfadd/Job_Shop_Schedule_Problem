import argparse
import os
import pickle
import sys

from .solution import Solution


def print_message_and_usage(parser_obj, message):
    """
    Prints a short message and usage of the program then exits.

    :param parser_obj: The argparse object
    :param message: The message to print
    :return:
    """
    print(message)
    parser_obj.print_usage()
    exit(1)


class CheckDataDir(argparse.Action):
    """
    This argparse.Action class checks if the data directory exists ans contains the proper csv files.
    """

    def __call__(self, parser_obj, namespace, values, option_string=None):
        if not os.path.exists(values) or not os.path.isdir(values):
            print_message_and_usage(parser_obj, "data directory does not exist!: " + values)
        if not (os.path.exists(values + "/jobTasks.csv") and
                os.path.exists(values + "/machineRunSpeed.csv") and
                os.path.exists(values + "/sequenceDependencyMatrix.csv")):
            print_message_and_usage(parser_obj, "data directory does not contain required csv files!")
        namespace.data = values


class CheckBenchmarkArgs(argparse.Action):
    """
    This argparse.Action class checks if the initial benchmark solution exists.
    """

    def __call__(self, parser_obj, namespace, values, option_string=None):
        try:

            if os.path.exists(values[0]):

                with open(values[0], 'rb') as fin:
                    sol = pickle.load(fin)
                    if not isinstance(sol, Solution):
                        print_message_and_usage(parser_obj, "solution file must contain a pickled Solution object!")

                namespace.initial_solution = sol

            else:
                namespace.initial_solution = None

            namespace.benchmark = True

        except pickle.UnpicklingError:
            print_message_and_usage(parser_obj, "solution file must contain a pickled Solution object!")


def parse_args():
    """
    Parses all of the command line arguments

    :return: Namespace of arguments
    """

    # create parser object and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-pb', default=False, required=False,
                        help="Spawns a progress bar.", dest="progress_bar", action='store_true')

    parser.add_argument('-b', nargs=1, type=str, required=False, metavar="initial_solution.pkl", default=False, dest="benchmark",
                        help="Runs a benchmark of the program starting with initial_solution.pkl. "
                             "To generate random initial solutions use `-b na`", action=CheckBenchmarkArgs)

    parser.add_argument('-v', default=False, required=False, dest="verbose", action='store_true',
                        help="Runs in verbose mode.")

    parser.add_argument('-o', type=str, default=f"{os.getenv('HOME')}/jssp_output",
                        help="Directory where output is placed. (default = ~/jssp_output)",
                        metavar="output", dest="output_dir")

    parser.add_argument('-np', type=int, default=4,
                        help="Number of processes to run tabu search search in parallel. (default = 4)",
                        metavar="num_processes", dest="num_processes")

    parser.add_argument('-ts', type=int, default=50, help="Tabu list size. (default = 50)", metavar="tabu_list_size",
                        dest="tabu_list_size")

    parser.add_argument('-ns', type=int, default=300, help="Neighborhood size. (default = 300)", metavar="neighborhood_size",
                        dest="neighborhood_size")

    parser.add_argument('-nw', type=float, default=0.1,
                        help="Maximum time in seconds to wait while generating a neighborhood. (default = 0.1)",
                        metavar="neighborhood_wait", dest="neighborhood_wait")

    parser.add_argument('-p', type=float, default=0.8,
                        help="Probability of changing an operation's machine when generating a neighbor. (default = 0.8)",
                        metavar="prob_change_machine", dest="probability_change_machine")

    parser.add_argument('-rt', type=int, required=True, help="Runtime in seconds",
                        metavar="runtime", dest="runtime")

    parser.add_argument('data', type=str,
                        help="Directory containing the files: jobTasks.csv, machineRunSpeed.csv, sequenceDependencyMatrix.csv",
                        action=CheckDataDir)

    return parser.parse_args(sys.argv[1:])
