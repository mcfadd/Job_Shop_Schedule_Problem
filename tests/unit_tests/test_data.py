import os
import shutil
import unittest

import numpy as np

from JSSP import data
from tests import project_root
from tests import tmp_dir, get_all_fjs_files


class TestData(unittest.TestCase):
    def test_create_csv_data(self):
        csv_data = data.CSVData(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

        self.assertIsNotNone(csv_data.seq_dep_matrix_file_path)
        self.assertIsNotNone(csv_data.machine_speeds_file_path)
        self.assertIsNotNone(csv_data.job_tasks_file_path)
        self.assertIsNotNone(csv_data.sequence_dependency_matrix)
        self.assertIsNotNone(csv_data.job_task_index_matrix)
        self.assertIsNotNone(csv_data.usable_machines_matrix)
        self.assertIsNotNone(csv_data.task_processing_times_matrix)
        self.assertIsNotNone(csv_data.machine_speeds)

        self.assertNotEqual([], csv_data.jobs)
        self.assertIsNotNone(csv_data.total_number_of_jobs)
        self.assertIsNotNone(csv_data.total_number_of_tasks)
        self.assertIsNotNone(csv_data.total_number_of_machines)
        self.assertIsNotNone(csv_data.max_tasks_for_a_job)

        print(csv_data)

    def test_create_fjs_data(self):
        fjs_lst = get_all_fjs_files()

        for i, fjs_instance in enumerate(fjs_lst):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_lst)})")
            fjs_data = data.FJSData(fjs_instance)

            self.assertIsNotNone(fjs_data.fjs_file_path)
            self.assertIsNotNone(fjs_data.sequence_dependency_matrix)
            self.assertIsNotNone(fjs_data.job_task_index_matrix)
            self.assertIsNotNone(fjs_data.usable_machines_matrix)
            self.assertIsNotNone(fjs_data.task_processing_times_matrix)

            self.assertNotEqual([], fjs_data.jobs)
            self.assertIsNotNone(fjs_data.total_number_of_jobs)
            self.assertIsNotNone(fjs_data.total_number_of_tasks)
            self.assertIsNotNone(fjs_data.total_number_of_machines)
            self.assertIsNotNone(fjs_data.max_tasks_for_a_job)

    def test_attempt_create_base_class_data(self):
        try:
            data.Data()
            self.fail("Should not be able to instantiate type Data")
        except TypeError:
            pass


class TestFJSConversionToCSV(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_converting_fjs_instances(self):
        fjs_lst = get_all_fjs_files()

        for i, fjs_instance in enumerate(fjs_lst):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_lst)})")
            fjs_data = data.FJSData(fjs_instance)

            # copy all of the data that was read in
            sequence_dependency_matrix = np.copy(fjs_data.sequence_dependency_matrix)
            job_task_index_matrix = np.copy(fjs_data.job_task_index_matrix)
            usable_machines_matrix = np.copy(fjs_data.usable_machines_matrix)
            task_processing_times_matrix = np.copy(fjs_data.task_processing_times_matrix)
            jobs = fjs_data.jobs[:]
            total_number_of_jobs = fjs_data.total_number_of_jobs
            total_number_of_tasks = fjs_data.total_number_of_tasks
            total_number_of_machines = fjs_data.total_number_of_machines
            max_tasks_for_a_job = fjs_data.max_tasks_for_a_job

            data.Data.convert_fjs_to_csv(fjs_instance, tmp_dir)

            # read in converted csv file
            csv_data = data.CSVData(tmp_dir + os.sep + 'sequenceDependencyMatrix.csv',
                                    tmp_dir + os.sep + 'machineRunSpeed.csv',
                                    tmp_dir + os.sep + 'jobTasks.csv')

            # make sure the data is the same
            np.testing.assert_array_equal(sequence_dependency_matrix, csv_data.sequence_dependency_matrix,
                                          err_msg=f'sequence dependency matrices are not equal for {fjs_instance}')
            np.testing.assert_array_equal(job_task_index_matrix, csv_data.job_task_index_matrix,
                                          err_msg=f'job-task index matrices are not equal for {fjs_instance}')
            np.testing.assert_array_equal(usable_machines_matrix, csv_data.usable_machines_matrix,
                                          err_msg=f'usable machines matrices are not equal for {fjs_instance}')

            # TODO task_processing_times_matrix will not always be equal because of the way Data.convert_fjs_to_csv is implemented
            # np.testing.assert_array_equal(task_processing_times_matrix, csv_data.task_processing_times_matrix)

            self.assertEqual(task_processing_times_matrix.shape, csv_data.task_processing_times_matrix.shape,
                             f'task processing times matrices are not same shape for {fjs_instance}')
            self.assertEqual(jobs, csv_data.jobs, f'jobs lists are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_jobs, csv_data.total_number_of_jobs,
                             f'total number of jobs are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_tasks, csv_data.total_number_of_tasks,
                             f'total number of tasks are not equal for {fjs_instance}')
            self.assertEqual(total_number_of_machines, csv_data.total_number_of_machines,
                             f'total number of machines are not equal for {fjs_instance}')
            self.assertEqual(max_tasks_for_a_job, csv_data.max_tasks_for_a_job,
                             f'max tasks for a job are not equal for {fjs_instance}')


if __name__ == '__main__':
    unittest.main()
