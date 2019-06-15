import os
import shutil
import unittest

from JSSP.data import Data
from JSSP.solver import Solver
from tests import project_root, tmp_dir

"""
Test solver.tabu_search() function
"""


class TestTS(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        Data.initialize_data_from_csv(project_root + '/data/given_data/sequenceDependencyMatrix.csv',
                                      project_root + '/data/given_data/machineRunSpeed.csv',
                                      project_root + '/data/given_data/jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

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

        self.assertIsNotNone(solver.ts_best_solution, "TS should have produced a best solution")

        # output results
        solver.ts_best_solution.create_schedule(tmp_dir, filename='ts_test_schedule')
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_schedule.xlsx'), "ts_test_schedule.xlsx was not produced")

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
        solver.output_benchmark_results(tmp_dir, name='ts_test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark'), "TS benchmark results were not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/index.html'), "TS benchmark results index.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/ts_makespans.html'), "TS benchmark results ts_makespans.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/neighborhood_sizes.html'), "TS benchmark results neighborhood_sizes.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/tabu_list_sizes.html'), "TS benchmark results tabu_list_sizes.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/ts_schedule.xlsx'), "TS benchmark results ts_schedule.xlsx was not produced")

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

        self.assertIsNotNone(solver.ts_best_solution, "TS should have produced a best solution")

        # output results
        solver.ts_best_solution.create_schedule(tmp_dir, filename='ts_test_schedule')
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_schedule.xlsx'), "ts_test_schedule.xlsx was not produced")

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
        solver.output_benchmark_results(tmp_dir, name='ts_test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark'), "TS benchmark results were not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/index.html'), "TS benchmark results index.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/ts_makespans.html'), "TS benchmark results ts_makespans.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/neighborhood_sizes.html'), "TS benchmark results neighborhood_sizes.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/tabu_list_sizes.html'), "TS benchmark results tabu_list_sizes.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + '/ts_test_benchmark/ts_schedule.xlsx'), "TS benchmark results ts_schedule.xlsx was not produced")


if __name__ == '__main__':
    unittest.main()
