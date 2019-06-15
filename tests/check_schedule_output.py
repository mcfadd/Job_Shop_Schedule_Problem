import os

from JSSP.data import Data
from JSSP.solver import Solver

# test given data
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = './schedule_output'

# ts parameters
runtime = 5
num_processes = 1


def create_schedule_with_given_data():
    data_directory = project_root + '/data/given_data'
    Data.initialize_data_from_csv(data_directory + '/sequenceDependencyMatrix.csv',
                                  data_directory + '/machineRunSpeed.csv',
                                  data_directory + '/jobTasks.csv')

    # run tabu search
    solution = Solver().tabu_search_time(runtime,
                                         num_processes
                                         )

    solution.create_schedule(output_dir, filename='jsp_schedule')


# test fjs instance
def create_schedule_with_fjs_data():
    data_directory = project_root + '/data/fjs_data'
    Data.initialize_data_from_fjs(data_directory + '/Barnes/Barnes_mt10c1.fjs')

    # run tabu search
    solution = Solver().tabu_search_time(runtime,
                                         num_processes
                                         )

    solution.create_schedule(output_dir, filename='fjs_schedule')


if __name__ == '__main__':
    create_schedule_with_given_data()
    create_schedule_with_fjs_data()
