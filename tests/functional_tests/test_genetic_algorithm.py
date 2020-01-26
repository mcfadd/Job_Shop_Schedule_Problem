import os
import shutil
import unittest

from JSSP import data
from JSSP.genetic_algorithm import GASelectionEnum
from JSSP.solver import Solver
from tests import project_root, tmp_dir


class TestGA(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        self.data = data.CSVData(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_ga_time(self):
        try:
            runtime = 5  # seconds
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver(self.data)
            solver.genetic_algorithm_time(runtime=runtime,
                                          population=population,
                                          population_size=population_size,
                                          mutation_probability=mutation_probability,
                                          selection_size=selection_size)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ga_agent)

        # test parameters were set
        self.assertEqual(runtime, solver.ga_agent.runtime)
        self.assertTrue(solver.ga_agent.time_condition)
        self.assertFalse(solver.ga_agent.benchmark)
        self.assertEqual(population_size, solver.ga_agent.population_size)
        self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
        self.assertEqual(selection_size, solver.ga_agent.selection_size)

        self.assertNotEqual(0, len(solver.ga_agent.initial_population))
        self.assertNotEqual(0, len(solver.ga_agent.result_population))
        self.assertEqual(len(solver.ga_agent.initial_population), len(solver.ga_agent.result_population))

        # test that the result solution is better than all the solutions in the initial population
        for initial_sol in solver.ga_agent.initial_population:
            self.assertLessEqual(solver.solution, initial_sol)

        # output results
        solver.solution.create_schedule_xlsx_file(tmp_dir + os.sep + 'ga_test_schedule')
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_schedule.xlsx'),
                        "ga_test_schedule.xlsx was not produced")

    def test_ga_time_benchmark(self):
        try:
            runtime = 5  # seconds
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver(self.data)
            solver.genetic_algorithm_time(runtime=runtime,
                                          population=population,
                                          population_size=population_size,
                                          mutation_probability=mutation_probability,
                                          selection_size=selection_size,
                                          benchmark=True)
        except Exception as e:
            self.fail("Unexpected exception raised:" + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ga_agent)

        # test parameters were set
        self.assertEqual(runtime, solver.ga_agent.runtime)
        self.assertTrue(solver.ga_agent.time_condition)
        self.assertTrue(solver.ga_agent.benchmark)
        self.assertEqual(population_size, solver.ga_agent.population_size)
        self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
        self.assertEqual(selection_size, solver.ga_agent.selection_size)

        self.assertNotEqual(0, len(solver.ga_agent.initial_population))
        self.assertNotEqual(0, len(solver.ga_agent.result_population))
        self.assertEqual(len(solver.ga_agent.initial_population), len(solver.ga_agent.result_population))

        # test that the result solution is better than all the solutions in the initial population
        for initial_sol in solver.ga_agent.initial_population:
            self.assertLessEqual(solver.solution, initial_sol)

        # test benchmark results were produced
        self.assertNotEqual(0, len(solver.ga_agent.best_solution_makespan_v_iter))
        self.assertNotEqual(0, len(solver.ga_agent.avg_population_makespan_v_iter))
        self.assertNotEqual(0, len(solver.ga_agent.min_makespan_coordinates))

        # output results
        solver.output_benchmark_results(tmp_dir, name='ga_test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark'),
                        "GA benchmark results were not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'index.html'),
                        "GA benchmark results index.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'ga_makespans.html'),
                        "GA benchmark results ga_makespans.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'ga_schedule.xlsx'),
                        "GA benchmark results ga_schedule.xlsx was not produced")

    def test_ga_iter(self):
        try:
            iterations = 50
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver(self.data)
            solver.genetic_algorithm_iter(iterations=iterations,
                                          population=population,
                                          population_size=population_size,
                                          mutation_probability=mutation_probability,
                                          selection_size=selection_size)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ga_agent)

        # test parameters were set
        self.assertEqual(iterations, solver.ga_agent.iterations)
        self.assertFalse(solver.ga_agent.time_condition)
        self.assertFalse(solver.ga_agent.benchmark)
        self.assertEqual(population_size, solver.ga_agent.population_size)
        self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
        self.assertEqual(selection_size, solver.ga_agent.selection_size)

        self.assertNotEqual(0, len(solver.ga_agent.initial_population))
        self.assertNotEqual(0, len(solver.ga_agent.result_population))
        self.assertEqual(len(solver.ga_agent.initial_population), len(solver.ga_agent.result_population))

        # test that the result solution is better than all the solutions in the initial population
        for initial_sol in solver.ga_agent.initial_population:
            self.assertLessEqual(solver.solution, initial_sol)

        # output results
        solver.solution.create_schedule_xlsx_file(tmp_dir + os.sep + 'ga_test_schedule')
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_schedule.xlsx'),
                        "ga_test_schedule.xlsx was not produced")

    def test_ga_iter_benchmark(self):
        try:
            iterations = 50
            population = None
            population_size = 100
            mutation_probability = 0.8
            selection_size = 5

            solver = Solver(self.data)
            solver.genetic_algorithm_iter(iterations=iterations,
                                          population=population,
                                          population_size=population_size,
                                          mutation_probability=mutation_probability,
                                          selection_size=selection_size,
                                          benchmark=True)
        except Exception as e:
            self.fail("Unexpected exception raised:" + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ga_agent)

        # test parameters were set
        self.assertEqual(iterations, solver.ga_agent.iterations)
        self.assertFalse(solver.ga_agent.time_condition)
        self.assertTrue(solver.ga_agent.benchmark)
        self.assertEqual(population_size, solver.ga_agent.population_size)
        self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
        self.assertEqual(selection_size, solver.ga_agent.selection_size)

        self.assertNotEqual(0, len(solver.ga_agent.initial_population))
        self.assertNotEqual(0, len(solver.ga_agent.result_population))
        self.assertEqual(len(solver.ga_agent.initial_population), len(solver.ga_agent.result_population))

        # test that the result solution is better than all the solutions in the initial population
        for initial_sol in solver.ga_agent.initial_population:
            self.assertLessEqual(solver.solution, initial_sol)

        # test benchmark results were produced
        self.assertNotEqual(0, len(solver.ga_agent.best_solution_makespan_v_iter))
        self.assertNotEqual(0, len(solver.ga_agent.avg_population_makespan_v_iter))
        self.assertNotEqual(0, len(solver.ga_agent.min_makespan_coordinates))

        # # output results
        solver.output_benchmark_results(tmp_dir, name='ga_test_benchmark', auto_open=False)
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark'),
                        "GA benchmark results were not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'index.html'),
                        "GA benchmark results index.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'ga_makespans.html'),
                        "GA benchmark results ga_makespans.html was not produced")
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'ga_test_benchmark' + os.sep + 'ga_schedule.xlsx'),
                        "GA benchmark results ga_schedule.xlsx was not produced")


class TestGASelectionMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.data = data.CSVData(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def test_tournament_selection(self):
        test_selection(self, GASelectionEnum.TOURNAMENT, self.data)

    def test_fitness_proportionate_selection(self):
        test_selection(self, GASelectionEnum.FITNESS_PROPORTIONATE, self.data)

    def test_random_selection(self):
        test_selection(self, GASelectionEnum.RANDOM, self.data)


def test_selection(unit_test, selection_method, instance_data):
    try:
        iterations = 50
        population = None
        population_size = 100
        mutation_probability = 0.8

        # run GA
        solver = Solver(instance_data)
        solver.genetic_algorithm_iter(iterations=iterations,
                                      population=population,
                                      population_size=population_size,
                                      selection_method_enum=selection_method,
                                      mutation_probability=mutation_probability,
                                      selection_size=2 if selection_method is not GASelectionEnum.TOURNAMENT else 5)
    except Exception as e:
        unit_test.fail('Unexpected exception raised:' + str(e))

    unit_test.assertIsNotNone(solver.solution)
    unit_test.assertIsNotNone(solver.ga_agent)

    # test parameters were set
    unit_test.assertEqual(iterations, solver.ga_agent.iterations)
    unit_test.assertFalse(solver.ga_agent.time_condition)
    unit_test.assertFalse(solver.ga_agent.benchmark)
    unit_test.assertEqual(population_size, solver.ga_agent.population_size)
    unit_test.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
    unit_test.assertEqual(selection_method, solver.ga_agent.selection_method)

    unit_test.assertNotEqual(0, len(solver.ga_agent.initial_population))
    unit_test.assertNotEqual(0, len(solver.ga_agent.result_population))
    unit_test.assertEqual(len(solver.ga_agent.initial_population), len(solver.ga_agent.result_population))

    # test that the result solution is better than all the solutions in the initial population
    for initial_sol in solver.ga_agent.initial_population:
        unit_test.assertLessEqual(solver.solution, initial_sol)

    # test that the result population does not have duplicate solutions
    seen = []
    unit_test.assertFalse(any(sol in seen or seen.append(sol) for sol in solver.ga_agent.result_population))


if __name__ == '__main__':
    unittest.main()
