cdef extern from "Player.cpp":
    pass

# Declare the class with cdef
cdef extern from "Player.h" namespace "football":
    cdef cppclass Player:
        Player() except +
        Player(int, float, float, float, float, float, float, float) except +
        int id
        float position_x, position_y, velocity_x, velocity_y, vmax, reaction_time, tti_sigma, PPCF, time_to_intercept
        float simple_time_to_intercept(float target_x, float target_y)
        float probability_intercept_ball(float t)
