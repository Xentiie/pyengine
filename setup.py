from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("maths3d.pyx", annotate=True, force=True),
    name="maths3d",
    include_dirs=[numpy.get_include()]
)