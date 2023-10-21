import numpy as np

cimport numpy as np

from scipy.stats import multivariate_normal
from scipy.stats._multivariate import multivariate_normal_frozen


def cCalcTransitionProbabilityFrame(np.ndarray PPCFa, float ball_x, float ball_y, dict params, int n_grid_cells_x, float field_x, float field_y):
    # break the pitch down into a grid
    cdef int n_grid_cells_y = int(n_grid_cells_x * field_y / field_x)
    cdef np.ndarray[np.double_t] xgrid = np.linspace(-field_x / 2., field_x / 2., n_grid_cells_x)
    cdef np.ndarray[np.double_t] ygrid = np.linspace(-field_y / 2., field_y / 2., n_grid_cells_y)

    # initialise transition grid
    cdef np.ndarray[np.double_t, ndim=2] TP = np.zeros(shape=(len(ygrid), len(xgrid)))

    # calculate transition model at each location on the pitch
    cdef np.ndarray[np.double_t, ndim=1] target_position
    cdef np.ndarray[np.double_t, ndim=1] ball_position = np.array([ball_x, ball_y])
    cdef float sigma_2 = params['sigma_normal']**2
    cdef normal_distrib
    for i in range(len(ygrid)):
        for j in range(len(xgrid)):
            target_position = np.array([xgrid[j], ygrid[i]])
            normal_distrib = multivariate_normal(mean=ball_position, cov=[[sigma_2, 0], [0, sigma_2]])
            TP[i, j] = PPCFa[i, j]**(params['alpha']) * normal_distrib.pdf(target_position)

    # normalize T to unity
    TP = TP / np.sum(TP)

    return TP
