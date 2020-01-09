import datetime
import os
import random

import plotly.figure_factory as ff
import xlsxwriter
from plotly.offline import plot, iplot

from JSSP.data import Data


class UnacceptableScheduleTime(Exception):
    pass


def _get_n_colors(n):
    """
    Gets n random rgb values (colors).

    :param n: number of colors to return

    :rtype: list
    :returns: list of n rgb tuple values
    """
    ret = []
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)
    step = 256 / n
    for i in range(n):
        r += step
        g += step
        b += step
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        ret.append((r, g, b))
    return ret


def _convert_mins_to_formatted_str(minutes):
    """
    Converts minutes to days, hours, minutes as a formatted String.

    :type minutes: int
    :param minutes: minutes to convert

    :rtype: str
    :returns: string in the form "{days}d {hours}h {minutes}m"
    """
    days = minutes // (60 * 24)
    minutes %= (60 * 24)
    hours = minutes // 60
    minutes %= 60

    return f"{int(days)}d {int(hours)}h {int(minutes)}m"


class _CustomDayHourMinute:
    """
    Class for keeping track of the start & end times of operations in a schedule.

    :type start_time: datetime.time
    :param start_time: Start time of the workday

    :type end_time: datetime.time
    :param end_time: End time of the workday

    See help(_CustomDayHourMinute.__init__)
    """
    def __init__(self, start_time, end_time):
        """
        Initializes a _CustomDayHourMinute with day = 1, hour = start_time.hour, min = start_time.minute,
        start_time = start_time, end_time = end_time, and total_elapsed_minutes = 0.
        """
        if end_time <= start_time:
            raise UnacceptableScheduleTime(
                f"start_time={start_time} is greater than or equal to end_time={end_time}")

        self.day = 1
        self.hour = start_time.hour
        self.min = start_time.minute
        self.start_time = start_time
        self.end_time = end_time
        self.total_elapsed_minutes = 0

    def add_minutes(self, minutes_to_add):
        """
        Adds a number of minutes to this _CustomDayHourMinute.

        :type minutes_to_add: int
        :param minutes_to_add: minutes to add

        :returns: None
        """
        if minutes_to_add <= 0:
            return

        days_to_add = minutes_to_add // (60 * self.end_time.hour + self.end_time.minute - 60 * self.start_time.hour - self.start_time.minute)
        minutes_to_add %= (60 * self.end_time.hour + self.end_time.minute - 60 * self.start_time.hour - self.start_time.minute)
        hours_to_add = minutes_to_add // 60
        minutes_to_add %= 60

        self.day += days_to_add
        self.hour += hours_to_add
        self.min += minutes_to_add
        self.total_elapsed_minutes += days_to_add * (self.end_time.hour + self.end_time.minute / 60 - self.start_time.hour - self.start_time.minute / 60) + hours_to_add * 60 + minutes_to_add

        if days_to_add > 0:
            self.hour = self.start_time.hour
            self.min = self.start_time.minute

        if self.min >= 60:
            self.hour += 1
            self.min -= 60

        if self.hour > self.end_time.hour or (self.hour == self.end_time.hour and self.min >= self.end_time.minute):
            self.day += 1
            self.hour = self.start_time.hour
            self.min = self.start_time.minute

    def copy(self):
        """
        :returns: a copy of this _CustomDayHourMinute
        """
        result = _CustomDayHourMinute(self.start_time, self.end_time)
        result.day = self.day
        result.hour = self.hour
        result.min = self.min
        return result

    def get_hour_min_sec_str(self):
        """
        :rtype: str
        :returns: string in the form "{self.hour}:{self.min}:00"
        """
        return "{:02d}:{:02d}:00".format(int(self.hour), int(self.min))

    def __str__(self):
        """
        :returns: string in the form "day {self.day} {self.hour}:{self.min}:00
        """
        return "day {}  {:02d}:{:02d}:00".format(int(self.day), int(self.hour), int(self.min))


