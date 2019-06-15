import os
import pickle
import unittest

from JSSP.data import Data
from JSSP.solution.makespan import compute_machine_makespans
from tests import project_root

"""
Test integrity of solution.makespan.compute_machine_makespans() function for the given data (i.e. csv) 
"""


class TestMakespan(unittest.TestCase):

    def __init__(self, *args):
        self.operation_matrices_dir = os.path.dirname(os.path.abspath(__file__)) + '/operation_matrices'
        super(TestMakespan, self).__init__(*args)

    def setUp(self) -> None:
        Data.initialize_data_from_csv(project_root + '/data/given_data/sequenceDependencyMatrix.csv',
                                      project_root + '/data/given_data/machineRunSpeed.csv',
                                      project_root + '/data/given_data/jobTasks.csv')

    def test_makespan_integrity1(self):
        with open(self.operation_matrices_dir + '/operation_matrix1.pkl', 'rb') as fin:
            operation_matrix = pickle.load(fin)

        machine_makespans = [7996.268342767385, 8398.781671526705, 8343.87056502593, 6924.5613419194015,
                             7787.349643580393, 7397.651671526705, 8520.94199359736, 6546.192632325946]

        self.assertEqual(machine_makespans, list(compute_machine_makespans(operation_matrix,
                                                                           Data.task_processing_times_matrix,
                                                                           Data.sequence_dependency_matrix,
                                                                           Data.job_task_index_matrix)))

    def test_makespan_integrity2(self):
        with open(self.operation_matrices_dir + '/operation_matrix2.pkl', 'rb') as fin:
            operation_matrix = pickle.load(fin)

        machine_makespans = [7164.847326846639, 7826.668527368575, 7298.214357227469, 6836.4973312287375,
                             6670.195475155797, 7201.790941161678, 6566.151253038424, 6003.240322893379]

        self.assertEqual(machine_makespans, list(compute_machine_makespans(operation_matrix,
                                                                           Data.task_processing_times_matrix,
                                                                           Data.sequence_dependency_matrix,
                                                                           Data.job_task_index_matrix)))

    def test_makespan_integrity3(self):
        with open(self.operation_matrices_dir + '/operation_matrix3.pkl', 'rb') as fin:
            operation_matrix = pickle.load(fin)

        machine_makespans = [5622.211909610022, 6668.672413793104, 6198.45099818512, 7328.462489909265,
                             5576.7756781282205, 6459.11152450091, 6441.177636208749, 6614.8161680749035]

        self.assertEqual(machine_makespans, list(compute_machine_makespans(operation_matrix,
                                                                           Data.task_processing_times_matrix,
                                                                           Data.sequence_dependency_matrix,
                                                                           Data.job_task_index_matrix)))

    def test_makespan_integrity4(self):
        with open(self.operation_matrices_dir + '/operation_matrix4.pkl', 'rb') as fin:
            operation_matrix = pickle.load(fin)

        machine_makespans = [9989.582752327537, 10803.08454507686, 9811.387630376317, 7800.677606979643,
                             7691.085943026534, 10134.502752327537, 9078.174622487135, 9977.302745579258]

        self.assertEqual(machine_makespans, list(compute_machine_makespans(operation_matrix,
                                                                           Data.task_processing_times_matrix,
                                                                           Data.sequence_dependency_matrix,
                                                                           Data.job_task_index_matrix)))

    def test_makespan_integrity5(self):
        with open(self.operation_matrices_dir + '/operation_matrix5.pkl', 'rb') as fin:
            operation_matrix = pickle.load(fin)

        machine_makespans = [7887.918413494386, 8837.07330635202, 8506.797444283055, 7980.680300819141,
                             8334.323760072528, 7838.29338568095, 7910.037297677689, 7943.372792640731]

        self.assertEqual(machine_makespans, list(compute_machine_makespans(operation_matrix,
                                                                           Data.task_processing_times_matrix,
                                                                           Data.sequence_dependency_matrix,
                                                                           Data.job_task_index_matrix)))


if __name__ == '__main__':
    unittest.main()
