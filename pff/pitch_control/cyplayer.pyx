# distutils: language = c++

from .Player cimport Player


# Create a Cython extension type which holds a C++ instance
# as an attribute and create a bunch of forwarding methods
# Python extension type.
cdef class CyPlayer:
    cdef Player cpp_player  # Hold a C++ instance which we're wrapping

    def __cinit__(self, int id, float position_x, float position_y, float velocity_x, float velocity_y, float vmax, float reaction_time, float tti_sigma):
        self.cpp_player = Player(id, position_x, position_y, velocity_x, velocity_y, vmax, reaction_time, tti_sigma)

    def simple_time_to_intercept(self, float target_x, float target_y):
        return self.cpp_player.simple_time_to_intercept(target_x, target_y)

    def probability_intercept_ball(self, float t):
        return self.cpp_player.probability_intercept_ball(t)

    @property
    def id(self):
        return self.cpp_player.id

    @property
    def position_x(self):
        return self.cpp_player.position_x

    @property
    def position_y(self):
        return self.cpp_player.position_y

    @property
    def velocity_x(self):
        return self.cpp_player.velocity_x

    @property
    def velocity_y(self):
        return self.cpp_player.velocity_y

    @property
    def time_to_intercept(self):
        return self.cpp_player.time_to_intercept
    @time_to_intercept.setter
    def time_to_intercept(self, time_to_intercept):
        self.cpp_player.time_to_intercept = time_to_intercept

    @property
    def PPCF(self):
        return self.cpp_player.PPCF
    @PPCF.setter
    def PPCF(self, PPCF):
        self.cpp_player.PPCF = PPCF
