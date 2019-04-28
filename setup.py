#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.extension import Extension

__version__ = '1.0.0'

REQUIRED = [
    'Cython',
    'numpy',
    'plotly',
    'progressbar',
    'XlsxWriter'
]

ext_modules = [Extension("genetic_algorithm.ga_helpers",
                         ["JSSP/genetic_algorithm/ga_helpers.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()]),
               Extension("solution.makespan",
                         ["JSSP/solution/makespan.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()]),
               Extension("tabu_search.generate_neighbor",
                         ["JSSP/tabu_search/generate_neighbor.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()])
               ]

setup(
    name='JSSP',
    version=__version__,
    description='Program for solving the job shop schedule problem with sequence dependent set up times.',
    author='Matt McFadden',
    author_email='TODO',
    python_requires='>=3.6.0',
    url='https://github.com/mcfadd/Job_Shop_Schedule_Problem',
    license='MIT',
    keywords='Job Shop Schedule',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    entry_points={
        'console_scripts': ['jssp=JSSP.main:command_line_interface'],
    },
    install_requires=REQUIRED,
    ext_modules=cythonize(ext_modules)
)
