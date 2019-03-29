from tabu_search import search
from feasible_solution_factory import *
import time, sys, getopt


def print_help_and_exit():
    print("usage:\n")
    print(" " * 2, "python main.py [-h] -t <runtime> -s <tabu size> -n <neighborhood size> -w <neighborhood wait> <data>")
    print()
    print("args:\n")
    print("[-h]".center(10), "prints this help message")
    print("-t".center(10), "runtime in seconds for tabu search")
    print("-s".center(10), "tabu list size")
    print("-n".center(10), "neighborhood size")
    print("-w".center(10), "max time in seconds to wait for generating a neighborhood")
    print("data".center(10), "directory containing the files: jobTasks.csv")
    print(" " * 42, "machineRunSpeed.csv")
    print(" " * 42, "sequenceDependencyMatrix.csv")
    print("example:\n")
    print(" " * 2, "python main.py -t 600 -s 100 -n 150 -w 1 ./data/data_set2")
    sys.exit()


def parse_args(argv):
    """
    This function parses all of the command line arguments.
    If the user does not provide all of the necessary arguments then a help message is printed.

    Parses the following arguments:
        [-h | --help]
        (-t | --time=)          time in seconds for tabu search to run
        (-s | --tabu=)          tabu list size
        (-n | --neighborhood=)  neighborhood size
        (-w | --wait=)          max time in seconds to wait for generating a neighborhood
        data                    directory that contains the csv files

    :param argv: a list of command line arguments to parse
    :return: parsed arguments in the order (time, tabu, neighborhoood, wait, data)
    """

    tabu_search_time = None
    tabu_list_size = None
    neighborhood_size = None
    neighborhood_wait = None
    data_directory = None

    try:

        opts, args = getopt.getopt(argv, "ht:s:n:w:", ["help", "time=", "tabu=", "neighborhood=", "wait="])

    except getopt.GetoptError:
        print_help_and_exit()

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print_help_and_exit()
        elif opt in ("-t", "--time"):
            tabu_search_time = float(arg)
        elif opt in ("-s", "--tabu"):
            tabu_list_size = int(arg)
        elif opt in ("-n", "--neighborhood"):
            neighborhood_size = int(arg)
        elif opt in ("-w", "--wait"):
            neighborhood_wait = float(arg)

    # check if data directory was passed in
    if len(args) == 1:
        data_directory = args[0]

    # check if all parameters were initialized
    if tabu_search_time is None or tabu_list_size is None or neighborhood_size is None or neighborhood_wait is None or data_directory is None:
        print_help_and_exit()

    print(f"search time = {tabu_search_time} seconds\n"
          f"tabu list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"neighborhood wait time = {neighborhood_wait} seconds\n"
          f"data directory = {data_directory}")

    return tabu_search_time, tabu_list_size, neighborhood_size, neighborhood_wait, data_directory


def main(args):
    start_time = time.time()

    # read csv files
    # make sure the path to the data directory is correct and it contains the csv files!
    Data.read_data_from_files(f'{args[4]}/sequenceDependencyMatrix.csv',
                              f'{args[4]}/machineRunSpeed.csv',
                              f'{args[4]}/jobTasks.csv')

    initial_solution = generate_feasible_solution()

    print("\nInitial Solution:")
    print(f"makespan = {round(initial_solution.makespan)}")

    print("\nTabu Search Result:")
    print("...searching...")
    tuple = search(initial_solution, search_time=args[0], tabu_size=args[1], neighborhood_size=args[2],
                   neighborhood_wait=args[3])
    print(f"makespan = {round(tuple[0].makespan)}\n\n"
          f"number of iterations TS performed = {tuple[1]}")

    print(f"\nDuration {time.time() - start_time} seconds")


if __name__ == '__main__':
    # uncomment this if you don't want to pass command line args
    sys.argv[1:] = ["-t", 6, "-s", 10, "-n", 8, "-w", 0.1, "./data/data_set1"]
    main(parse_args(sys.argv[1:]))
