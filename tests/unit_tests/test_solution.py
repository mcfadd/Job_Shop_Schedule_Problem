import os
import pickle
import shutil
import unittest

import numpy as np

from JSSP import solution
from JSSP.data import Data
from tests import project_root, tmp_dir

"""
Test the following: 

1. solution.Solution equality
2. solution.Solution inequality
3. solution.Solution less than
4. solution.Solution greater than 
5. sorting solution.Solution objects
6. InfeasibleSolutionException is raised when an infeasible operation list is passed to solution.Solution()
7. IncompleteSolutionException is raised when an incomplete operation list is passed to solution.Solution()   
8. solution.generate_feasible_solution() function
9. pickling a solution.Solution object to a file

"""


class TestSolution(unittest.TestCase):

    def setUp(self) -> None:
        Data.initialize_data_from_csv(project_root + '/data/given_data/sequenceDependencyMatrix.csv',
                                      project_root + '/data/given_data/machineRunSpeed.csv',
                                      project_root + '/data/given_data/jobTasks.csv')

    def test_solution_equality(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.Solution(solution_obj1.operation_2d_array)

        self.assertEqual(solution_obj1, solution_obj2, "These two Solutions should be equal")

    def test_solution_inequality(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.generate_feasible_solution()

        self.assertNotEqual(solution_obj1, solution_obj2, "These two Solutions should not be equal")

    def test_solution_less_than(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.Solution(solution_obj1.operation_2d_array)
        solution_obj2.makespan -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

        solution_obj2.makespan += 1
        solution_obj2.machine_makespans[0] -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

    def test_solution_greater_than(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.Solution(solution_obj1.operation_2d_array)
        solution_obj2.makespan -= 1

        self.assertGreater(solution_obj1, solution_obj2, "solution_obj2 should be greater than solution_obj1")

        solution_obj2.makespan += 1
        solution_obj2.machine_makespans[0] -= 1

        self.assertGreater(solution_obj1, solution_obj2, "solution_obj2 should be greater than solution_obj1")

    def test_sorting_solutions(self):
        lst = [solution.generate_feasible_solution() for i in range(50)]
        lst = sorted(lst)
        for i in range(1, len(lst)):
            self.assertLess(lst[i - 1], lst[i], "lst should be in sorted order")

    def test_infeasible_solution(self):
        try:

            solution_obj = solution.generate_feasible_solution()
            solution_obj.operation_2d_array[[0, 200]] = solution_obj.operation_2d_array[[200, 0]]
            solution.Solution(solution_obj.operation_2d_array)

            self.assertTrue(False, "Failed to raise InfeasibleSolutionException")

        except solution.InfeasibleSolutionException:
            pass

    def test_incomplete_solution(self):
        try:

            solution_obj = solution.generate_feasible_solution()
            solution.Solution(np.delete(solution_obj.operation_2d_array, 0, axis=0))

            self.assertTrue(False, "Failed to raise IncompleteSolutionException")

        except solution.IncompleteSolutionException:
            pass

    def test_generate_feasible_solution(self):
        try:
            for i in range(500):
                solution.generate_feasible_solution()

        except solution.InfeasibleSolutionException:
            self.assertTrue(False, "Infeasible solution was generated")


class TestPicklingSolution(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        Data.initialize_data_from_csv(project_root + '/data/given_data/sequenceDependencyMatrix.csv',
                                      project_root + '/data/given_data/machineRunSpeed.csv',
                                      project_root + '/data/given_data/jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_pickle_to_file(self):

        solution_obj = solution.generate_feasible_solution()
        solution_obj.pickle_to_file(tmp_dir + '/test_solution.pkl')

        self.assertTrue(os.path.exists(tmp_dir + '/test_solution.pkl'), "The pickled solution does not exist")

        with open(tmp_dir + '/test_solution.pkl', 'rb') as fin:
            solution_obj_pickled = pickle.load(fin)

        self.assertEqual(solution_obj, solution_obj_pickled, "The pickled solution should be equal to solution_obj")
        solution_obj.makespan -= 1
        self.assertNotEqual(solution_obj, solution_obj_pickled, "The pickled solution should not be equal to solution_obj")


if __name__ == '__main__':
    unittest.main()
