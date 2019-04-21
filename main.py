import time
from progressbar import Bar, ETA, ProgressBar, RotatingMarker
import multiprocessing as mp
import tabu
import benchmark
from data import Data
import parser


def progress_bar(seconds):
    widgets = [Bar(marker=RotatingMarker()), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        time.sleep(.99)
        pbar.update(i)
    pbar.finish()
    print()


def main(args):
    print(f"Parameters:\n"
          f"number of processes = {args.num_processes}\n"
          f"runtime = {args.runtime} seconds\n"
          f"tabu list size = {args.tabu_list_size}\n"
          f"neighborhood size = {args.neighborhood_size}\n"
          f"neighborhood wait time = {args.neighborhood_wait} seconds\n"
          f"probability of changing an operation's machine = {args.probability_change_machine}\n"
          f"data directory = {args.data}\n"
          f"output directory = {args.output_dir}")

    ts_manager = tabu.TabuSearchManager(args)
    ts_manager.start(verbose=args.verbose)

    print("Tabu Search Makespan Results:")
    print([solution.makespan for solution in ts_manager.all_solutions])
    print()
    print("Best Solution Found:")
    ts_manager.best_solution.pprint()
    print()
    print(f"Schedule.xlsx placed in {args.output_dir}")
    ts_manager.best_solution.create_schedule(args.output_dir)


if __name__ == '__main__':
    mp.set_start_method('fork')
    arguments = parser.parse_args()
    Data.initialize_data(f'{arguments.data}/sequenceDependencyMatrix.csv',
                         f'{arguments.data}/machineRunSpeed.csv',
                         f'{arguments.data}/jobTasks.csv')

    if arguments.progress_bar:
        mp.Process(target=progress_bar, args=[arguments.runtime]).start()

    if arguments.benchmark:
        benchmark.run(arguments)
    else:
        main(arguments)
