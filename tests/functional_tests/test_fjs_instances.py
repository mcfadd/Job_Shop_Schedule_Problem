import random
import unittest

from JSSP import data
from JSSP.solver import Solver
from tests.util import project_root, tmp_dir, get_files_with_suffix, rm_tree

fjs_data = get_files_with_suffix(project_root / 'data/fjs_data', '.fjs')
fjs_data = random.choices(fjs_data, k=20)


class TestFJSOptimization(unittest.TestCase):

    def setUp(self) -> None:
        if not tmp_dir.exists():
            tmp_dir.mkdir()

    def tearDown(self) -> None:
        rm_tree(tmp_dir)

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
                                        probability_change_machine=probability_change_machine)

            except Exception as e:
                self.fail(f'Unexpected exception raised while running TS for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution, "TS should have produced a best solution")

            # output results
            output_file = tmp_dir / 'fjs_ts_schedule.xlsx'
            solver.solution.create_schedule_xlsx_file(output_file)
            self.assertTrue(output_file.exists(), "fjs_ts_schedule.xlsx was not produced")

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
                                        probability_change_machine=probability_change_machine,
                                        benchmark=True)

            except Exception as e:
                self.fail(f'Unexpected exception raised while running TS for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution, "TS should have produced a best solution")

            # output results
            output_file = tmp_dir / 'fjs_ts_benchmark'
            solver.output_benchmark_results(output_file, auto_open=False)
            self.assertTrue(output_file.exists(), "fjs_ts_benchmark was not produced")

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
            output_file = tmp_dir / 'fjs_ga_schedule.xlsx'
            solver.solution.create_schedule_xlsx_file(output_file)
            self.assertTrue(output_file.exists(), "fjs_ga_schedule.xlsx was not produced")

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
                                              selection_size=selection_size,
                                              benchmark=True)
            except Exception as e:
                self.fail(f'Unexpected exception raised while running GA for {fjs_instance}:' + str(e))

            self.assertIsNotNone(solver.solution)
            self.assertIsNotNone(solver.ga_agent)

            # test parameters were set
            self.assertEqual(iterations, solver.ga_agent.iterations)
            self.assertFalse(solver.ga_agent.time_condition)
            self.assertTrue(solver.ga_agent.benchmark)
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
            output_file = tmp_dir / 'fjs_ga_benchmark'
            solver.output_benchmark_results(output_file, auto_open=False)
            self.assertTrue(output_file.exists(), "fjs_ga_benchmark was not produced")


if __name__ == '__main__':
    unittest.main()
