import unittest
from JSSP.data import Data
from JSSP.solver import Solver
import os
import shutil

"""
Test Solver's Tabu Search (regular run and benchmark run)
"""


class TestTS(unittest.TestCase):

    def __init__(self, *args):
        self.tmp_dir = f'{os.path.dirname(os.path.realpath(__file__))}/tmp'
        super(TestTS, self).__init__(*args)

    def setUp(self) -> None:
        Data.initialize_data_from_csv('../data/given_data/sequenceDependencyMatrix.csv',
                                      '../data/given_data/machineRunSpeed.csv',
                                      '../data/given_data/jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_ts(self):

        try:

            # parameters
            runtime = 5
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search(runtime,
                               num_processes,
                               tabu_list_size,
                               neighborhood_size,
                               neighborhood_wait,
                               probability_change_machine)

            self.assertIsNotNone(solver.ts_best_solution)

            # output results
            solver.ts_best_solution.create_schedule(self.tmp_dir)

            self.assertTrue(os.path.exists(self.tmp_dir + '/Schedule.xlsx'))

        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

    def test_ts_benchmark(self):

        try:
            # parameters
            runtime = 5
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search(runtime,
                               num_processes,
                               tabu_list_size,
                               neighborhood_size,
                               neighborhood_wait,
                               probability_change_machine,
                               benchmark=True)

            self.assertIsNotNone(solver.ts_best_solution)

            for value in solver.ts_parameters.values():
                self.assertIsNotNone(value)

            self.assertTrue(solver.ts_benchmark)
            self.assertNotEqual(0, len(solver.ts_iterations))
            self.assertNotEqual(0, len(solver.ts_nh_sizes))
            self.assertNotEqual(0, len(solver.ts_makespans))
            self.assertNotEqual(0, len(solver.ts_tabu_sizes))
            self.assertNotEqual(0, len(solver.ts_min_makespan_coordinates))

            # output results
            solver.output_benchmark_results(self.tmp_dir, name='test_benchmark', auto_open=False)

            self.assertTrue(os.path.exists(self.tmp_dir + '/test_benchmark'))

        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))


if __name__ == '__main__':
    unittest.main()
