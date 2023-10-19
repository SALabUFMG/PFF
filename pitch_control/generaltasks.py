# Library imports
import numpy as np
import pandas as pd
import d6tflow as d6t
import luigi

# Project imports
import data_process.tracking as tr
import pitch_control.parameters as pr
from pitch_control.cyplayer import CyPlayer

class InitialiseFrame(d6t.tasks.TaskCache):
    match_id = d6t.IntParameter()
    half = d6t.IntParameter()
    frame_num = d6t.IntParameter()

    def requires(self):
        return {'tracking': self.clone(tr.LoadTrackingHalf),
                'params': pr.PCModelParameters()}

    def run(self):
        frames = self.input()['tracking']['frames'].load()
        frames = frames[frames['frame_num'] == self.frame_num]

        players = self.input()['tracking']['players'].load()
        first_players = players[players['frame_num'] == players['frame_num'].min()]
        players = players[players['frame_num'] == self.frame_num]
        closest_right_touchline = first_players.loc[first_players['x'] == first_players['x'].max(), 'team'].values[0]

        if frames['home_ball'].values[0] == 1:
            if closest_right_touchline == 'home':
                players[['x', 'y', 'vx', 'vy', 'ax', 'ay']] *= (-1)
                frames[['ball_x', 'ball_y']] *= (-1)
            att_players = players[players['team'] == 'home']
            def_players = players[players['team'] == 'away']
        else:
            if closest_right_touchline == 'away':
                players[['x', 'y', 'vx', 'vy', 'ax', 'ay']] *= (-1)
                frames[['ball_x', 'ball_y']] *= (-1)
            att_players = players[players['team'] == 'away']
            def_players = players[players['team'] == 'home']

        params = self.input()['params'].load()  # Model parameters

        attacking_players = []
        defending_players = []

        for p in att_players.itertuples():
            attacking_players.append(CyPlayer(p.player_id, p.x, p.y, p.vx, p.vy, params['max_player_speed'], params['reaction_time'], params['tti_sigma']))

        for p in def_players.itertuples():
            defending_players.append(CyPlayer(p.player_id, p.x, p.y, p.vx, p.vy, params['max_player_speed'], params['reaction_time'], params['tti_sigma']))

        ball_position = np.array([frames['ball_x'], frames['ball_y']])

        offsides_players = []

        # find the second-last defender
        x_defending_players = []
        for player in defending_players:
            x_defending_players.append(player.position_x)

        x_defending_players = np.sort(x_defending_players)
        second_last_defender_x = x_defending_players[-2]
        for player in attacking_players:
            position_x = player.position_x
            # if player is nearer to the opponent's goal than the ball
            if position_x > ball_position[0] and position_x > second_last_defender_x and position_x > 0:
                offsides_players.append(player)

        for op in offsides_players:
            attacking_players.remove(op)

        self.save({'attacking_players': attacking_players, 'defending_players': defending_players, 'ball_position': ball_position})