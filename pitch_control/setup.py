import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

cyplayer_module = Extension(
    name="cyplayer",
    sources=["cyplayer.pyx"],
    include_dirs=[np.get_include()],
)

pc_module = Extension(
    name="cpitchcontrol",
    sources=["cpitchcontrol.pyx"],
    include_dirs=[np.get_include()],
)

tp_module = Extension(
    name="ctransitionprobability",
    sources=["ctransitionprobability.pyx"],
    include_dirs=[np.get_include()],
)

setup(ext_modules=cythonize([cyplayer_module, pc_module, tp_module]))
