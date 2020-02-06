import datetime
import os
import shutil
import unittest

from JSSP import data
from JSSP.solution import SolutionFactory
from JSSP.solution._schedule_creator import _DayHourMinute, UnacceptableScheduleTimeException
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


class TestDayHourMinute(unittest.TestCase):

    # TODO add assertEquals for total_elapsed_minutes

    def test_invalid_start_and_end_time(self):
        try:
            start_time = datetime.time(23, 0)
            end_time = datetime.time(22, 0)
            _DayHourMinute(start_time, end_time)
            self.fail()
        except UnacceptableScheduleTimeException:
            pass

    def test_adding_minutes(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(0)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(-1)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(1)
        self.assertEqual(1, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.hour = 8
        schedule_time.min = 0

        schedule_time.add_minutes(60)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(59, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(10)
        self.assertEqual(9, schedule_time.min)
        self.assertEqual(10, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

    def test_adding_hours(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(12, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(60 * 3 + 1)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(60 * 3 + 1)
        self.assertEqual(1, schedule_time.min)
        self.assertEqual(11, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(3, schedule_time.day)

    def test_adding_days(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * (end_time.hour - start_time.hour) * 5)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(6, schedule_time.day)

        schedule_time.add_minutes(60 * 11)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(19, schedule_time.hour)
        self.assertEqual(6, schedule_time.day)

        schedule_time.add_minutes(60)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(7, schedule_time.day)

    def test_adding_minutes_w_start_minute(self):
        start_time = datetime.time(8, 30)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(0)
        self.assertEqual(30, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(1)
        self.assertEqual(1, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(10, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(30, schedule_time.min)
        self.assertEqual(10, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

    def test_adding_hours_w_start_minute(self):
        start_time = datetime.time(8, 30)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 12)
        self.assertEqual(30, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(1)
        self.assertEqual(1, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(10, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(30, schedule_time.min)
        self.assertEqual(10, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

    def test_adding_minutes_w_end_minute(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 30)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 12)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(20, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(1)
        self.assertEqual(1, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(59)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

        schedule_time.add_minutes(30)
        self.assertEqual(30, schedule_time.min)
        self.assertEqual(9, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)

    def test_adding_hours_w_end_minute(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(12, 30)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 4)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(12, schedule_time.hour)
        self.assertEqual(1, schedule_time.day)
        self.assertEqual(60 * 4, schedule_time.total_elapsed_minutes)

        schedule_time.add_minutes(30)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(2, schedule_time.day)
        self.assertEqual(60 * 4 + 30 + (11.5 + 8) * 60, schedule_time.total_elapsed_minutes)

        schedule_time.add_minutes(60 * 4 + 30)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(3, schedule_time.day)

        schedule_time.add_minutes(31)
        self.assertEqual(31, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(3, schedule_time.day)

        schedule_time.add_minutes(60 * 4)
        self.assertEqual(0, schedule_time.min)
        self.assertEqual(8, schedule_time.hour)
        self.assertEqual(4, schedule_time.day)


if __name__ == '__main__':
    unittest.main()
