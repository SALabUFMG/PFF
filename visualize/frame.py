# Library imports
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
import d6tflow as d6t
import copy
import pandas as pd
import torch

# Project imports
from data_process import tracking as tr
from visualize import pitch as pt

@d6t.inherits(tr.LoadTrackingHalf)
class Frame(d6t.tasks.TaskCache):
    frame_num = d6t.IntParameter()
    velocities = d6t.BoolParameter(default=True)
    shirt_number = d6t.BoolParameter(default=True)

    def requires(self):
        return self.clone(tr.LoadTrackingHalf)

    def run(self):
        d6t.run(pt.Pitch(), forced_all=True)
        pitch = pt.Pitch().output().load()
        fig = pitch['fig']
        ax = pitch['ax']

        player_colors = ('r', 'b')  # Player colors (red and blue)
        surface_color = 'Reds'

        frames = self.input()['frames'].load()
        frames = frames[frames['frame_num'] == self.frame_num]

        players = self.input()['players'].load()
        players = players[players['frame_num'] == self.frame_num]

        if frames['home_ball'].values[0] == 1:
            attacking_players = players[players['team'] == 'home']
            defending_players = players[players['team'] == 'away']
        else:
            attacking_players = players[players['team'] == 'away']
            defending_players = players[players['team'] == 'home']

        # plot home & away teams in order
        for team, color in zip([attacking_players, defending_players], player_colors):
            ax.plot(team['x'], team['y'], color + 'o', markeredgecolor='black', markersize=10, alpha=0.7)  # plot player positions

            if self.velocities:
                ax.quiver(team['x'], team['y'], team['vx'], team['vy'], color=color, scale_units='x', scale=1., width=0.0015, headlength=5, headwidth=3, alpha=0.7)

            if self.shirt_number:
                for _, row in team.iterrows():
                    x_coord = row['x'] + 0.5
                    y_coord = row['y'] + 0.5
                    shirt_number = row['shirt_number']
                    ax.text(x_coord, y_coord, shirt_number, fontsize=10, color=color)

        # plot ball
        ax.plot(frames['ball_x'], frames['ball_y'], 'ko', markersize=6, alpha=1.0, linewidth=0)

        # plot axis labels
        ax.set_xlabel('x (m)', fontsize=20)
        ax.set_ylabel('y (m)', fontsize=20)
        ax.tick_params(labelsize=14)

        # ax.set_title(self.gameid, fontdict={'fontsize': 30})
        fig.tight_layout()
        fig.show()

        #fig.savefig(d6t.settings.dir + '\\' + str(self.match_id) + '_' + str(self.frame_id))

        self.save(ax)