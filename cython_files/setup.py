from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize

ext_modules = [Extension("makespan_compiled",
                         ["makespan_compiled.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()]),
               Extension("generate_neighbor_compiled",
                         ["generate_neighbor_compiled.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()])]

setup(
    ext_modules=cythonize(ext_modules, annotate=True)
)
