import unittest

from JSSP.solver import Solver
from tests.util import tmp_dir, csv_data, rm_tree


class TestTS(unittest.TestCase):

    def setUp(self) -> None:
        if not tmp_dir.exists():
            tmp_dir.mkdir()

    def tearDown(self) -> None:
        rm_tree(tmp_dir)

    def test_ts_time(self):
        runtime = 5  # seconds
        num_solutions_per_process = 1
        num_processes = 2
        tabu_list_size = 50
        neighborhood_size = 200
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        solver = Solver(csv_data)
        solver.tabu_search_time(runtime,
                                num_solutions_per_process=num_solutions_per_process,
                                num_processes=num_processes,
                                tabu_list_size=tabu_list_size,
                                neighborhood_size=neighborhood_size,
                                neighborhood_wait=neighborhood_wait,
                                probability_change_machine=probability_change_machine
                                )

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ts_agent_list)

        # test parameters were set
        self.assertEqual(len(solver.ts_agent_list), num_processes)
        for ts_agent in solver.ts_agent_list:
            self.assertEqual(runtime, ts_agent.runtime)
            self.assertTrue(ts_agent.time_condition)
            self.assertFalse(ts_agent.benchmark)
            self.assertEqual(num_solutions_per_process, ts_agent.num_solutions_to_find)
            self.assertEqual(tabu_list_size, ts_agent.tabu_list_size)
            self.assertEqual(neighborhood_size, ts_agent.neighborhood_size)
            self.assertEqual(neighborhood_wait, ts_agent.neighborhood_wait)
            self.assertEqual(probability_change_machine, ts_agent.probability_change_machine)

        # output results
        output_file = tmp_dir / 'ts_test_schedule.xlsx'
        solver.solution.create_schedule_xlsx_file(output_file)
        self.assertTrue(output_file.exists(), "ts_test_schedule.xlsx was not produced")

    def test_ts_time_benchmark(self):
        runtime = 5  # seconds
        num_solutions_per_process = 1
        num_processes = 2
        tabu_list_size = 50
        neighborhood_size = 200
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        solver = Solver(csv_data)
        solver.tabu_search_time(runtime,
                                num_solutions_per_process=num_solutions_per_process,
                                num_processes=num_processes,
                                tabu_list_size=tabu_list_size,
                                neighborhood_size=neighborhood_size,
                                neighborhood_wait=neighborhood_wait,
                                probability_change_machine=probability_change_machine,
                                benchmark=True)

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ts_agent_list)

        # test parameters were set
        self.assertEqual(len(solver.ts_agent_list), num_processes)
        for ts_agent in solver.ts_agent_list:
            self.assertEqual(runtime, ts_agent.runtime)
            self.assertTrue(ts_agent.time_condition)
            self.assertTrue(ts_agent.benchmark)
            self.assertEqual(num_solutions_per_process, ts_agent.num_solutions_to_find)
            self.assertEqual(tabu_list_size, ts_agent.tabu_list_size)
            self.assertEqual(neighborhood_size, ts_agent.neighborhood_size)
            self.assertEqual(neighborhood_wait, ts_agent.neighborhood_wait)
            self.assertEqual(probability_change_machine, ts_agent.probability_change_machine)

            # test benchmark results were produced
            self.assertNotEqual(0, ts_agent.benchmark_iterations)
            self.assertNotEqual(0, len(ts_agent.neighborhood_size_v_iter))
            self.assertNotEqual(0, len(ts_agent.seed_solution_makespan_v_iter))
            self.assertNotEqual(0, len(ts_agent.tabu_size_v_iter))
            self.assertNotEqual((0, 0), ts_agent.min_makespan_coordinates)

        # output results
        output_file = tmp_dir / 'ts_test_benchmark'
        solver.output_benchmark_results(output_file, auto_open=False)
        self.assertTrue(output_file.exists(), "TS benchmark results were not produced")

    def test_ts_iter(self):
        try:
            iterations = 50
            num_solutions_per_process = 1
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8

            solver = Solver(csv_data)
            solver.tabu_search_iter(iterations,
                                    num_solutions_per_process=num_solutions_per_process,
                                    num_processes=num_processes,
                                    tabu_list_size=tabu_list_size,
                                    neighborhood_size=neighborhood_size,
                                    neighborhood_wait=neighborhood_wait,
                                    probability_change_machine=probability_change_machine
                                    )
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ts_agent_list)

        # test parameters were set
        self.assertEqual(len(solver.ts_agent_list), num_processes)
        for ts_agent in solver.ts_agent_list:
            self.assertEqual(iterations, ts_agent.iterations)
            self.assertFalse(ts_agent.time_condition)
            self.assertFalse(ts_agent.benchmark)
            self.assertEqual(num_solutions_per_process, ts_agent.num_solutions_to_find)
            self.assertEqual(tabu_list_size, ts_agent.tabu_list_size)
            self.assertEqual(neighborhood_size, ts_agent.neighborhood_size)
            self.assertEqual(neighborhood_wait, ts_agent.neighborhood_wait)
            self.assertEqual(probability_change_machine, ts_agent.probability_change_machine)

        # output results
        output_file = tmp_dir / 'ts_test_schedule.xlsx'
        solver.solution.create_schedule_xlsx_file(output_file)
        self.assertTrue(output_file.exists(), "ts_test_schedule.xlsx was not produced")

    def test_ts_iter_benchmark(self):
        try:
            iterations = 50
            num_solutions_per_process = 1
            num_processes = 2
            tabu_list_size = 50
            neighborhood_size = 200
            neighborhood_wait = 0.1
            probability_change_machine = 0.8

            solver = Solver(csv_data)
            solver.tabu_search_iter(iterations,
                                    num_solutions_per_process=num_solutions_per_process,
                                    num_processes=num_processes,
                                    tabu_list_size=tabu_list_size,
                                    neighborhood_size=neighborhood_size,
                                    neighborhood_wait=neighborhood_wait,
                                    probability_change_machine=probability_change_machine,
                                    benchmark=True)
        except Exception as e:
            self.fail('Unexpected exception raised:' + str(e))

        self.assertIsNotNone(solver.solution)
        self.assertIsNotNone(solver.ts_agent_list)

        # test parameters were set
        self.assertEqual(len(solver.ts_agent_list), num_processes)
        for ts_agent in solver.ts_agent_list:
            self.assertEqual(iterations, ts_agent.iterations)
            self.assertFalse(ts_agent.time_condition)
            self.assertTrue(ts_agent.benchmark)
            self.assertEqual(num_solutions_per_process, ts_agent.num_solutions_to_find)
            self.assertEqual(tabu_list_size, ts_agent.tabu_list_size)
            self.assertEqual(neighborhood_size, ts_agent.neighborhood_size)
            self.assertEqual(neighborhood_wait, ts_agent.neighborhood_wait)
            self.assertEqual(probability_change_machine, ts_agent.probability_change_machine)

            # test benchmark results were produced
            self.assertNotEqual(0, ts_agent.benchmark_iterations)
            self.assertNotEqual(0, len(ts_agent.neighborhood_size_v_iter))
            self.assertNotEqual(0, len(ts_agent.seed_solution_makespan_v_iter))
            self.assertNotEqual(0, len(ts_agent.tabu_size_v_iter))
            self.assertNotEqual((0, 0), ts_agent.min_makespan_coordinates)

        # output results
        output_file = tmp_dir / 'ts_test_benchmark'
        solver.output_benchmark_results(output_file, auto_open=False)
        self.assertTrue(output_file.exists(), "TS benchmark results were not produced")

    def test_ts_multiple_solutions_per_process(self):
        iterations = 10
        tabu_list_size = 50
        neighborhood_size = 200
        neighborhood_wait = 0.1
        probability_change_machine = 0.8

        num_processes_list = [1, 2, 3, 4]
        num_solutions_per_process_list = [1, 2, 3, 4, 5]

        for num_processes in num_processes_list:
            for num_solutions_per_process in num_solutions_per_process_list:
                solver = Solver(csv_data)
                solver.tabu_search_iter(iterations,
                                        num_solutions_per_process=num_solutions_per_process,
                                        num_processes=num_processes,
                                        tabu_list_size=tabu_list_size,
                                        neighborhood_size=neighborhood_size,
                                        neighborhood_wait=neighborhood_wait,
                                        probability_change_machine=probability_change_machine
                                        )

                self.assertIsNotNone(solver.solution)
                self.assertIsNotNone(solver.ts_agent_list)

                # test parameters were set
                self.assertEqual(len(solver.ts_agent_list), num_processes)
                for ts_agent in solver.ts_agent_list:
                    self.assertEqual(iterations, ts_agent.iterations)
                    self.assertFalse(ts_agent.time_condition)
                    self.assertFalse(ts_agent.benchmark)
                    self.assertEqual(num_solutions_per_process, ts_agent.num_solutions_to_find)
                    self.assertEqual(tabu_list_size, ts_agent.tabu_list_size)
                    self.assertEqual(neighborhood_size, ts_agent.neighborhood_size)
                    self.assertEqual(neighborhood_wait, ts_agent.neighborhood_wait)
                    self.assertEqual(probability_change_machine, ts_agent.probability_change_machine)

                all_solutions = []
                for ts_agent in solver.ts_agent_list:
                    all_solutions += ts_agent.all_solutions

                self.assertEqual(len(all_solutions), num_processes * num_solutions_per_process,
                                 f"Parallel TS should have produced {num_processes * num_solutions_per_process} solutions")


if __name__ == '__main__':
    unittest.main()
