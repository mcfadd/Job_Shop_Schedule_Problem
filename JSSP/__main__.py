import multiprocessing as mp
import os
import sys

# change path to include JSSP
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

from JSSP import parser
from JSSP.data import Data
from JSSP.main import main


def start():
    mp.set_start_method('fork')
    args = parser.parse_args()

    # initialize static data from csv files
    Data.initialize_data(f'{args.data}/sequenceDependencyMatrix.csv',
                         f'{args.data}/machineRunSpeed.csv',
                         f'{args.data}/jobTasks.csv')

    # run the main program
    return main(args.runtime,
                args.output_dir,
                args.num_processes,
                args.tabu_list_size,
                args.neighborhood_size,
                args.neighborhood_wait,
                args.probability_change_machine,
                initial_solution=args.initial_solution if args.benchmark else None,
                is_benchmark=args.benchmark,
                verbose=args.verbose,
                progress_bar=args.progress_bar)


if __name__ == '__main__':
    sys.exit(start())
