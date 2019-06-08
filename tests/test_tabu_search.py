import unittest
from JSSP.data import Data
from JSSP.solver import Solver
import os
import shutil

"""
Test solver.tabu_search() function
"""


class TestTS(unittest.TestCase):

    def __init__(self, *args):
        self.tmp_dir = os.path.dirname(os.path.realpath(__file__)) + '/tmp'
        Data.initialize_data_from_csv('../data/given_data/sequenceDependencyMatrix.csv',
                                      '../data/given_data/machineRunSpeed.csv',
                                      '../data/given_data/jobTasks.csv')

        super(TestTS, self).__init__(*args)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_ts_time(self):

        try:

            # parameters
            runtime = 5  # seconds
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search_time(runtime,
                                    num_processes,
                                    tabu_list_size,
                                    neighborhood_size,
                                    neighborhood_wait,
                                    probability_change_machine)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.ts_best_solution)

        # output results
        solver.ts_best_solution.create_schedule(self.tmp_dir)
        self.assertTrue(os.path.exists(self.tmp_dir + '/Schedule.xlsx'))

    def test_ts_time_benchmark(self):

        try:
            # parameters
            runtime = 5  # seconds
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search_time(runtime,
                                    num_processes,
                                    tabu_list_size,
                                    neighborhood_size,
                                    neighborhood_wait,
                                    probability_change_machine,
                                    benchmark=True)

        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

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

    def test_ts_iter(self):

        try:

            # parameters
            iterations = 50
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search_iter(iterations,
                                    num_processes,
                                    tabu_list_size,
                                    neighborhood_size,
                                    neighborhood_wait,
                                    probability_change_machine)

        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.ts_best_solution)

        # output results
        solver.ts_best_solution.create_schedule(self.tmp_dir)
        self.assertTrue(os.path.exists(self.tmp_dir + '/Schedule.xlsx'))

    def test_ts_iter_benchmark(self):

        try:
            # parameters
            iterations = 50
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8
            solver = Solver()

            solver.tabu_search_iter(iterations,
                                    num_processes,
                                    tabu_list_size,
                                    neighborhood_size,
                                    neighborhood_wait,
                                    probability_change_machine,
                                    benchmark=True)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.ts_best_solution)

        for value in solver.ts_parameters.values():
            self.assertIsNotNone(value)

        self.assertTrue(solver.ts_benchmark)
        self.assertNotEqual(0, len(solver.ts_iterations))
        self.assertNotEqual(0, len(solver.ts_nh_sizes))
        self.assertNotEqual(0, len(solver.ts_makespans))
        self.assertNotEqual(0, len(solver.ts_tabu_sizes))
        self.assertNotEqual(0, len(solver.ts_min_makespan_coordinates))

        for ts_iteration in solver.ts_iterations:
            self.assertEqual(iterations, ts_iteration)

        # output results
        solver.output_benchmark_results(self.tmp_dir, name='test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(self.tmp_dir + '/test_benchmark'))


if __name__ == '__main__':
    unittest.main()
