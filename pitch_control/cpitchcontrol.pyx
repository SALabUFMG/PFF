import numpy as np
cimport numpy as np
import cmath

def cCalcPitchControlTarget(float target_x, float target_y, list attacking_players, list defending_players, float ball_x, float ball_y, dict params):
    # calculate ball travel time from start position to end position.
    # ball travel time is distance to target position from current ball position divided assumed average ball speed
    cdef float ball_travel_time = cmath.sqrt(pow(target_x - ball_x, 2) + pow(target_y - ball_y, 2)).real / params['average_ball_speed']

    for p in attacking_players:
        p.simple_time_to_intercept(target_x, target_y)
    for p in defending_players:
        p.simple_time_to_intercept(target_x, target_y)

    # first get arrival time of 'nearest' attacking player (nearest also dependent on current velocity)
    cdef float tau_min_att = np.nanmin([p.simple_time_to_intercept(target_x, target_y) for p in attacking_players])
    cdef float tau_min_def = np.nanmin([p.simple_time_to_intercept(target_x, target_y) for p in defending_players])

    # solve pitch control model by integrating equation 3 in Spearman et al.
    # set up integration arrays
    cdef np.ndarray[np.double_t] dT_array = np.arange(ball_travel_time - params['int_dt'], ball_travel_time + params['max_int_time'], params['int_dt'])
    cdef np.ndarray[np.double_t] PPCFatt = np.zeros_like(dT_array)
    cdef np.ndarray[np.double_t] PPCFdef = np.zeros_like(dT_array)
    # integration equation 3 of Spearman 2018 until convergence or tolerance limit hit (see 'params')
    cdef float ptot = 0.0
    cdef int i = 1
    cdef float T
    cdef float dPPCFdT

    while 1 - ptot > params['model_converge_tol'] and i < dT_array.size:
        T = dT_array[i]
        for player in attacking_players:
            # calculate ball control probablity for 'player' in time interval T+dt
            dPPCFdT = (1 - PPCFatt[i - 1] - PPCFdef[i - 1]) * player.probability_intercept_ball(T) * params['lambda_att']
            # make sure it's greater than zero
            assert dPPCFdT >= 0, 'Invalid attacking player probability (CalcPitchControlTarget)'
            player.PPCF += dPPCFdT * params['int_dt']  # total contribution from individual player
            PPCFatt[i] += player.PPCF  # add to sum over players in the attacking team
        for player in defending_players:
            # calculate ball control probablity for 'player' in time interval T+dt
            dPPCFdT = (1 - PPCFatt[i - 1] - PPCFdef[i - 1]) * player.probability_intercept_ball(T) * params['lambda_def']
            # make sure it's greater than zero
            assert dPPCFdT >= 0, 'Invalid defending player probability (CalcPitchControlTarget)'
            player.PPCF += dPPCFdT * params['int_dt']  # total contribution from individual player
            PPCFdef[i] += player.PPCF  # add to sum over players in the defending team
        ptot = PPCFdef[i] + PPCFatt[i]  # total pitch control probability
        i += 1
    
    '''if i >= dT_array.size:
        print("Integration failed to converge: %1.3f" % (ptot))'''

    return attacking_players, defending_players

def cCalcPitchControlFrame(list attacking_players, list defending_players, float ball_x, float ball_y, dict params, int n_grid_cells_x, float field_x, float field_y):
    cdef int att_n = len(attacking_players)
    cdef int def_n = len(defending_players)

    # break the pitch down into a grid
    cdef int n_grid_cells_y = int(n_grid_cells_x * field_y / field_x)
    cdef np.ndarray[np.double_t] xgrid = np.linspace(-field_x / 2., field_x / 2., n_grid_cells_x)
    cdef np.ndarray[np.double_t] ygrid = np.linspace(-field_y / 2., field_y / 2., n_grid_cells_y)

    # initialise pitch control grids for attacking and defending teams np.zeros(shape=(len(ygrid), len(xgrid)))
    cdef np.ndarray[np.double_t, ndim=3] PPCFa = np.zeros(shape=(att_n + 1, len(ygrid), len(xgrid)))
    cdef np.ndarray[np.double_t, ndim=3] PPCFd = np.zeros(shape=(def_n + 1, len(ygrid), len(xgrid)))

    cdef float target_x
    cdef float target_y

    # calculate pitch pitch control model at each location on the pitch
    for i in range(len(ygrid)):
        for j in range(len(xgrid)):
            target_y = ygrid[i]
            target_x = xgrid[j]

            attacking_players, def_pls = cCalcPitchControlTarget(target_x, target_y, attacking_players, defending_players, ball_x, ball_y, params)

            for k in range(att_n):
                PPCFa[-1, i, j] += attacking_players[k].PPCF
                PPCFa[k, i, j] = attacking_players[k].PPCF
                attacking_players[k].PPCF = 0
                attacking_players[k].time_to_intercept = 0
            for k in range(def_n):
                PPCFd[-1, i, j] += defending_players[k].PPCF
                PPCFd[k, i, j] = defending_players[k].PPCF
                defending_players[k].PPCF = 0
                defending_players[k].time_to_intercept = 0

    return PPCFa, PPCFd