class _ContinuousCustomDayHourMinute(_CustomDayHourMinute):
    """
    Class for keeping track of the start/end times of operations in a continuous schedule.

    See help(_ContinuousCustomDayHourMinute.__init__)
    """
    def __init__(self):
        """
        Initializes a _CustomDayHourMinute with day = 1, hour = 0, min = 0, and total_elapsed_minutes = 0.
        """
        super().__init__(datetime.time(hour=0, minute=0), datetime.time(hour=1, minute=0))

    def add_minutes(self, minutes_to_add):
        """
        Adds a number of minutes to this _ContinuousCustomDayHourMinute.

        :type minutes_to_add: int
        :param minutes_to_add: minutes to add

        :returns: None
        """
        if minutes_to_add <= 0:
            return

        days_to_add = minutes_to_add // (60 * 24)
        minutes_to_add %= (60 * 24)
        hours_to_add = minutes_to_add // 60
        minutes_to_add %= 60

        self.day += days_to_add
        self.hour += hours_to_add
        self.min += minutes_to_add
        self.total_elapsed_minutes += minutes_to_add

        while self.min >= 60:
            self.hour += 1
            self.min -= 60

        while self.hour >= 24:
            self.day += 1
            self.hour -= 24

    def copy(self):
        """
        :returns: a copy of this _ContinuousCustomDayHourMinute
        """
        result = _ContinuousCustomDayHourMinute()
        result.day = self.day
        result.hour = self.hour
        result.min = self.min
        return result


