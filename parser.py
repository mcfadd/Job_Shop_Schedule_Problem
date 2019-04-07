import argparse
import os
import pickle

import solution


def print_message_and_usage(message):
    print(message)
    parser.print_usage()
    exit(1)


class CheckDataDir(argparse.Action):

    def __call__(self, parser_obj, namespace, values, option_string=None):
        if not os.path.isdir(values):
            print_message_and_usage("data directory does not exist!: " + values)
        if not (os.path.exists(values + "/jobTasks.csv") and
                os.path.exists(values + "/machineRunSpeed.csv") and
                os.path.exists(values + "/sequenceDependencyMatrix.csv")):
            print_message_and_usage("data directory does not contain required csv files!")
        namespace.data = values


class CheckBenchmarkArgs(argparse.Action):

    def __call__(self, parser_obj, namespace, values, option_string=None):
        try:

            if not os.path.exists(values[0]):
                print_message_and_usage("solution file does not exist!: " + values[0])

            with open(values[0], 'rb') as fin:
                sol = pickle.load(fin)
                if not isinstance(sol, solution.Solution):
                    print_message_and_usage("solution file must contain a pickled Solution object!")

            namespace.benchmark = True
            namespace.initial_solution = sol
            namespace.iterations = int(values[1])

        except ValueError:
            print_message_and_usage("N must be and integer value!: " + values[1])
        except pickle.UnpicklingError:
            print_message_and_usage("solution file must contain a pickled Solution object!")


# create parser object and add arguments
parser = argparse.ArgumentParser()
parser.add_argument('-pb', default=False, required=False,
                    help="Spawns a progress bar.", dest="progress_bar", action='store_true')
parser.add_argument('-b', nargs=2, type=str, required=False, metavar=("solution_file", "N"), default=False,
                    dest="benchmark",
                    help="Runs a benchmark of the program. Tabu Search is ran N times starting with an initial solution, then a report of the results is put in the output directory. "
                         "solution_file contains the pickled initial solution to start the search from.",
                    action=CheckBenchmarkArgs)
parser.add_argument('-o', type=str, default="~/jsp_output",
                    help="Directory where output is placed. (default = ~/jsp_output)",
                    metavar="output", dest="output_dir")
parser.add_argument('-rt', type=int, required=True, help="Runtime in seconds for tabu search",
                    metavar="runtime", dest="runtime")
parser.add_argument('-ts', type=int, required=True, help="Tabu list size", metavar="tabu_list_size",
                    dest="tabu_list_size")
parser.add_argument('-ns', type=int, required=True, help="Neighborhood size", metavar="neighborhood_size",
                    dest="neighborhood_size")
parser.add_argument('-nw', type=float, default=0.1,
                    help="Maximum time in seconds to wait while generating a neighborhood. (default = 0.1)",
                    metavar="neighborhood_wait", dest="neighborhood_wait")
parser.add_argument('-p', type=float, default=0.5,
                    help="Probability of changing an operation's machine when generating a neighbor. (default = 0.1)",
                    metavar="prob_change_machine", dest="probability_change_machine")
parser.add_argument('data', type=str,
                    help="Directory containing the files: jobTasks.csv, machineRunSpeed.csv, sequenceDependencyMatrix.csv",
                    action=CheckDataDir)
