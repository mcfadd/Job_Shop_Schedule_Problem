from data_set import Operation
from makespan import *
from tabu_search import SolutionSet
import unittest

"""
This Unit Test contains test cases that do the following: 

1. test equality of Operation objects
2. test equality of Solution objects
3. test an InfeasibleSolutionException is raised when an infeasible operation list is passed to Solution()
4. test an IncompleteSolutionException is raised when an incomplete operation list is passed to Solution()   
5. test SolutionSet add method
6. test SolutionSet remove method

"""
Data.read_data_from_files('data/data_set1/sequenceDependencyMatrix.csv', 'data/data_set1/machineRunSpeed.csv',
                          'data/data_set1/jobTasks.csv')


class Test(unittest.TestCase):

    def test_operation_equality(self):
        self.assertEqual(Operation(task=Data.get_job(0).get_task(0), machine=0),
                         Operation(task=Data.get_job(0).get_task(0), machine=0),
                         "These two Operations should be equal")

        self.assertNotEqual(Operation(task=Data.get_job(0).get_task(0), machine=0),
                            Operation(task=Data.get_job(0).get_task(1), machine=0),
                            "These two Operations should not be equal")

        self.assertNotEqual(Operation(task=Data.get_job(0).get_task(0), machine=0),
                            Operation(task=Data.get_job(0).get_task(0), machine=1),
                            "These two Operations should not be equal")

    def test_solution_equality(self):
        self.assertEqual(Solution([[0, 0, 0, 1, 10],
                                   [0, 1, 1, 0, 5],
                                   [1, 0, 0, 1, 8],
                                   [2, 0, 0, 0, 8],
                                   [1, 1, 1, 0, 5]]),
                         Solution([[0, 0, 0, 1, 10],
                                   [0, 1, 1, 0, 5],
                                   [1, 0, 0, 1, 8],
                                   [2, 0, 0, 0, 8],
                                   [1, 1, 1, 0, 5]]),
                         "These two Solutions should be equal"
                         )

        self.assertNotEqual(Solution([[0, 0, 0, 1, 10],
                                      [0, 1, 1, 0, 5],
                                      [1, 0, 0, 1, 8],
                                      [2, 0, 0, 0, 8],
                                      [1, 1, 1, 0, 5]]),
                            Solution([[0, 0, 0, 1, 10],
                                      [2, 0, 0, 0, 8],
                                      [0, 1, 1, 0, 5],
                                      [1, 0, 0, 1, 8],
                                      [1, 1, 1, 0, 5]]),
                            "These two Solutions should not be equal"
                            )

    def test_infeasible_solution(self):
        try:

            Solution([[0, 1, 1, 0, 5],
                      [0, 0, 0, 1, 10],
                      [1, 0, 0, 1, 8],
                      [2, 0, 0, 0, 8],
                      [1, 1, 1, 0, 5]])

            self.assertTrue(False, "Failed to raise InfeasibleSolutionException")

        except InfeasibleSolutionException:
            pass

    def test_incomplete_solution(self):
        try:

            Solution([[0, 0, 0, 1, 10],
                      [1, 0, 0, 1, 8],
                      [2, 0, 0, 0, 8],
                      [1, 1, 1, 0, 5]])

            self.assertTrue(False, "Failed to raise IncompleteSolutionException")

        except IncompleteSolutionException:
            pass

    def test_solution_set_add(self):
        solution_set = SolutionSet()

        solution = Solution([[0, 0, 0, 1, 10],
                             [0, 1, 1, 0, 5],
                             [1, 0, 0, 1, 8],
                             [2, 0, 0, 0, 8],
                             [1, 1, 1, 0, 5]])

        solution_set.add(solution)

        # make sure Solution was added
        self.assertTrue(solution_set.contains(solution))

        solution_set.add(solution)

        # make sure duplicate Solution was not added
        self.assertEqual(solution_set.size, 1)
        solution = Solution([[0, 0, 0, 1, 10],
                             [2, 0, 0, 0, 8],
                             [0, 1, 1, 0, 5],
                             [1, 0, 0, 1, 8],
                             [1, 1, 1, 0, 5]])

        solution_set.add(solution)

        # make sure last Solution was added
        self.assertTrue(solution_set.contains(solution))
        self.assertEqual(solution_set.size, 2)

    def test_solution_set_remove(self):
        solution_set = SolutionSet()

        solution = Solution([[0, 0, 0, 1, 10],
                             [0, 1, 1, 0, 5],
                             [1, 0, 0, 1, 8],
                             [2, 0, 0, 0, 8],
                             [1, 1, 1, 0, 5]])

        solution_set.add(solution)

        # make sure Solution was added
        self.assertTrue(solution_set.contains(solution))

        solution_set.remove(solution)

        # make sure solution was removed
        self.assertFalse(solution_set.contains(solution))
        self.assertEqual(solution_set.size, 0)

        self.assertFalse(solution_set.remove(solution))


if __name__ == '__main__':
    unittest.main()
