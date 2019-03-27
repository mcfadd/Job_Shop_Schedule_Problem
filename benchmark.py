#!/usr/bin/env python3
from data_set import Data
import tabu_search
import feasible_solution_factory
import time, sys, getopt
import statistics


def print_usage_and_exit():
    print("usage:\n"
          " benchmark.py [-h] -t <runtime in seconds> -s <tabu list size> -n <neighborhood size> -w <max wait time for generating a neighborhood in seconds> -i <number of tabu searches to run>  <data directory>")
    sys.exit()


def parse_args(argv):
    """
    This function parses all of the command line arguments.
    If the user does not provide all of the necessary arguments then a help message will be printed.

    Parses the following arguments:
        [-h | --help]
        (-t | --time=) time in minutes for tabu search to run
        (-s | --tabu=) tabu list size
        (-n | --neighborhood=) neighborhood size
        (-w | --wait=) max time to wait for generating a neighborhood
        (-i | --iters=) number of tabu searches to run starting with the initial test solution
        (<data_dir>) directory that contains the csv files

    :param argv: a list of command line arguments to parse
    :return: parsed arguments in the order (time, tabu, neighborhoood, wait, data_dir, iters)
    """

    tabu_search_time = None
    tabu_list_size = None
    neighborhood_size = None
    neighborhood_wait = None
    data_directory = None
    iters = None

    try:

        opts, args = getopt.getopt(argv, "ht:s:n:w:i:", ["help", "time=", "tabu=", "neighborhood=", "wait=", "iters="])

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
        elif opt in ("-w", "--wait"):
            neighborhood_wait = float(arg)
        elif opt in ("-i", "--iters"):
            iters = int(arg)

    # check if data directory was passed in
    if len(args) == 1:
        data_directory = args[0]

    # check if all parameters were initialized
    if tabu_search_time is None or tabu_list_size is None or neighborhood_size is None or neighborhood_wait is None or data_directory is None or iters is None:
        print_usage_and_exit()

    print(f"search time = {tabu_search_time} seconds\n"
          f"tabu list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"neighborhood wait time = {neighborhood_wait} seconds\n"
          f"data directory = {data_directory}\n"
          f"iterations = {iters}")

    return tabu_search_time, tabu_list_size, neighborhood_size, neighborhood_wait, data_directory, iters


def main(args):
    start_time = time.time()

    # read csv files
    # make sure the path to the data directory is correct and it contains the csv files!
    Data.read_data_from_files(f'{args[4]}/sequenceDependencyMatrix.csv',
                              f'{args[4]}/machineRunSpeed.csv',
                              f'{args[4]}/jobTasks.csv')

    if "data_set1" in args[4]:
        initial_solution = feasible_solution_factory.get_small_test_solution()
    else:
        initial_solution = feasible_solution_factory.get_large_test_solution()

    print()
    print(f"initial makespan = {round(initial_solution.makespan)}")

    makespans = []
    iterations = []
    for i in range(args[5]):
        result = tabu_search.search(initial_solution, search_time=args[0], tabu_size=args[1], neighborhood_size=args[2], neighborhood_wait=args[3])
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
    print()
    print(f"mean iterations that tabu search performed = {statistics.mean(iterations)}")

    duration = time.time() - start_time

    print(f"\nDuration {duration} seconds")


if __name__ == '__main__':
    # uncomment this if you don't want to pass command line args
    # sys.argv[1:] = ["-t", 2, "-s", 10, "-n", 8, "-w", 0.01, "-i", 5, "./data/data_set1"]
    sys.argv[1:] = ["-t", 12, "-s", 200, "-n", 50, "-w", 60, "-i", 10, "./data/data_set2"]
    main(parse_args(sys.argv[1:]))
