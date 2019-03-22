#!/usr/bin/env python3
from tabu_search import search
from feasible_solution_factory import *
import time, sys, getopt


def print_usage_and_exit():
    print("usage:\n"
          " main.py [-h] -t <time in minutes to run> -s <tabu list size> -n <neighborhood size> <data directory>")
    sys.exit()


def parse_args(argv):
    """
    This function parses all of the command line arguments.
    If the user does not provide all of the necessary arguments then a help message will be printed.

    Parses the following arguments:
        [-h | --help]
        (-t | --time=) time in minutes for tabu search to run
        (-s | --tabu=) tabu list size
        (-s | --nieghborhood=) neighborhood size
        (<data_dir>) directory that contains the csv files

    :param argv: a list of command line arguments to parse
    :return: the parsed arguments
    """

    tabu_search_time = None
    tabu_list_size = None
    neighborhood_size = None
    data_directory = None

    try:

        opts, args = getopt.getopt(argv, "ht:s:n:", ["help", "time=", "tabu=", "neighborhood="])

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

    # check if data directory was passed in
    if len(args) == 1:
        data_directory = args[0]

    # check if all parameters were initialized
    if tabu_search_time is None or tabu_list_size is None or neighborhood_size is None or data_directory is None:
        print_usage_and_exit()

    print(f"search time = {tabu_search_time} minute(s)\n"
          f"tabu list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"data directory = {data_directory}")

    return tabu_search_time, tabu_list_size, neighborhood_size, data_directory


def main(args):
    start_time = time.time()

    # read csv files
    # make sure the path to the data directory is correct and it contains the csv files!
    Data.read_data_from_files(f'{args[3]}/sequenceDependencyMatrix.csv',
                              f'{args[3]}/machineRunSpeed.csv',
                              f'{args[3]}/jobTasks.csv')

    initial_solution = generate_feasible_solution()

    print("\nInitial Solution:")
    print(f"makespan = {round(initial_solution.makespan)}")

    print("\nTabu Search Result:")
    print("...searching...")
    tuple = search(initial_solution, args[0], tabu_size=args[1], neighborhood_size=args[2])
    print(f"makespan = {round(tuple[0].makespan)}\n"
          f"number of iterations TS performed = {tuple[1]}")

    duration = time.time() - start_time

    print(f"\nDuration {duration} seconds")


if __name__ == '__main__':
    # sys.argv[1:] = ["-t", .01, "-s", 10, "-n", 8, "./data"]  # uncomment this if you don't want to pass command line args
    main(parse_args(sys.argv[1:]))
