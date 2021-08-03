"""
Copyright (C) 2016 Yaniv Erlich
License: GPLv3-or-later. See COPYING file for details.
"""
# all .pyx files in a folder
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='NAMFountain',
    ext_modules=cythonize(["*.pyx"]),
)
