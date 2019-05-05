import os

from . import tabu_search


def main(runtime, output_dir, num_processes=4, tabu_list_size=50, neighborhood_size=300, neighborhood_wait=0.1,
         probability_change_machine=0.8, initial_solutions=None, is_benchmark=False, verbose=False, progress_bar=False):
    """
    Runs the main program.

    This function runs Tabu Search in parallel for a certain duration then puts the results in the output directory specified.

    :param runtime: The duration that Tabu search will run in seconds.
    :param output_dir: The directory to place the results into.
    :param num_processes: The number of Tabu search processes to run in parallel.
    :param tabu_list_size: The size of the Tabu list.
    :param neighborhood_size: The size of neighborhoods to generate during Tabu search.
    :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :param initial_solutions: The initial solutions to start the Tabu searches from (defaults to generating random solutions).
    :param is_benchmark: If True, a benchmark run is performed. See JSSP.benchmark for details
    :param verbose: If True, extra information such as pid of child processes is printed
    :param progress_bar: If True, spawns a progress bar
    :return: 0 if successful
    """
    if is_benchmark:
        print("...Running Benchmark...")

    print(f"Parameters:\n"
          f"runtime = {runtime} seconds\n"
          f"output directory = {output_dir}\n"
          f"number of processes = {num_processes}\n"
          f"tabu list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"neighborhood wait time = {neighborhood_wait} seconds\n"
          f"probability of changing an operation's machine = {probability_change_machine}\n"
          )

    ts_manager = tabu_search.TabuSearchManager(runtime,
                                               num_processes,
                                               tabu_list_size,
                                               neighborhood_size,
                                               neighborhood_wait,
                                               probability_change_machine,
                                               initial_solutions)

    ts_manager.start(benchmark=is_benchmark, verbose=verbose, progress_bar=progress_bar)

    print("Tabu Search Makespan Results:")
    print([solution.makespan for solution in ts_manager.all_solutions])
    print()
    print("Best Solution Found:")
    ts_manager.best_solution.pprint()

    # check if output directory exists
    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if is_benchmark:
        print()
        print("generating benchmark results")
        ts_manager.output_benchmark_results(output_dir)
    else:
        print()
        print(f"Schedule.xlsx placed in {output_dir}")
        ts_manager.best_solution.create_schedule(output_dir)

    return 0

