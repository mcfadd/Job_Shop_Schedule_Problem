import pickle
import unittest

import numpy as np
import JSSP.cython_files.makespan_compiled.InfeasibleSolutionException  # the error can be ignored as long as makespan_compiled has been built

import JSSP.solution as solution
import JSSP.data.Data as Data

"""
This Unit Test contains test cases that do the following: 

1. test Solution equality
2. test Solution inequality
3. test Solution less than
4. test Solution greater than 
5. test sorting Solutions
6. test InfeasibleSolutionException is raised when an infeasible operation list is passed to Solution()
7. test IncompleteSolutionException is raised when an incomplete operation list is passed to Solution()   
8. test that generate_feasible_solution() does not generate infeasible solutions
9. test pickling a Solution to a file
"""
Data.initialize_data_from_csv('../data/data_set2/sequenceDependencyMatrix.csv', '../data/data_set2/machineRunSpeed.csv',
                     '../data/data_set2/jobTasks.csv')


class Test(unittest.TestCase):

    def test_solution_equality(self):

        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.Solution(solution_obj1.operation_2d_array)

        self.assertEqual(solution_obj1, solution_obj2, "These two Solutions should be equal")

    def test_solution_inequality(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.generate_feasible_solution()

        self.assertNotEqual(solution_obj1, solution_obj2, "These two Solutions should not be equal")

    def test_solution_lt(self):
        solution_obj1 = solution.generate_feasible_solution()
        solution_obj2 = solution.Solution(solution_obj1.operation_2d_array)
        solution_obj2.makespan -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

        solution_obj2.makespan += 1
        solution_obj2.machine_makespans[0] -= 1

        self.assertLess(solution_obj2, solution_obj1, "solution_obj2 should be less than solution_obj1")

    def test_solution_gt(self):
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

        except InfeasibleSolutionException:
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

        except InfeasibleSolutionException:
            self.assertTrue(False, "Infeasible solution was generated")

    def test_pickle_to_file(self):

        solution_obj = solution.generate_feasible_solution()
        solution_obj.pickle_to_file('./test_solution.pkl')

        with open('./test_solution.pkl', 'rb') as fin:
            solution_obj_pickled = pickle.load(fin)

        self.assertEqual(solution_obj, solution_obj_pickled, "The pickled solution should be equal to solution_obj")
        solution_obj.makespan -= 1
        self.assertNotEqual(solution_obj, solution_obj_pickled, "The pickled solution should not be equal to solution_obj")


if __name__ == '__main__':
    unittest.main()
