.. toctree::
   :maxdepth: 2
   :hidden:

   doc/JSSP
   Problem_description
   Algorithms
   Examples


Welcome to JSSP's Documentation!
================================

JSSP is an optimization package for the Job Shop Schedule Problem. |br|
For more information on the specific job shop schedule problem JSSP was designed to solve see the `Problem Description <Problem_description.html>`_ page.

As of right now, JSSP is only supported on Unix type operating systems. See `Issue #4 <https://github.com/mcfadd/Job_Shop_Schedule_Problem/issues/4>`_ for more information.

JSSP has two different optimization algorithms: |br|

1. Parallel Tabu Search
2. Genetic Algorithm

For more information on these algorithms see the `Algorithms <Algorithms.html>`_ page.

========
Features
========

1. Find near optimal solutions to flexible job shop schedule problems with sequence dependency setup times.
2. Use of `Cython <https://cython.org/>`_ C extensions for fast execution of code.
3. Plot tabu search and/or genetic algorithm optimization using `plotly <https://plot.ly/>`_.
4. Create gantt charts using `plotly <https://plot.ly/>`_.
5. Create production schedule excel file.

==============
How to Install
==============

1. `Download JSSP < TODO >`_
2. Run ``easy_install < TODO >``

If you get an error about ``python.h`` not being found try installing `python3-dev <https://stackoverflow.com/questions/31002091/what-is-python-dev-package-used-for>`_.

==========
How to Use
==========

After installation, JSSP can imported as a normal python package. |br|
See the `Examples <Examples.html>`_ page for examples on how to use JSSP.

**Important Note**

Job-tasks in jobTasks.csv and sequenceDependencyMatrix.csv need to be in ascending order according to (job_id, task_id). |br|
(see the csv files on `GitHub <https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/given_data>`_ for a reference)

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |br| raw:: html

  <br/>
