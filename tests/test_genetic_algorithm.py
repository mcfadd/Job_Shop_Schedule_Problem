import os
import shutil
import unittest

from JSSP.data import Data
from JSSP.solver import Solver

"""
Test Solver's Genetic Algorithm (regular run and benchmark run)
"""


class TestGA(unittest.TestCase):

    def __init__(self, *args):
        self.tmp_dir = f'{os.path.dirname(os.path.realpath(__file__))}/tmp'
        super(TestGA, self).__init__(*args)

    def setUp(self) -> None:
        Data.initialize_data_from_csv('../data/given_data/sequenceDependencyMatrix.csv',
                                      '../data/given_data/machineRunSpeed.csv',
                                      '../data/given_data/jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_ga(self):

        try:

            # parameters
            runtime = 5
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            # run GA
            solver = Solver()
            solver.genetic_algorithm(runtime,
                                     population,
                                     population_size,
                                     mutation_probability,
                                     selection_size)

            self.assertIsNotNone(solver.ga_best_solution, "The GA should have produced a best solution")

            # output results
            solver.ga_best_solution.create_schedule(self.tmp_dir, filename='ga_test_schedule')

            self.assertTrue(os.path.exists(self.tmp_dir + '/ga_test_schedule.xlsx'), "ga_test_schedule.xlsx was not produced")

        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

    def test_ga_benchmark(self):

        try:

            # parameters
            runtime = 5
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver()
            solver.genetic_algorithm(runtime,
                                     population,
                                     population_size,
                                     mutation_probability,
                                     selection_size,
                                     benchmark=True)

            self.assertIsNotNone(solver.ga_best_solution, "The GA should have produced a best solution")

            for value in solver.ga_parameters.values():
                self.assertIsNotNone(value, "One of the GA parameters was not set")

            self.assertTrue(solver.ga_benchmark, "GA should have ran a benchmark")
            self.assertIsNotNone(solver.ga_iterations, "GA")
            self.assertNotEqual(0, len(solver.ga_best_makespans))
            self.assertNotEqual(0, len(solver.ga_avg_population_makespans))
            self.assertNotEqual(0, len(solver.ga_min_makespan_coordinates))

            # output results
            solver.output_benchmark_results(self.tmp_dir, name='test_benchmark', auto_open=False)

            self.assertTrue(os.path.exists(self.tmp_dir + '/test_benchmark'))

        except Exception as e:
            self.fail("Unexpected exception raised:" + str(e))


if __name__ == '__main__':
    unittest.main()
