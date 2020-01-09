import datetime
import os
import shutil
import unittest

from JSSP import solution
from JSSP.data import Data
from JSSP.solution._schedule_creator import _DayHourMinute, UnacceptableScheduleTime
from tests import project_root, tmp_dir

"""
Test the following: 

1. solution.create_schedule()

"""


class TestSchedule(unittest.TestCase):

    def setUp(self) -> None:
        Data.initialize_data_from_csv(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def tearDown(self) -> None:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_create_schedule(self):
        solution_obj = solution.SolutionFactory.get_solution()
        solution_obj.create_schedule_xlsx_file(tmp_dir + os.sep + 'test_schedule')
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'test_schedule.xlsx'))

    def test_create_schedule_w_start__and_end_times(self):
        solution_obj = solution.SolutionFactory.get_solution()
        solution_obj.create_schedule_xlsx_file(tmp_dir + os.sep + 'test_schedule', start_time=datetime.time(10, 0), end_time=datetime.time(21, 0))
        self.assertTrue(os.path.exists(tmp_dir + os.sep + 'test_schedule.xlsx'))


class TestCustomDayHourMinute(unittest.TestCase):

    def test_invalid_start_and_end_time(self):
        try:
            start_time = datetime.time(23, 0)
            end_time = datetime.time(22, 0)
            _DayHourMinute(start_time, end_time)
            self.fail()
        except UnacceptableScheduleTime:
            pass

    def test_adding_minutes(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(0)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(-1)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(1)
        self.assertEqual(schedule_time.min, 1)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.hour = 8
        schedule_time.min = 0

        schedule_time.add_minutes(60)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 59)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(10)
        self.assertEqual(schedule_time.min, 9)
        self.assertEqual(schedule_time.hour, 10)
        self.assertEqual(schedule_time.day, 1)

    def test_adding_hours(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(12, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(60 * 3 + 1)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(60 * 3 + 1)
        self.assertEqual(schedule_time.min, 1)
        self.assertEqual(schedule_time.hour, 11)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 3)

    def test_adding_days(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * (end_time.hour - start_time.hour) * 5)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 6)

        schedule_time.add_minutes(60 * 11)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 19)
        self.assertEqual(schedule_time.day, 6)

        schedule_time.add_minutes(60)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 7)

    def test_adding_minutes_w_start_minute(self):
        start_time = datetime.time(8, 30)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(0)
        self.assertEqual(schedule_time.min, 30)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(1)
        self.assertEqual(schedule_time.min, 1)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 10)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 30)
        self.assertEqual(schedule_time.hour, 10)
        self.assertEqual(schedule_time.day, 1)

    def test_adding_hours_w_start_minute(self):
        start_time = datetime.time(8, 30)
        end_time = datetime.time(20, 0)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 12)
        self.assertEqual(schedule_time.min, 30)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(1)
        self.assertEqual(schedule_time.min, 1)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 10)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 30)
        self.assertEqual(schedule_time.hour, 10)
        self.assertEqual(schedule_time.day, 2)

    def test_adding_minutes_w_end_minute(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(20, 30)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 12)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 20)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(1)
        self.assertEqual(schedule_time.min, 1)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(59)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 30)
        self.assertEqual(schedule_time.hour, 9)
        self.assertEqual(schedule_time.day, 2)

    def test_adding_hours_w_end_minute(self):
        start_time = datetime.time(8, 0)
        end_time = datetime.time(12, 30)
        schedule_time = _DayHourMinute(start_time, end_time)

        schedule_time.add_minutes(60 * 4)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 12)
        self.assertEqual(schedule_time.day, 1)

        schedule_time.add_minutes(30)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 2)

        schedule_time.add_minutes(60 * 4 + 30)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 3)

        schedule_time.add_minutes(31)
        self.assertEqual(schedule_time.min, 31)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 3)

        schedule_time.add_minutes(60 * 4)
        self.assertEqual(schedule_time.min, 0)
        self.assertEqual(schedule_time.hour, 8)
        self.assertEqual(schedule_time.day, 4)


if __name__ == '__main__':
    unittest.main()
