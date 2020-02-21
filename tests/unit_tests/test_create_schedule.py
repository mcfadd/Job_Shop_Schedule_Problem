import datetime
import os
import shutil
import unittest

from JSSP import data
from JSSP.solution import SolutionFactory
from tests import project_root, tmp_dir


class TestSchedule(unittest.TestCase):
    output_file = f'{tmp_dir}{os.sep}test_output'

    def setUp(self) -> None:
        self.data = data.CSVData(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_create_continuous_xlsx_schedule(self):
        solution_obj = SolutionFactory(self.data).get_solution()
        solution_obj.create_schedule_xlsx_file(self.output_file, continuous=True)
        self.assertTrue(os.path.exists(self.output_file + '.xlsx'))

    def test_create_schedule_w_start_and_end_times(self):
        solution_obj = SolutionFactory(self.data).get_solution()
        solution_obj.create_schedule_xlsx_file(self.output_file, start_time=datetime.time(10, 0),
                                               end_time=datetime.time(21, 0))
        self.assertTrue(os.path.exists(self.output_file + '.xlsx'))

    def test_create_continuous_gantt_chart(self):
        solution_obj = SolutionFactory(self.data).get_solution()
        solution_obj.create_gantt_chart_html_file(self.output_file, continuous=True)
        self.assertTrue(os.path.exists(self.output_file + '.html'))

    def test_create_gantt_chart_w_start_and_end_times(self):
        solution_obj = SolutionFactory(self.data).get_solution()
        solution_obj.create_gantt_chart_html_file(self.output_file, start_time=datetime.time(10, 0),
                                                  end_time=datetime.time(21, 0))
        self.assertTrue(os.path.exists(self.output_file + '.html'))


if __name__ == '__main__':
    unittest.main()
