# Library imports
import d6tflow as d6t
import numpy as np


class PCModelParameters(d6t.tasks.TaskCache):
    """
    Dictionary with pitch control model parameters.
    Further explanation next to each parameter
    """

    def run(self):
        # If the probability that another team or player can get to the ball and
        # control it is less than 10^-time_to_control_veto, ignore that player.
        # key parameters for the model, as described in Spearman 2018
        time_to_control_veto = 3

        params = {}
        # model parameters
        params["max_player_accel"] = (
            7.0  # maximum player acceleration m/s/s, not used in this implementation
        )
        params["max_player_speed"] = 5.0  # maximum player speed m/s
        params["reaction_time"] = (
            # seconds, time taken for player to react and change trajectory.
            # Roughly determined as vmax/amax
            0.7
        )
        params["tti_sigma"] = (
            # Standard deviation of sigmoid function in Spearman 2018 ('s')
            # that determines uncertainty in player arrival time
            0.45
        )
        params["kappa_def"] = (
            # kappa parameter in Spearman 2018 (=1.72 in the paper) that gives
            # the advantage defending players to control ball, I have set to 1
            # so that home & away players have same ball control probability
            1.0
        )
        params["lambda_att"] = 4.3  # ball control parameter for attacking team
        params["lambda_def"] = (
            4.3 * params["kappa_def"]
        )  # ball control parameter for defending team
        params["average_ball_speed"] = 15.0  # average ball travel speed in m/s

        # numerical parameters for model evaluation
        params["int_dt"] = 0.04  # integration timestep (dt)
        params["max_int_time"] = 10  # upper limit on integral time
        params["model_converge_tol"] = (
            0.01  # assume convergence when PPCF>0.99 at a given location.
        )
        # The following are 'short-cut' parameters. We do not need to calculated
        # PPCF explicitly when a player has a sufficient head start.
        # A sufficient head start is when the a player arrives at the target location
        # at least 'time_to_control' seconds before the next player
        params["time_to_control_att"] = (
            time_to_control_veto
            * np.log(10)
            * (np.sqrt(3) * params["tti_sigma"] / np.pi + 1 / params["lambda_att"])
        )
        params["time_to_control_def"] = (
            time_to_control_veto
            * np.log(10)
            * (np.sqrt(3) * params["tti_sigma"] / np.pi + 1 / params["lambda_def"])
        )

        self.save(params)


class TModelParameters(d6t.tasks.TaskCache):
    """
    Dictionary with transition probability model parameters.
    Further explanation next to each parameter
    """

    def run(self):
        params = {}

        params["sigma_normal"] = (
            23.9  # Check William Spearman's "Beyond Expected Goals"
        )
        params["alpha"] = 1.04  # Check William Spearman's "Beyond Expected Goals"

        self.save(params)