def create_schedule_xlsx_file(solution, output_path, start_time=datetime.time(hour=8, minute=0),
                              end_time=datetime.time(hour=20, minute=0), continuous=False):
    """
    Creates an excel file in the output_dir directory that contains the schedule for each machine of the solution parameter.

    :type solution: Solution
    :param solution: solution to create a schedule for

    :type output_path: str
    :param output_path: path to the excel file to create

    :type start_time: datetime.time
    :param start_time: start time of the work day

    :type end_time: datetime.time
    :param end_time: end time of the work day

    :type continuous: bool
    :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

    :returns: None
    """
    custom_day_hour_min_dict = {machine_id: _CustomDayHourMinute(start_time, end_time) if not continuous else _ContinuousCustomDayHourMinute()
                                for machine_id in range(Data.total_number_of_machines)}

    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(output_path)

    if not output_path.endswith(".xlsx"):
        output_path += ".xlsx"

    # get all the necessary data from the static Data class
    task_processing_times_matrix = Data.task_processing_times_matrix
    job_task_index_matrix = Data.job_task_index_matrix
    sequence_dependency_matrix = Data.sequence_dependency_matrix
    num_jobs = sequence_dependency_matrix.shape[0]
    num_machines = task_processing_times_matrix.shape[1]

    # create an excel workbook and worksheet in output directory
    workbook = xlsxwriter.Workbook(f'{output_path}')
    colored = workbook.add_format({'bg_color': '#E7E6E6'})
    worksheet = workbook.add_worksheet('Schedule')

    col = 0

    # Write headers to excel worksheet and format cells
    for i in range(num_machines):
        worksheet.set_column(col, col, 12)
        worksheet.write(0, col, f'Machine {i}')
        worksheet.write_row(4, col, ["Job_Task", "Start", "End"])
        worksheet.set_column(col + 1, col + 1, 13)
        worksheet.set_column(col + 2, col + 2, 13)
        worksheet.set_column(col + 3, col + 3, 2, colored)
        col += 4

    worksheet.set_row(4, 16, cell_format=colored)

    # get the operation matrix
    operation_2d_array = solution.operation_2d_array

    # all of the row entries (i.e. Job_Task, Start, End) start at row 3 in the excel file
    machine_current_row = [5] * num_machines

    # memory for keeping track of all machine's make span times
    machine_makespan_memory = [0] * num_machines

    # memory for keeping track of total wait time on a machine
    machine_waitime_memory = [0] * num_machines

    # memory for keeping track of total setup time on a machine
    machine_setup_time_memory = [0] * num_machines

    # memory for keeping track of all machine's latest (job, task) that was processed
    machine_jobs_memory = [(-1, -1)] * num_machines

    # memory for keeping track of all job's latest task's sequence that was processed
    job_seq_memory = [0] * num_jobs

    # memory for keeping track of all job's previous sequence end time (used for calculating wait times)
    prev_job_seq_end_memory = [0] * num_jobs

    # memory for keeping track of all job's latest end time (used for updating prev_job_seq_end_memory)
    job_end_memory = [0] * num_jobs

    for row in range(operation_2d_array.shape[0]):

        job_id = operation_2d_array[row, 0]
        task_id = operation_2d_array[row, 1]
        sequence = operation_2d_array[row, 2]
        machine = operation_2d_array[row, 3]

        # get the setup time for the current operation
        if machine_jobs_memory[machine] != (-1, -1):
            cur_task_index = job_task_index_matrix[job_id, task_id]
            prev_task_index = job_task_index_matrix[machine_jobs_memory[machine]]
            setup = sequence_dependency_matrix[cur_task_index, prev_task_index]
        else:
            setup = 0

        # update previous job sequence end t if a new sequence if
        if job_seq_memory[job_id] < sequence:
            prev_job_seq_end_memory[job_id] = job_end_memory[job_id]

        if prev_job_seq_end_memory[job_id] <= machine_makespan_memory[machine]:
            wait = 0
        else:
            wait = prev_job_seq_end_memory[job_id] - machine_makespan_memory[machine]

        runtime = task_processing_times_matrix[job_task_index_matrix[job_id, task_id], machine]

        custom_day_hour_min_dict[machine].add_minutes(wait)
        tmp_custom_day_hour_min = custom_day_hour_min_dict[machine].copy()
        day_before_addition = tmp_custom_day_hour_min.day
        tmp_custom_day_hour_min.add_minutes(wait + setup + runtime)

        if not continuous and day_before_addition < tmp_custom_day_hour_min.day:
            custom_day_hour_min_dict[machine].total_elapsed_minutes += \
                24 * 60 - (custom_day_hour_min_dict[machine].hour * 60 + custom_day_hour_min_dict[machine].min) + \
                custom_day_hour_min_dict[machine].start_time.hour * 60 + custom_day_hour_min_dict[machine].start_time.minute
            custom_day_hour_min_dict[machine].day += 1
            custom_day_hour_min_dict[machine].hour = custom_day_hour_min_dict[machine].start_time.hour
            custom_day_hour_min_dict[machine].min = custom_day_hour_min_dict[machine].start_time.minute
            setup = 0

        start_of_operation_setup = custom_day_hour_min_dict[machine].__str__()
        custom_day_hour_min_dict[machine].add_minutes(setup)

        # write Job_Task setup
        worksheet.write_row(machine_current_row[machine], machine * 4, [f"{job_id}_{task_id} setup",
                                                                        start_of_operation_setup,
                                                                        custom_day_hour_min_dict[machine].__str__()])

        end_of_operation_setup = custom_day_hour_min_dict[machine].__str__()
        custom_day_hour_min_dict[machine].add_minutes(runtime)

        # write Job_Task run
        worksheet.write_row(machine_current_row[machine] + 1, machine * 4, [f"{job_id}_{task_id} run",
                                                                            end_of_operation_setup,
                                                                            custom_day_hour_min_dict[
                                                                                machine].__str__()])

        # compute total added time and update memory modules
        machine_makespan_memory[machine] += runtime + wait + setup
        machine_waitime_memory[machine] += wait
        machine_setup_time_memory[machine] += setup
        job_end_memory[job_id] = max(machine_makespan_memory[machine], job_end_memory[job_id])
        job_seq_memory[job_id] = sequence
        machine_jobs_memory[machine] = (job_id, task_id)

        # increment current row for machine by 2
        machine_current_row[machine] += 2

    col = 0
    for i in range(num_machines):
        worksheet.write_row(1, col, ["Makespan =", _convert_mins_to_formatted_str(custom_day_hour_min_dict[i].total_elapsed_minutes)])
        worksheet.write_row(2, col, ["Total Wait =", _convert_mins_to_formatted_str(machine_waitime_memory[i])])
        worksheet.write_row(3, col, ["Total Setup =", _convert_mins_to_formatted_str(machine_setup_time_memory[i])])
        col += 4

    workbook.close()


