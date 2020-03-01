import datetime
import os
import random

import plotly.figure_factory as ff
import xlsxwriter
from plotly.offline import plot, iplot


def _get_n_colors(n):
    """
    Gets n random rgb values (colors).

    :type n: int
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


def _check_output_path(output_path, file_ext):
    """
    Creates the output path if it doesnt exist.

    :type output_path: str
    :param output_path: the output path to create

    :type file_ext: str
    :param file_ext: file extension of the output path

    :rtype: str
    :return: the output path with the file extension
    """
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    if not output_path.endswith(file_ext):
        return output_path + file_ext
    else:
        return output_path


def create_schedule_xlsx_file(solution, output_path, start_date=datetime.date.today(), start_time=datetime.time(hour=8, minute=0),
                              end_time=datetime.time(hour=20, minute=0), continuous=False):
    """
    Creates an excel file in the output_dir directory that contains the schedule for each machine of the solution parameter.

    :type solution: Solution
    :param solution: solution to create a schedule for

    :type output_path: str
    :param output_path: path to the excel file to create

    :type start_date: datetime.date
    :param start_date: start date of the schedule

    :type start_time: datetime.time
    :param start_time: start time of the work day

    :type end_time: datetime.time
    :param end_time: end time of the work day

    :type continuous: bool
    :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

    :returns: None
    """
    output_path = _check_output_path(output_path, ".xlsx")

    # create an excel workbook and worksheet in output directory
    workbook = xlsxwriter.Workbook(f'{output_path}')
    colored = workbook.add_format({'bg_color': '#E7E6E6'})
    worksheet = workbook.add_worksheet('Schedule')

    col = 0
    # Write headers to excel worksheet and format cells
    for machine in range(solution.data.total_number_of_machines):
        worksheet.set_column(col, col, 12)
        worksheet.write(0, col, f'Machine {machine}')
        worksheet.write_row(2, col, ["Job_Task", "Start", "End"])
        worksheet.set_column(col + 1, col + 1, 20)
        worksheet.set_column(col + 2, col + 2, 20)
        worksheet.set_column(col + 3, col + 3, 2, colored)
        col += 4

    worksheet.set_row(2, 16, cell_format=colored)
    machine_current_row = [3] * solution.data.total_number_of_machines
    strftime = "%Y-%m-%d %H:%M:%S"
    operations = solution.get_operation_list_for_machine(start_date, start_time, end_time, continuous=continuous)
    for operation in operations:
        job_id = operation.job_id
        task_id = operation.task_id
        machine = operation.machine
        setup_start = operation.setup_start_time.strftime(strftime)
        setup_end = operation.setup_end_time.strftime(strftime)
        runtime_end = operation.runtime_end_time.strftime(strftime)

        worksheet.write_row(machine_current_row[machine],
                            machine * 4,
                            [f"{job_id}_{task_id} setup", setup_start, setup_end])

        worksheet.write_row(machine_current_row[machine] + 1,
                            machine * 4,
                            [f"{job_id}_{task_id} run", setup_end, runtime_end])

        machine_current_row[machine] += 2

    col = 0
    for machine in range(solution.data.total_number_of_machines):
        machine_operations = [op for op in operations if op.machine == machine]
        if len(machine_operations) > 0:
            s = machine_operations[0].setup_start_time
            e = machine_operations[-1].runtime_end_time
            makespan = str(e - s)
        else:
            makespan = "0"
        worksheet.write_row(1, col, ["Makespan =", makespan])
        col += 4

    workbook.close()


def create_gantt_chart(solution, output_path, title='Gantt Chart', start_date=datetime.date.today(),
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

    :type start_date: datetime.date
    :param start_date: date to start the schedule from

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

    if not iplot_bool:
        output_path = _check_output_path(output_path, ".html")

    df = []
    strftime = "%Y-%m-%d %H:%M:%S"
    operations = solution.get_operation_list_for_machine(start_date, start_time, end_time, continuous=continuous)
    for operation in operations:
        job_id = operation.job_id
        machine = operation.machine
        setup_start = operation.setup_start_time.strftime(strftime)
        setup_end = operation.setup_end_time.strftime(strftime)
        runtime_end = operation.runtime_end_time.strftime(strftime)

        df.append(dict(Task=f"Machine-{machine}",
                       Start=setup_start,
                       Finish=setup_end,
                       Resource="setup"))

        df.append(dict(Task=f"Machine-{machine}",
                       Start=setup_end,
                       Finish=runtime_end,
                       Resource=f"Job {job_id}"))

    colors = {'setup': 'rgb(107, 127, 135)'}
    for i, rgb in enumerate(_get_n_colors(solution.data.total_number_of_jobs)):
        colors[f'Job {i}'] = f'rgb{rgb}'

    fig = ff.create_gantt(df, colors, show_colorbar=True, index_col='Resource', title=title, showgrid_x=True, showgrid_y=True, group_tasks=True)
    if iplot_bool:
        iplot(fig)
    else:
        plot(fig, filename=output_path, auto_open=auto_open)
