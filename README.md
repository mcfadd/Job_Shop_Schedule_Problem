# Job Shop Schedule Problem (JSSP)

This problem was given to us in a mathematics course titled *Math 490 Preparation for Industrial Careers: Solving Industrial and Applied Problems in Teams* (sponsered by [PIC Math](https://www.maa.org/programs-and-communities/professional-development/pic-math)) at The University of Wisconsin - Milwaukee.

The specific JSSP problem this program attempts to solve is classified as the  
**Partial Flexible Job Shop Scheduling Problem With Sequence Dependent Setup Times**. For a complete description of the problem see the [Problem Description](https://github.com/mcfadd/Job_Shop_Schedule_Problem/wiki/Job-Shop-Schedule-Problem-Description) wiki.

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

After installation, JSSP can imported into a python project/ipython notebook.  
See the [examples](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/examples) folder for example jupyter notebooks. 

**Important Note:**

Job-Tasks in jobTasks.csv and sequenceDependencyMatrix.csv need to be in ascending order according to their (job_id, task_id).  
(see csv files in the [data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/data_set2) folder for reference)
  
**Flexable Job Shop**  
You can read in a flexable job shop problem from a .fjs file (see [data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/fjs_data) folder) with the following:
```python
from JSSP.data import Data

Data.initialize_data_from_fjs('data/fjs_data/Barnes/Barnes_mt10c1.fjs')
```
