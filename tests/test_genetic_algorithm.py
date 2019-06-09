import os
import shutil
import unittest

from JSSP.data import Data
from JSSP.solver import Solver

"""
Test the genetic algorithm
"""


class TestGA(unittest.TestCase):

    def __init__(self, *args):
        self.tmp_dir = os.path.dirname(os.path.realpath(__file__)) + '/tmp'

        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        Data.initialize_data_from_csv(self.project_root + '/data/given_data/sequenceDependencyMatrix.csv',
                                      self.project_root + '/data/given_data/machineRunSpeed.csv',
                                      self.project_root + '/data/given_data/jobTasks.csv')
        super(TestGA, self).__init__(*args)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_ga_time(self):

        try:

            # parameters
            runtime = 5  # seconds
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            # run GA
            solver = Solver()
            solver.genetic_algorithm_time(runtime,
                                          population,
                                          population_size,
                                          mutation_probability,
                                          selection_size)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.ga_best_solution, "GA should have produced a best solution")

        # output results
        solver.ga_best_solution.create_schedule(self.tmp_dir, filename='ga_test_schedule')
        self.assertTrue(os.path.exists(self.tmp_dir + '/ga_test_schedule.xlsx'),
                        "ga_test_schedule.xlsx was not produced")

    def test_ga_time_benchmark(self):

        try:

            # parameters
            runtime = 5  # seconds
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver()
            solver.genetic_algorithm_time(runtime,
                                          population,
                                          population_size,
                                          mutation_probability,
                                          selection_size,
                                          benchmark=True)
        except Exception as e:
            self.fail("Unexpected exception raised:" + str(e))

        self.assertIsNotNone(solver.ga_best_solution, "GA should have produced a best solution")

        for value in solver.ga_parameters.values():
            self.assertIsNotNone(value, "One of the GA parameters was not set")

        self.assertTrue(solver.ga_benchmark, "GA should have ran a benchmark")
        self.assertIsNotNone(solver.ga_iterations, "GA iterations should not be None")

        self.assertNotEqual(0, len(solver.ga_best_makespans))
        self.assertNotEqual(0, len(solver.ga_avg_population_makespans))
        self.assertNotEqual(0, len(solver.ga_min_makespan_coordinates))

        # output results
        solver.output_benchmark_results(self.tmp_dir, name='test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(self.tmp_dir + '/test_benchmark'))

    def test_ga_iter(self):

        try:

            # parameters
            iterations = 50
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            # run GA
            solver = Solver()
            solver.genetic_algorithm_iter(iterations,
                                          population,
                                          population_size,
                                          mutation_probability,
                                          selection_size)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.ga_best_solution, "GA should have produced a best solution")

        # output results
        solver.ga_best_solution.create_schedule(self.tmp_dir, filename='ga_test_schedule')
        self.assertTrue(os.path.exists(self.tmp_dir + '/ga_test_schedule.xlsx'),
                        "ga_test_schedule.xlsx was not produced")

    def test_ga_iter_benchmark(self):

        try:

            # parameters
            iterations = 50
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver()
            solver.genetic_algorithm_iter(iterations,
                                          population,
                                          population_size,
                                          mutation_probability,
                                          selection_size,
                                          benchmark=True)
        except Exception as e:
            self.fail("Unexpected exception raised:" + str(e))

        self.assertIsNotNone(solver.ga_best_solution, "GA should have produced a best solution")

        for value in solver.ga_parameters.values():
            self.assertIsNotNone(value, "One of the GA parameters was not set")

        self.assertTrue(solver.ga_benchmark, "GA should have ran a benchmark")
        self.assertEqual(iterations, solver.ga_iterations, "GA iterations is incorrect")

        self.assertNotEqual(0, len(solver.ga_best_makespans))
        self.assertNotEqual(0, len(solver.ga_avg_population_makespans))
        self.assertNotEqual(0, len(solver.ga_min_makespan_coordinates))

        # output results
        solver.output_benchmark_results(self.tmp_dir, name='test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(self.tmp_dir + '/test_benchmark'))


if __name__ == '__main__':
    unittest.main()
