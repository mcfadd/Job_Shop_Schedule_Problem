import pickle
import unittest

import numpy as np

from JSSP.exception import IncompleteSolutionException, InfeasibleSolutionException
from JSSP.solution import Solution
from tests.util import tmp_dir, rm_tree, csv_data_solution_factory, csv_data


class TestSolution(unittest.TestCase):

    def test_solution_equality(self):
        solution_obj1 = csv_data_solution_factory.get_solution()
        solution_obj2 = Solution(csv_data, solution_obj1.operation_2d_array)

        self.assertEqual(solution_obj1, solution_obj2, "These two solution.Solutions should be equal")

    def test_solution_inequality(self):
        solution_obj1 = csv_data_solution_factory.get_solution()
        solution_obj2 = csv_data_solution_factory.get_solution()

        self.assertNotEqual(solution_obj1, solution_obj2, "These two solution.Solutions should not be equal")

    def test_solution_less_than(self):
        solution_obj1 = csv_data_solution_factory.get_solution()
        solution_obj2 = Solution(csv_data, solution_obj1.operation_2d_array)
        solution_obj2.makespan -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

        solution_obj2.makespan += 1
        solution_obj2.machine_makespans[0] -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

    def test_solution_greater_than(self):
        solution_obj1 = csv_data_solution_factory.get_solution()
        solution_obj2 = Solution(csv_data, solution_obj1.operation_2d_array)
        solution_obj2.makespan -= 1

        self.assertGreater(solution_obj1, solution_obj2, "solution_obj2 should be greater than solution_obj1")

        solution_obj2.makespan += 1
        solution_obj2.machine_makespans[0] -= 1

        self.assertGreater(solution_obj1, solution_obj2, "solution_obj2 should be greater than solution_obj1")

    def test_sorting_solutions(self):
        lst = sorted(csv_data_solution_factory.get_n_solutions(50))
        for i in range(1, len(lst)):
            self.assertLess(lst[i - 1], lst[i], "lst should be in sorted order")

    def test_solution_in_list(self):
        sol1 = csv_data_solution_factory.get_solution()
        sol2 = Solution(csv_data, sol1.operation_2d_array)
        lst = [sol1]
        self.assertIn(sol2, lst)

    def test_infeasible_solution(self):
        try:
            solution_obj = csv_data_solution_factory.get_solution()
            solution_obj.operation_2d_array[[0, 200]] = solution_obj.operation_2d_array[[200, 0]]
            Solution(csv_data, solution_obj.operation_2d_array)

            self.fail("Failed to raise solution.InfeasibleSolutionException")

        except InfeasibleSolutionException:
            pass

    def test_incomplete_solution(self):
        try:
            solution_obj = csv_data_solution_factory.get_solution()
            Solution(csv_data, np.delete(solution_obj.operation_2d_array, 0, axis=0))

            self.fail("Failed to raise solution.IncompleteSolutionException")

        except IncompleteSolutionException:
            pass


class TestPicklingSolution(unittest.TestCase):

    def setUp(self) -> None:
        if not tmp_dir.exists():
            tmp_dir.mkdir()

    def tearDown(self) -> None:
        rm_tree(tmp_dir)

    def test_pickle_to_file(self):
        solution_obj = csv_data_solution_factory.get_solution()
        with open(tmp_dir / 'test_solution.pkl', 'wb') as fout:
            pickle.dump(solution_obj, fout)

        self.assertTrue((tmp_dir / 'test_solution.pkl').exists(), "The pickled solution does not exist")

        with open(tmp_dir / 'test_solution.pkl', 'rb') as fin:
            solution_obj_pickled = pickle.load(fin)

        self.assertEqual(solution_obj, solution_obj_pickled, "The pickled solution should be equal to solution_obj")


if __name__ == '__main__':
    unittest.main()
