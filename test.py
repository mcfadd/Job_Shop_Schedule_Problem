from data_set import Operation
from makespan import *
from tabu_search import Neighborhood
import unittest

"""
This Unit Test contains test cases that do the following: 

1. tests equality of Operation objects
2. tests equality of Solution objects
3. ensures a Neighborhood object cannot add duplicate Solutions
4. ensures a InfeasibleSolutionException is raised when an infeasible operation list is passed to Solution constructor   

Note: the tests have been created using the smallest problem instance (i.e. data set) in the repository.
"""
Data.read_data_from_files('data/sequenceDependencyMatrix.csv', 'data/machineRunSpeed.csv', 'data/jobTasks.csv')


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
        self.assertEqual(Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                   Operation(task=Data.get_job(0).get_task(1), machine=1),
                                   Operation(task=Data.get_job(1).get_task(0), machine=1),
                                   Operation(task=Data.get_job(2).get_task(0), machine=0),
                                   Operation(task=Data.get_job(1).get_task(1), machine=0)]),
                         Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                   Operation(task=Data.get_job(0).get_task(1), machine=1),
                                   Operation(task=Data.get_job(1).get_task(0), machine=1),
                                   Operation(task=Data.get_job(2).get_task(0), machine=0),
                                   Operation(task=Data.get_job(1).get_task(1), machine=0)]),
                         "These two Solutions should be equal"
                         )

        self.assertNotEqual(Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                      Operation(task=Data.get_job(0).get_task(1), machine=1),
                                      Operation(task=Data.get_job(1).get_task(0), machine=1),
                                      Operation(task=Data.get_job(2).get_task(0), machine=0),
                                      Operation(task=Data.get_job(1).get_task(1), machine=0)]),
                            Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                      Operation(task=Data.get_job(0).get_task(1), machine=1),
                                      Operation(task=Data.get_job(1).get_task(0), machine=1),
                                      Operation(task=Data.get_job(2).get_task(0), machine=0),
                                      Operation(task=Data.get_job(1).get_task(1), machine=1)]),
                            "These two Solutions should not be equal"
                            )

    def test_infeasible_solution(self):
        try:

            Solution([Operation(task=Data.get_job(0).get_task(1), machine=0),
                      Operation(task=Data.get_job(0).get_task(0), machine=1),
                      Operation(task=Data.get_job(1).get_task(0), machine=1),
                      Operation(task=Data.get_job(2).get_task(0), machine=0),
                      Operation(task=Data.get_job(1).get_task(1), machine=0)])

            self.assertTrue(False, "Failed to raise InfeasibleSolutionException")

        except InfeasibleSolutionException:
            pass

    def test_neighborhood_class(self):
        neighborhood = Neighborhood()   # create new Neighborhood

        neighborhood.add(Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                   Operation(task=Data.get_job(0).get_task(1), machine=1),
                                   Operation(task=Data.get_job(1).get_task(0), machine=1),
                                   Operation(task=Data.get_job(2).get_task(0), machine=0),
                                   Operation(task=Data.get_job(1).get_task(1), machine=0)]))

        # make sure Solution was added
        self.assertEqual(neighborhood.size, 1, "")
        neighborhood.add(Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                   Operation(task=Data.get_job(0).get_task(1), machine=1),
                                   Operation(task=Data.get_job(1).get_task(0), machine=1),
                                   Operation(task=Data.get_job(2).get_task(0), machine=0),
                                   Operation(task=Data.get_job(1).get_task(1), machine=0)]))

        # make sure duplicate Solution was not added
        self.assertEqual(neighborhood.size, 1, "")
        neighborhood.add(Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                                   Operation(task=Data.get_job(0).get_task(1), machine=1),
                                   Operation(task=Data.get_job(1).get_task(0), machine=1),
                                   Operation(task=Data.get_job(1).get_task(1), machine=0),
                                   Operation(task=Data.get_job(2).get_task(0), machine=0)]))

        # make sure last Solution was added
        self.assertEqual(neighborhood.size, 2, "")


if __name__ == '__main__':
    unittest.main()
