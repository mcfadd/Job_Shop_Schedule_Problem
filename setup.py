#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup, Extension
import pathlib

__version__ = '1.0.0'

README = (pathlib.Path(__file__).parent / "README.md").read_text()


class NumpyExtension(Extension):
    # setuptools calls this function after installing dependencies
    def _convert_pyx_sources_to_lang(self):
        import numpy
        self.include_dirs.append(numpy.get_include())
        # include libraries and compile flags if not on Windows
        if os.name != 'nt':
            self.libraries.append('m')
            self.extra_compile_args.append('-ffast-math')
        super()._convert_pyx_sources_to_lang()


ext_modules = [NumpyExtension('JSSP.genetic_algorithm._ga_helpers',
                              ['JSSP/genetic_algorithm/_ga_helpers.pyx']),
               NumpyExtension('JSSP.solution._makespan',
                              ['JSSP/solution/_makespan.pyx']),
               NumpyExtension('JSSP.tabu_search._generate_neighbor',
                              ['JSSP/tabu_search/_generate_neighbor.pyx'])
               ]

setup(
    name='JSSP',
    version=__version__,
    description='Package for solving the job shop schedule problem with sequence dependent set up times.',
    author='Matt McFadden (mcfadd)',
    author_email='mrfadd8@gmail.com',
    python_requires='>=3.6.0',
    url='https://github.com/mcfadd/Job_Shop_Schedule_Problem',
    download_url='https://github.com/mcfadd/Job_Shop_Schedule_Problem/archive/' + __version__ + '.tar.gz',
    license='ISC',
    keywords=['Job Shop Schedule Problem', 'Optimization', 'Tabu Search', 'Genetic Algorithm'],
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Cython',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Office/Business :: Scheduling',
    ],
    setup_requires=['numpy', 'cython'],
    install_requires=['numpy', 'plotly', 'progressbar', 'XlsxWriter'],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    ext_modules=ext_modules,
)
