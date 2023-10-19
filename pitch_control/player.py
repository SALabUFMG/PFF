# Library imports
import numpy as np
import d6tflow as d6t
import luigi

# Project imports

class player(object):
    """
    player() class

    Class defining a player object that stores position, velocity, time-to-intercept and pitch control contributions for a player

    __init__ Parameters
    -----------
    pid: id (jersey number) of player
    team: row of tracking data for team
    teamname: team name "Home" or "Away"
    params: Dictionary of model parameters (default model parameters can be generated using default_model_params() )

    methods include:
    -----------
    simple_time_to_intercept(r_final): time take for player to get to target position (r_final) given current position
    probability_intercept_ball(T): probability player will have controlled ball at time T given their expected time_to_intercept

    """

    # player object holds position, velocity, time-to-intercept and pitch control contributions for each player
    def __init__(self, player_data, params):
        self.id = player_data['player_id']
        self.vmax = params['max_player_speed']  # player max speed in m/s. Could be individualised
        self.reaction_time = params['reaction_time']  # player reaction time in 's'. Could be individualised
        self.tti_sigma = params['tti_sigma']  # standard deviation of sigmoid function (see Eq 4 in Spearman, 2018)
        self.position = np.array([player_data['x'], player_data['y']])
        self.velocity = np.array([player_data['vx'], player_data['vy']])
        self.PPCF = 0.  # initialise this for later

    def simple_time_to_intercept(self, r_final):
        # Time to intercept assumes that the player continues moving at current velocity for 'reaction_time' seconds
        # and then runs at full speed to the target position.
        r_reaction = self.position + self.velocity * self.reaction_time
        self.time_to_intercept = self.reaction_time + np.linalg.norm(r_final - r_reaction) / self.vmax
        return self.time_to_intercept

    def probability_intercept_ball(self, T):
        # probability of a player arriving at target location at time 'T' given their expected time_to_intercept (time of arrival), as described in Spearman 2018
        f = 1 / (1. + np.exp(-np.pi / np.sqrt(3.0) / self.tti_sigma * (T - self.time_to_intercept)))
        return f