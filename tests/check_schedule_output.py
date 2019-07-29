#!/usr/bin/env python

import os
import datetime

from JSSP.data import Data
from JSSP.solver import Solver

# test given data
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'schedule_output'

# ts parameters
runtime = 30
num_processes = 4


def create_schedule_with_given_data():
    data_directory = project_root + os.sep + 'data' + os.sep + 'given_data'
    Data.initialize_data_from_csv(data_directory + os.sep + 'sequenceDependencyMatrix.csv',
                                  data_directory + os.sep + 'machineRunSpeed.csv',
                                  data_directory + os.sep + 'jobTasks.csv')

    # run tabu search
    solution = Solver().tabu_search_time(runtime,
                                         num_processes
                                         )

    solution.create_schedule_xlsx_file(output_dir, start_time=datetime.time(8, 30), end_time=datetime.time(20, 30), filename='jsp_schedule')
    # solution.create_gantt_chart_html_file(output_dir, filename='jsp_gantt_chart.html', continuous=True)


# test fjs instance
def create_schedule_with_fjs_data():
    data_directory = project_root + os.sep + 'data' + os.sep + 'fjs_data'
    Data.initialize_data_from_fjs(data_directory + os.sep + 'Barnes' + os.sep + 'Barnes_mt10c1.fjs')

    # run tabu search
    solution = Solver().tabu_search_time(runtime,
                                         num_processes
                                         )

    # solution.create_schedule_xlsx_file(output_dir, filename='fjs_schedule')
    # solution.create_gantt_chart_html_file(output_dir)


if __name__ == '__main__':
    create_schedule_with_given_data()
    # create_schedule_with_fjs_data()
