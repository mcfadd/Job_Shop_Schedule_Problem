# Job Shop Schedule Problem (JSSP)

[![CircleCI](https://circleci.com/gh/mcfadd/Job_Shop_Schedule_Problem/tree/master.svg?style=svg)](https://circleci.com/gh/mcfadd/Job_Shop_Schedule_Problem/tree/master)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=mcfadd_Job_Shop_Schedule_Problem&metric=alert_status)](https://sonarcloud.io/dashboard?id=mcfadd_Job_Shop_Schedule_Problem)
[![Documentation Status](https://readthedocs.org/projects/job-shop-schedule-problem/badge/?version=stable)](https://job-shop-schedule-problem.readthedocs.io/en/stable/?badge=stable)

#### Version 2.1.0 

JSSP is an optimization package for the Job Shop Schedule Problem.  
JSSP has two different optimization algorithms:  

- Parallel Tabu Search
- Genetic Algorithm

### Features 

1. Find near optimal solutions to flexible job shop schedule problems with sequence dependency setup times.
2. Use of [Cython](https://cython.org/) C extensions for fast execution of code.
3. Plot tabu search and/or genetic algorithm optimization using [Plotly](https://plot.ly/).
4. Create gantt charts using [Plotly](https://plot.ly/).
5. Create production schedule excel file.

For more information as well as examples, [read the docs](https://readthedocs.org/projects/job-shop-schedule-problem/).

## How to Install

After cloning this repo, change directories to where `setup.py` exists and run 
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install .
```
If you get an error about `python.h` not being found try installing [python3-dev](https://stackoverflow.com/questions/31002091/what-is-python-dev-package-used-for).

To build the C-extensions (i.e compile `.pyx` files) without installing JSSP run
```bash
python setup.py build_ext
```

## How to Use

After installation, JSSP can imported as a normal python module.  
For examples on how to use JSSP see the jupyter notebooks in the [examples](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/examples) folder or [see the docs](https://job-shop-schedule-problem.readthedocs.io/en/stable/Examples.html).

**Important Note**

Job-Tasks in [jobTasks.csv](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/jobTasks.csv) and [sequenceDependencyMatrix.csv](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/sequenceDependencyMatrix.csv) need to be in ascending order according to (job_id, task_id).  

### Example

The following example minimally demonstrates how to run parallel tabu search to find a solution to the problem instance in [data/given_data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/given_data).

```python
from JSSP.solver import Solver
from JSSP.data import SpreadsheetData

# initialize data
data = SpreadsheetData('data/given_data/sequenceDependencyMatrix.csv',
                       'data/given_data/machineRunSpeed.csv',
                       'data/given_data/jobTasks.csv')

# run parallel Tabu Search
solver = Solver(data)
solution = solver.tabu_search_iter(iterations=500,
                                   num_processes=4,
                                   tabu_list_size=20,
                                   neighborhood_size=250)

# create Schedule
solution.create_schedule_xlsx_file('output/Schedule.xlsx')                   
```

**Flexible Job Shop**

To read in a flexible job shop problem instance from a .fjs file (see [data/fjs_data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/fjs_data)) do the following:
```python
from JSSP.data import FJSData

data = FJSData('data/fjs_data/Barnes/Barnes_mt10c1.fjs')
```

## How to Contribute

If you would like to contribute to this project please see [CONTRIBUTING.md](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/CONTRIBUTING.md).

## License

JSSP is licensed under the [ISC License](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/LICENSE):
```text
ISC License

Copyright (c) 2019, Matthew McFadden

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```


