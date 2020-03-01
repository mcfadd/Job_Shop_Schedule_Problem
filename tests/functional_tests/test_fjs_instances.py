import os
import random
import shutil
import unittest

from JSSP import data
from JSSP.solver import Solver
from tests import tmp_dir, get_all_fjs_files

# directory used by tests
fjs_data = random.choices(get_all_fjs_files(), k=20)


class TestFJSOptimization(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir)

    def test_ts_iter(self):
        # parameters
        iterations = 50  # keep this value small
        num_processes = 1
        tabu_list_size = 10
        neighborhood_size = 25
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        for i, fjs_instance in enumerate(fjs_data):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_data)})")
            try:
                data_instance = data.FJSData(fjs_instance)

                solver = Solver(data_instance)
                solver.tabu_search_iter(iterations,
                                        num_solutions_per_process=1,
                                        num_processes=num_processes,
                                        tabu_list_size=tabu_list_size,
                                        neighborhood_size=neighborhood_size,
                                        neighborhood_wait=neighborhood_wait,
                                        probability_change_machine=probability_change_machine
                                        )

            except Exception as e:
                self.fail(f'Unexpected exception raised while running TS for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution, "TS should have produced a best solution")

            # output results
            solver.solution.create_schedule_xlsx_file(tmp_dir + os.sep + 'fjs_ts_schedule')
            self.assertTrue(os.path.exists(tmp_dir + os.sep + 'fjs_ts_schedule.xlsx'),
                            "fjs_ts_schedule.xlsx was not produced")

    def test_ts_iter_benchmark(self):
        # parameters
        iterations = 50  # keep this value small
        num_processes = 1
        tabu_list_size = 10
        neighborhood_size = 25
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        for i, fjs_instance in enumerate(fjs_data):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_data)})")
            try:
                data_instance = data.FJSData(fjs_instance)

                solver = Solver(data_instance)
                solver.tabu_search_iter(iterations,
                                        num_solutions_per_process=1,
                                        num_processes=num_processes,
                                        tabu_list_size=tabu_list_size,
                                        neighborhood_size=neighborhood_size,
                                        neighborhood_wait=neighborhood_wait,
                                        probability_change_machine=probability_change_machine
                                        )

            except Exception as e:
                self.fail(f'Unexpected exception raised while running TS for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution, "TS should have produced a best solution")

            # output results
            solver.output_benchmark_results(tmp_dir, name='fjs_ts_benchmark')
            self.assertTrue(os.path.exists(tmp_dir + os.sep + 'fjs_ts_benchmark'),
                            "fjs_ts_benchmark was not produced")

    def test_ga_iter(self):
        # parameters
        iterations = 10  # keep this value small
        population_size = 50  # keep this value small
        mutation_probability = 0.8
        selection_size = 5

        for i, fjs_instance in enumerate(fjs_data):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_data)})")
            try:
                data_instance = data.FJSData(fjs_instance)

                # run GA
                solver = Solver(data_instance)
                solver.genetic_algorithm_iter(iterations=iterations,
                                              population_size=population_size,
                                              mutation_probability=mutation_probability,
                                              selection_size=selection_size)
            except Exception as e:
                self.fail(f'Unexpected exception raised while running GA for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution)
            self.assertIsNotNone(solver.ga_agent)

            # test parameters were set
            self.assertEqual(iterations, solver.ga_agent.iterations)
            self.assertFalse(solver.ga_agent.time_condition)
            self.assertFalse(solver.ga_agent.benchmark)
            self.assertEqual(population_size, solver.ga_agent.population_size)
            self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
            self.assertEqual(selection_size, solver.ga_agent.selection_size)

            self.assertEqual(population_size, len(solver.ga_agent.initial_population))
            self.assertEqual(population_size, len(solver.ga_agent.result_population))

            # test that the result solution is better than all the solutions in the initial population
            for initial_sol in solver.ga_agent.initial_population:
                self.assertLessEqual(solver.solution, initial_sol)

            # test that the result population does not have duplicate solutions
            seen = []
            self.assertTrue(not any(sol in seen or seen.append(sol) for sol in solver.ga_agent.result_population))

            # output results
            solver.solution.create_schedule_xlsx_file(tmp_dir + os.sep + 'fjs_ga_schedule')
            self.assertTrue(os.path.exists(tmp_dir + os.sep + 'fjs_ga_schedule.xlsx'),
                            "fjs_ga_schedule.xlsx was not produced")

    def test_ga_iter_benchmark(self):
        # parameters
        iterations = 10  # keep this value small
        population_size = 50  # keep this value small
        mutation_probability = 0.8
        selection_size = 5

        for i, fjs_instance in enumerate(fjs_data):
            print(f"testing fjs instance {fjs_instance} ({i + 1} of {len(fjs_data)})")
            try:
                data_instance = data.FJSData(fjs_instance)

                # run GA
                solver = Solver(data_instance)
                solver.genetic_algorithm_iter(iterations=iterations,
                                              population_size=population_size,
                                              mutation_probability=mutation_probability,
                                              selection_size=selection_size)
            except Exception as e:
                self.fail(f'Unexpected exception raised while running GA for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution)
            self.assertIsNotNone(solver.ga_agent)

            # test parameters were set
            self.assertEqual(iterations, solver.ga_agent.iterations)
            self.assertFalse(solver.ga_agent.time_condition)
            self.assertFalse(solver.ga_agent.benchmark)
            self.assertEqual(population_size, solver.ga_agent.population_size)
            self.assertEqual(mutation_probability, solver.ga_agent.mutation_probability)
            self.assertEqual(selection_size, solver.ga_agent.selection_size)

            self.assertEqual(population_size, len(solver.ga_agent.initial_population))
            self.assertEqual(population_size, len(solver.ga_agent.result_population))

            # test that the result solution is better than all the solutions in the initial population
            for initial_sol in solver.ga_agent.initial_population:
                self.assertLessEqual(solver.solution, initial_sol)

            # test that the result population does not have duplicate solutions
            seen = []
            self.assertTrue(not any(sol in seen or seen.append(sol) for sol in solver.ga_agent.result_population))

            # output results
            solver.output_benchmark_results(tmp_dir, name='fjs_ga_benchmark')
            self.assertTrue(os.path.exists(tmp_dir + os.sep + 'fjs_ga_benchmark'),
                            "fjs_ga_benchmark was not produced")


if __name__ == '__main__':
    unittest.main()