def create_gantt_chart(solution, output_path, title='Gantt Chart', start_date=datetime.datetime.now(),
                       start_time=datetime.time(hour=8, minute=0), end_time=datetime.time(hour=20, minute=0),
                       iplot_bool=False, auto_open=False, continuous=False):
    """
    Creates a gantt chart html file of the solution parameters in the output_dir directory if iplot_bool is false,
    else it plots a gantt chart of the solution parameter in an ipyton notebook.

    :type solution: Solution
    :param solution: solution to create a schedule for

    :type output_path: str
    :param output_path: path to the gantt chart file to create

    :type title: str
    :param title: name of the gantt chart

    :type start_date: datetime.datetime
    :param start_date: datetime to start the schedule from

    :type start_time: datetime.time
    :param start_time: start time of the work day

    :type end_time: datetime.time
    :param end_time: end time of the work day

    :type iplot_bool: bool
    :param iplot_bool: if true plots the gantt chart in an ipyton notebook

    :type auto_open: bool
    :param auto_open: if true the gantt chart html file is automatically opened in a browser

    :type continuous: bool
    :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

    :returns: None
    """

    df = []

    custom_day_hour_min_dict = {machine_id: _CustomDayHourMinute(start_time, end_time) if not continuous else _ContinuousCustomDayHourMinute()
                                for machine_id in range(Data.total_number_of_machines)}
    start_date_dict = {machine_id: start_date for machine_id in range(Data.total_number_of_machines)}

    if not iplot_bool and not os.path.exists(os.path.dirname(output_path)):
        os.mkdir(os.path.dirname(output_path))

    # get all the necessary data from the static Data class
    task_processing_times_matrix = Data.task_processing_times_matrix
    job_task_index_matrix = Data.job_task_index_matrix
    sequence_dependency_matrix = Data.sequence_dependency_matrix
    num_jobs = sequence_dependency_matrix.shape[0]
    num_machines = task_processing_times_matrix.shape[1]

    # get the operation matrix
    operation_2d_array = solution.operation_2d_array

    # all of the row entries (i.e. Job_Task, Start, End) start at row 3 in the excel file
    machine_current_row = [5] * num_machines

    # memory for keeping track of all machine's make span times
    machine_makespan_memory = [0] * num_machines

    # memory for keeping track of total wait time on a machine
    machine_waitime_memory = [0] * num_machines

    # memory for keeping track of total setup time on a machine
    machine_setup_time_memory = [0] * num_machines

    # memory for keeping track of all machine's latest (job, task) that was processed
    machine_jobs_memory = [(-1, -1)] * num_machines

    # memory for keeping track of all job's latest task's sequence that was processed
    job_seq_memory = [0] * num_jobs

    # memory for keeping track of all job's previous sequence end time (used for calculating wait times)
    prev_job_seq_end_memory = [0] * num_jobs

    # memory for keeping track of all job's latest end time (used for updating prev_job_seq_end_memory)
    job_end_memory = [0] * num_jobs

    for row in range(operation_2d_array.shape[0]):

        job_id = operation_2d_array[row, 0]
        task_id = operation_2d_array[row, 1]
        sequence = operation_2d_array[row, 2]
        machine = operation_2d_array[row, 3]

        # get the setup time for the current operation
        if machine_jobs_memory[machine] != (-1, -1):
            cur_task_index = job_task_index_matrix[job_id, task_id]
            prev_task_index = job_task_index_matrix[machine_jobs_memory[machine]]
            setup = sequence_dependency_matrix[cur_task_index, prev_task_index]
        else:
            setup = 0

        # update previous job sequence end t if a new sequence if
        if job_seq_memory[job_id] < sequence:
            prev_job_seq_end_memory[job_id] = job_end_memory[job_id]

        if prev_job_seq_end_memory[job_id] <= machine_makespan_memory[machine]:
            wait = 0
        else:
            wait = prev_job_seq_end_memory[job_id] - machine_makespan_memory[machine]

        runtime = task_processing_times_matrix[job_task_index_matrix[job_id, task_id], machine]

        custom_day_hour_min_dict[machine].add_minutes(wait)
        tmp_custom_day_hour_min = custom_day_hour_min_dict[machine].copy()
        day_before_addition = tmp_custom_day_hour_min.day
        tmp_custom_day_hour_min.add_minutes(wait + setup + runtime)

        if not continuous and day_before_addition < tmp_custom_day_hour_min.day:
            custom_day_hour_min_dict[machine].total_elapsed_minutes += \
                24 * 60 - (custom_day_hour_min_dict[machine].hour * 60 + custom_day_hour_min_dict[machine].min) + \
                custom_day_hour_min_dict[machine].start_time.hour * 60 + custom_day_hour_min_dict[machine].start_time.minute
            custom_day_hour_min_dict[machine].day += 1
            custom_day_hour_min_dict[machine].hour = start_time.hour
            custom_day_hour_min_dict[machine].min = start_time.minute
            start_date_dict[machine] += datetime.timedelta(days=1)
            start_date_dict[machine] = start_date_dict[machine].replace(hour=start_time.hour, minute=start_time.minute)

        start_of_operation_setup = custom_day_hour_min_dict[machine].copy()
        start_date_of_operation_setup = start_date_dict[machine]
        custom_day_hour_min_dict[machine].add_minutes(setup)
        start_date_dict[machine] = start_date_dict[machine] + datetime.timedelta(minutes=int(setup))

        df.append(dict(Task=f"Machine-{machine}",
                       Start=f"{start_date_of_operation_setup.strftime('%Y-%m-%d')} {start_of_operation_setup.get_hour_min_sec_str()}",
                       Finish=f"{start_date_dict[machine].strftime('%Y-%m-%d')} {custom_day_hour_min_dict[machine].get_hour_min_sec_str()}",
                       Resource="setup"))

        end_of_operation_setup = custom_day_hour_min_dict[machine].copy()
        end_date_of_operation_setup = start_date_dict[machine]
        custom_day_hour_min_dict[machine].add_minutes(runtime)
        start_date_dict[machine] = start_date_dict[machine] + datetime.timedelta(minutes=int(runtime))

        df.append(dict(Task=f"Machine-{machine}",
                       Start=f"{end_date_of_operation_setup.strftime('%Y-%m-%d')} {end_of_operation_setup.get_hour_min_sec_str()}",
                       Finish=f"{start_date_dict[machine].strftime('%Y-%m-%d')} {custom_day_hour_min_dict[machine].get_hour_min_sec_str()}",
                       Resource=f"Job {job_id}"))

        # compute total added time and update memory modules
        machine_makespan_memory[machine] += runtime + wait + setup
        machine_waitime_memory[machine] += wait
        machine_setup_time_memory[machine] += setup
        job_end_memory[job_id] = max(machine_makespan_memory[machine], job_end_memory[job_id])
        job_seq_memory[job_id] = sequence
        machine_jobs_memory[machine] = (job_id, task_id)

        # increment current row for machine by 2
        machine_current_row[machine] += 2

    colors = {'setup': 'rgb(107, 127, 135)'}
    for i, rgb in enumerate(_get_n_colors(Data.total_number_of_jobs)):
        colors[f'Job {i}'] = f'rgb{rgb}'

    fig = ff.create_gantt(df, colors, show_colorbar=True, index_col='Resource', title=title, showgrid_x=True, showgrid_y=True, group_tasks=True)
    if iplot_bool:
        iplot(fig)
    else:
        plot(fig, filename=output_path, auto_open=auto_open)
