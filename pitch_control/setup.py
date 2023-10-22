import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

cyplayer_module = Extension(
    name="cyplayer", sources=["cyplayer.pyx"], include_dirs=[np.get_include()]
)

setup(ext_modules=cythonize([cyplayer_module]))

pc_module = Extension(
    "cpitchcontrol", sources=["cpitchcontrol.pyx"], include_dirs=[np.get_include()]
)
setup(ext_modules=cythonize([pc_module]))

tp_module = Extension(
    "ctransitionprobability",
    sources=["ctransitionprobability.pyx"],
    include_dirs=[np.get_include()],
)
setup(ext_modules=cythonize([tp_module]))

"""setup(
    name='pc',
    version='1.0',
    author='Hugo',
    ext_modules=[pc_module]
)"""
