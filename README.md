# Job Shop Schedule Problem (JSSP)

This problem was given to us in a mathematics course titled *Math 490 Preparation for Industrial Careers: Solving Industrial and Applied Problems in Teams* (sponsered by [PIC Math](https://www.maa.org/programs-and-communities/professional-development/pic-math)) at The University of Wisconsin - Milwaukee.

The specific JSSP problem this program attempts to solve is classified as the  
**Partial Flexible Job Shop Scheduling Problem With Sequence Dependent Setup Times**.  
For a complete description of the problem see the [Problem Description](https://github.com/mcfadd/Job_Shop_Schedule_Problem/wiki/Job-Shop-Schedule-Problem-Description) wiki.

**Team**  
[Matthew McFadden](https://github.com/mcfadd)  
[Jessica Wolfson](https://github.com/JFWolfson)  
[Maddie Kenney](https://github.com/MaddieKenney)  
[Anthony Valdez ](https://github.com/avaldez96)  

## Program

As of right now, JSSP is only supported on unix type operating systems.  
JSSP has two different optimization algorithms, parallel tabu search, and a genetic algorithm.
For more information on these algorithms see the [Algorithms](https://github.com/mcfadd/Job_Shop_Schedule_Problem/wiki/Algorithms) wiki.

### How to Install:

1. Make sure you have [python3-dev](https://stackoverflow.com/questions/31002091/what-is-python-dev-package-used-for) installed (for cython)

2. Clone this repository:
```
git clone https://github.com/mcfadd/Job_Shop_Schedule_Problem
```
3. Navigate to the cloned directory where setup.py is located.  

4. Run the following:
```
pip install -r requirements.txt
python setup.py build_ext
pip install .
```

### How to Use:

After installation, JSSP can imported into a python project/notebook.  
See the [examples](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/examples) folder for examples. 

**Important Note**

Job-Tasks in jobTasks.csv and sequenceDependencyMatrix.csv need to be in ascending order according to their (job_id, task_id).  
(see csv files in the [data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/given_data) folder for reference)

**Example**
```python
from JSSP.solver import Solver
from JSSP.data import Data
import os

# initialize data
data_directory = 'data/given_data'
Data.initialize_data_from_csv(data_directory + '/sequenceDependencyMatrix.csv',
                              data_directory + '/machineRunSpeed.csv',
                              data_directory + '/jobTasks.csv')

# run tabu search
solver = Solver()
solution = solver.tabu_search(stopping_condition=30,
                              num_processes=2,
                              tabu_list_size=50,
                              neighborhood_size=250,
                              neighborhood_wait=0.1,
                              probability_change_machine=0.8,
                              reset_threshold=100
                             )                              
```

**Flexible Job Shop**

To read in a flexible job shop problem instance from a .fjs file (see [data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/fjs_data) folder) do the following:
```python
from JSSP.data import Data

Data.initialize_data_from_fjs('data/fjs_data/Barnes/Barnes_mt10c1.fjs')
```

## License

JSSP is licensed under the [ISC License]():
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
