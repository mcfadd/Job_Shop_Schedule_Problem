import unittest

from JSSP import Solver
from tests.util import csv_data, tmp_dir, rm_tree, random_string


class TestSolverOutputBenchmark(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = Solver(csv_data)
        self.output_dir = tmp_dir / random_string()

    @classmethod
    def tearDownClass(cls) -> None:
        if tmp_dir.exists():
            rm_tree(tmp_dir)

    def test_no_run(self):
        try:
            self.solver.output_benchmark_results(self.output_dir)
            self.fail("UserWarning should have been raised")
        except UserWarning as e:
            self.assertEqual("Solver's agents were None. You need to run at least one optimization function.", str(e),
                             "warning message does not match")

    def test_no_benchmark_run(self):
        try:
            self.solver.genetic_algorithm_iter(1)
            self.solver.tabu_search_iter(1)
            self.solver.output_benchmark_results(self.output_dir)
            self.fail("UserWarning should have been raised")
        except UserWarning as e:
            self.assertEqual("You must run one of the optimization functions in benchmark mode.", str(e),
                             "warning message does not match")

    def test_ga_benchmark_ts_None(self):
        self.assertFalse(self.output_dir.exists())

        self.solver.genetic_algorithm_iter(1, benchmark=True)
        self.solver.output_benchmark_results(self.output_dir, auto_open=False)

        self.assertTrue(self.output_dir.exists())

    def test_ts_benchmark_ga_None(self):
        self.assertFalse(self.output_dir.exists())
        
        self.solver.tabu_search_iter(1, benchmark=True)
        self.solver.output_benchmark_results(self.output_dir, auto_open=False)

        self.assertTrue(self.output_dir.exists())

    def test_ga_benchmark_ts_not_None(self):
        self.assertFalse(self.output_dir.exists())

        self.solver.genetic_algorithm_iter(1, benchmark=True)
        self.solver.tabu_search_iter(1)
        self.solver.output_benchmark_results(self.output_dir, auto_open=False)

        self.assertTrue(self.output_dir.exists())

    def test_ts_benchmark_ga_not_None(self):
        self.assertFalse(self.output_dir.exists())

        self.solver.genetic_algorithm_iter(1)
        self.solver.tabu_search_iter(1, benchmark=True)
        self.solver.output_benchmark_results(self.output_dir, auto_open=False)
        
        self.assertTrue(self.output_dir.exists())


if __name__ == '__main__':
    unittest.main()
