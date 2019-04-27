from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize

ext_modules = [Extension("ga_helpers",
                         ["ga_helpers.pyx"],
                         libraries=["m"],
                         extra_compile_args=["-ffast-math"],
                         include_dirs=[numpy.get_include()])]

setup(
    ext_modules=cythonize(ext_modules, annotate=True)
)
