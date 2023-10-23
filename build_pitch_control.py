import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

cyplayer_module = Extension(
    name="pff.pitch_control.cyplayer",
    sources=["pff/pitch_control/cyplayer.pyx"],
    include_dirs=[np.get_include()],
)

pc_module = Extension(
    name="pff.pitch_control.cpitchcontrol",
    sources=["pff/pitch_control/cpitchcontrol.pyx"],
    include_dirs=[np.get_include()],
)

tp_module = Extension(
    name="pff.pitch_control.ctransitionprobability",
    sources=["pff/pitch_control/ctransitionprobability.pyx"],
    include_dirs=[np.get_include()],
)

setup(ext_modules=cythonize([cyplayer_module, pc_module, tp_module]))
