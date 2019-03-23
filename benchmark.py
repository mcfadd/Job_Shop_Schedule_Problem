#!/usr/bin/env python3
from tabu_search import search
from feasible_solution_factory import *
import time, sys, getopt
import statistics


def print_usage_and_exit():
    print("usage:\n"
          " benchmark.py [-h] -t <time in minutes for each tabu search> -s <tabu list size> -n <neighborhood size> -i <number of tabu searches to run>  <data directory>")
    sys.exit()


def parse_args(argv):
    """
    This function parses all of the command line arguments.
    If the user does not provide all of the necessary arguments then a help message will be printed.

    Parses the following arguments:
        [-h | --help]
        (-t | --time=) time in minutes for tabu search to run
        (-s | --tabu=) tabu list size
        (-n | --nieghborhood=) neighborhood size
        (-i | --iters=) number of iterations to perform tabu search on initial solution
        (<data_dir>) directory that contains the csv files

    :param argv: a list of command line arguments to parse
    :return: the parsed arguments
    """

    tabu_search_time = None
    tabu_list_size = None
    neighborhood_size = None
    data_directory = None
    iters = None

    try:

        opts, args = getopt.getopt(argv, "ht:s:n:i:", ["help", "time=", "tabu=", "neighborhood=", "iters="])

    except getopt.GetoptError:
        print_usage_and_exit()

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print_usage_and_exit()
        elif opt in ("-t", "--time"):
            tabu_search_time = float(arg)
        elif opt in ("-s", "--tabu"):
            tabu_list_size = int(arg)
        elif opt in ("-n", "--neighborhood"):
            neighborhood_size = int(arg)
        elif opt in ("-i", "--iters"):
            iters = int(arg)

    if len(args) == 1:
        data_directory = args[0]

    if tabu_search_time is None or tabu_list_size is None or neighborhood_size is None or data_directory is None or iters is None:
        print_usage_and_exit()

    print(f"search time = {tabu_search_time} minute(s)\n"
          f"tabu list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"iterations = {iters}\n"
          f"data directory = {data_directory}")

    return tabu_search_time, tabu_list_size, neighborhood_size, iters, data_directory


def main(args):
    start_time = time.time()

    # read csv files
    # make sure the path to the data directory is correct and it contains the csv files!
    Data.read_data_from_files(f'{args[4]}/sequenceDependencyMatrix.csv',
                              f'{args[4]}/machineRunSpeed.csv',
                              f'{args[4]}/jobTasks.csv')

    if args[4] == "data":
        initial_solution = get_small_test_operation()  # this is for getting a consistent feasible solution
    else:
        initial_solution = get_large_test_operation()

    print()
    print(f"initial makespan = {round(initial_solution.makespan)}")

    makespans = []
    iterations = []
    for i in range(args[3]):
        result = search(initial_solution, args[0], tabu_size=args[1], neighborhood_size=args[2])
        makespans.append(result[0].makespan)
        iterations.append(result[1])

    print()
    print("Benchmark results:")
    print("  makespan:")
    print(f"  min = {round(min(makespans))}")
    print(f"  mean = {round(statistics.mean(makespans))}")
    print(f"  max = {round(max(makespans))}")
    print(f"  stdev = {round(statistics.stdev(makespans))}")
    print(f"  var = {round(statistics.variance(makespans))}")

    print(f"mean iterations that tabu search performed = {statistics.mean(iterations)}")

    duration = time.time() - start_time

    print(f"\nDuration {duration} seconds")


if __name__ == '__main__':
    # sys.argv[1:] = ["-t", .01, "-s", 10, "-n", 8, "-i", 10, "./data"]  # uncomment this if you don't want to pass command line args
    sys.argv[1:] = ["-t", .3, "-s", 200, "-n", 50, "-i", 20, "./given_data"]  # uncomment this if you don't want to pass command line args
    main(parse_args(sys.argv[1:]))
