import datetime
import unittest

from JSSP.solution import SolutionFactory
from tests.util import tmp_dir, csv_data, rm_tree


class TestSchedule(unittest.TestCase):

    def setUp(self) -> None:
        self.output_file = tmp_dir / 'test_output'

    def tearDown(self) -> None:
        rm_tree(tmp_dir)

    def test_create_continuous_xlsx_schedule(self):
        solution_obj = SolutionFactory(csv_data).get_solution()

        # test without suffix
        solution_obj.create_schedule_xlsx_file(self.output_file, continuous=True)
        self.assertTrue(self.output_file.with_suffix('.xlsx').exists())

        output_file = self.output_file.with_suffix('.xlsx')

        # test with suffix
        output_file.unlink()
        solution_obj.create_schedule_xlsx_file(output_file, continuous=True)
        self.assertTrue(output_file.exists())

        # test as string
        output_file.unlink()
        solution_obj.create_schedule_xlsx_file(str(output_file), continuous=True)
        self.assertTrue(output_file.exists())

    def test_create_schedule_w_start_and_end_times(self):
        solution_obj = SolutionFactory(csv_data).get_solution()
        solution_obj.create_schedule_xlsx_file(self.output_file,
                                               start_date=datetime.date.today(),
                                               start_time=datetime.time(10, 0),
                                               end_time=datetime.time(21, 0))
        self.assertTrue(self.output_file.with_suffix('.xlsx').exists())

    def test_create_continuous_gantt_chart(self):
        solution_obj = SolutionFactory(csv_data).get_solution()

        # test without suffix
        solution_obj.create_gantt_chart_html_file(self.output_file, continuous=True)
        self.assertTrue(self.output_file.with_suffix('.html').exists())

        output_file = self.output_file.with_suffix('.html')

        # test with suffix
        output_file.unlink()
        solution_obj.create_gantt_chart_html_file(output_file, continuous=True)
        self.assertTrue(output_file.exists())

        # test as string
        output_file.unlink()
        solution_obj.create_gantt_chart_html_file(str(output_file), continuous=True)
        self.assertTrue(output_file.exists())

    def test_create_gantt_chart_w_start_and_end_times(self):
        solution_obj = SolutionFactory(csv_data).get_solution()
        solution_obj.create_gantt_chart_html_file(self.output_file,
                                                  start_date=datetime.date.today(),
                                                  start_time=datetime.time(10, 0),
                                                  end_time=datetime.time(21, 0))
        self.assertTrue(self.output_file.with_suffix('.html').exists())


if __name__ == '__main__':
    unittest.main()
