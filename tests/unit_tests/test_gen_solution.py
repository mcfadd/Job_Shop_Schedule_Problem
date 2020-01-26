import os
import random
import unittest

from JSSP import data
from JSSP.exception import InfeasibleSolutionException
from JSSP.solution.factory import _MaxHeapObj, _MinHeapObj, _JobTaskHeap, SolutionFactory
from tests import project_root, get_all_fjs_files


class TestHeap(unittest.TestCase):

    def setUp(self) -> None:
        self.data = data.CSVData(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def test_min_heap_class(self):
        task1 = self.data.jobs[0].get_task(0)
        task2 = self.data.jobs[0].get_task(1)

        min_heap_obj_task1 = _MinHeapObj(self.data, task1)
        min_heap_obj_task2 = _MinHeapObj(self.data, task2)
        self.assertGreater(min_heap_obj_task1, min_heap_obj_task2)

    def test_max_heap_class(self):
        task1 = self.data.jobs[0].get_task(0)
        task2 = self.data.jobs[0].get_task(1)

        max_heap_obj_task1 = _MaxHeapObj(self.data, task1)
        max_heap_obj_task2 = _MaxHeapObj(self.data, task2)
        self.assertLess(max_heap_obj_task1, max_heap_obj_task2)

    def test_min_heap(self):
        heap = _JobTaskHeap(self.data, maxheap=False)
        for job in self.data.jobs:
            for task in job.get_tasks():
                heap.push_task(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop_task()
            task_index = self.data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in
                                self.data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertLessEqual(tmp_list[i][1], tmp_list[i + 1][1])

    def test_max_heap(self):
        heap = _JobTaskHeap(self.data, maxheap=True)
        for job in self.data.jobs:
            for task in job.get_tasks():
                heap.push_task(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop_task()
            task_index = self.data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in
                                self.data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertGreaterEqual(tmp_list[i][1], tmp_list[i + 1][1])


class TestGenSolution(unittest.TestCase):

    def test_generate_feasible_solution(self):
        try:
            SolutionFactory(data.CSVData(
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')
            ).get_n_solutions(500)

        except InfeasibleSolutionException:
            self.assertTrue(False, "Infeasible solution was generated")

    def test_generate_feasible_solution_spt(self):  # Note this test fails on data/given_data
        self.fjs_data = get_all_fjs_files()
        for fjs_instance in random.choices(self.fjs_data, k=10):
            try:
                print("test_generate_feasible_solution_spt with fjs data: " + fjs_instance)
                SolutionFactory(data.FJSData(fjs_instance)).get_n_shortest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.assertTrue(False, "Infeasible solution was generated")

    def test_generate_feasible_solution_lpt(self):  # Note this test fails on data/given_data
        self.fjs_data = get_all_fjs_files()
        for fjs_instance in random.choices(self.fjs_data, k=10):
            try:
                print("test_generate_feasible_solution_lpt with fjs data: " + fjs_instance)
                SolutionFactory(data.FJSData(fjs_instance)).get_n_longest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.assertTrue(False, "Infeasible solution was generated")


if __name__ == '__main__':
    unittest.main()
