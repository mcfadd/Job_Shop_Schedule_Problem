import os
import shutil
import unittest

import numpy as np

from JSSP.data import Data
from JSSP.solver import Solver
from tests import project_root, tmp_dir

"""
Test that the static data read in from Data.initialize_data_from_fjs is the same as converting the fjs instance 
to csv files using Data.convert_fjs_to_csv, then reading in the data from csv using Data.initialize_data_from_csv
"""


def get_all_fjs_files(path):
    """
    Gets a list of all the absolute file paths of all the .fjs files that are below the path in the directory tree.

    :param path: The root path of the directory tree to search
    :return: A list of all the absolute file paths of all the .fjs files
    """
    result = []
    for dirpath, dirs, files in os.walk(path):
        for filename in files:
            fname = os.path.join(dirpath, filename)
            if fname.endswith('.fjs'):
                result.append(fname)

    return result


# directory used by tests
fjs_data = get_all_fjs_files(project_root + '/data/fjs_data')


class TestFJSConversionToCSV(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_reading_all_fjs_instances(self):

        for fjs_instance in fjs_data:
            try:
                # read in fjs data
                Data.initialize_data_from_fjs(fjs_instance)
            except Exception as e:
                self.fail(f'Failed to read in {fjs_instance}. Exception raised: ' + str(e))

            # copy all of the data that was read in
            sequence_dependency_matrix = np.copy(Data.sequence_dependency_matrix)
            job_task_index_matrix = np.copy(Data.job_task_index_matrix)
            usable_machines_matrix = np.copy(Data.usable_machines_matrix)
            task_processing_times_matrix = np.copy(Data.task_processing_times_matrix)
            jobs = Data.jobs[:]
            total_number_of_jobs = Data.total_number_of_jobs
            total_number_of_tasks = Data.total_number_of_tasks
            total_number_of_machines = Data.total_number_of_machines
            max_tasks_for_a_job = Data.max_tasks_for_a_job

            try:
                # convert fjs data to csv
                Data.convert_fjs_to_csv(fjs_instance, tmp_dir)
            except Exception as e:
                self.fail(f'Failed to convert fjs data to csv for {fjs_instance}. Exception raised: ' + str(e))

            try:
                # read in converted csv file
                Data.initialize_data_from_csv(tmp_dir + '/sequenceDependencyMatrix.csv',
                                              tmp_dir + '/machineRunSpeed.csv',
                                              tmp_dir + '/jobTasks.csv')
            except Exception as e:
                self.fail(f'Failed to read converted fjs data for {fjs_instance}. Exception raised: ' + str(e))

            # make sure the data is the same
            np.testing.assert_array_equal(sequence_dependency_matrix, Data.sequence_dependency_matrix, err_msg=f'sequence dependency matrices are not equal for {fjs_instance}')
            np.testing.assert_array_equal(job_task_index_matrix, Data.job_task_index_matrix, err_msg=f'job-task index matrices are not equal for {fjs_instance}')
            np.testing.assert_array_equal(usable_machines_matrix, Data.usable_machines_matrix, err_msg=f'usable machines matrices are not equal for {fjs_instance}')

            # note the task_processing_times_matrix will not alway be equal because of the way Data.convert_fjs_to_csv is implemented
            # np.testing.assert_array_equal(task_processing_times_matrix, Data.task_processing_times_matrix)

            self.assertEqual(task_processing_times_matrix.shape, Data.task_processing_times_matrix.shape, f'task processing times matrices are not same shape for {fjs_instance}')
            self.assertEqual(jobs, Data.jobs, f'jobs lists are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_jobs, Data.total_number_of_jobs, f'total number of jobs are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_tasks, Data.total_number_of_tasks, f'total number of tasks are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_machines, Data.total_number_of_machines, f'total number of machines are not equal for {fjs_instance}')
            self.assertEqual(max_tasks_for_a_job, Data.max_tasks_for_a_job, f'max tasks for a job are not equal for {fjs_instance}')


class TestFJSOptimization(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir)

    def test_ts_iter(self):
        # parameters
        iterations = 10  # keep this value small
        num_processes = 1
        tabu_list_size = 10
        neighborhood_size = 25
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        for fjs_instance in fjs_data:
            try:
                Data.initialize_data_from_fjs(fjs_instance)

                solver = Solver()
                solver.tabu_search_iter(iterations,
                                        num_processes,
                                        tabu_list_size,
                                        neighborhood_size,
                                        neighborhood_wait,
                                        probability_change_machine)

            except Exception as e:
                self.fail(f'Unexpected exception raised while running TS for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.ts_best_solution, "TS should have produced a best solution")

            # output results
            solver.ts_best_solution.create_schedule(tmp_dir, filename='fjs_ts_schedule')
            self.assertTrue(os.path.exists(tmp_dir + '/fjs_ts_schedule.xlsx'), "fjs_ts_schedule.xlsx was not produced")

    def test_ga_iter(self):
        # parameters
        iterations = 10
        population = None
        population_size = 50
        mutation_probability = 0.8
        selection_size = 5

        for fjs_instance in fjs_data:
            try:
                Data.initialize_data_from_fjs(fjs_instance)

                # run GA
                solver = Solver()
                solver.genetic_algorithm_iter(iterations,
                                              population,
                                              population_size,
                                              mutation_probability,
                                              selection_size)
            except Exception as e:
                self.fail(f'Unexpected exception raised while running GA for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.ga_best_solution, "GA should have produced a best solution")

            # output results
            solver.ga_best_solution.create_schedule(tmp_dir, filename='fjs_ga_schedule')
            self.assertTrue(os.path.exists(tmp_dir + '/fjs_ga_schedule.xlsx'), "fjs_ga_schedule.xlsx was not produced")


if __name__ == '__main__':
    unittest.main()
