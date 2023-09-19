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

class Frame(d6t.tasks.TaskCache):


    def requires(self):
        return {'init_frame': self.clone(gt.InitialiseFrame)}

    def run(self):
        attacking_players = self.input()['init_frame'].load()['attacking_players']
        defending_players = self.input()['init_frame'].load()['defending_players']
        ball_position = self.input()['init_frame'].load()['ball_position']

        d6t.run(Pitch(), forced_all=True)
        pitch = Pitch().output().load()
        fig = pitch['fig']
        ax = pitch['ax']

        player_colors = ('r', 'b')  # Player colors (red and blue)
        surface_color = 'Reds'

        # plot home & away teams in order
        for team, color in zip([attacking_players, defending_players], player_colors):
            x_positions = [p.position_x for p in team]
            y_positions = [p.position_y for p in team]
            ax.plot(x_positions, y_positions, color + 'o', markeredgecolor='black', markersize=10,
                    alpha=0.7)  # plot player positions

            '''if self.include_player_velocities:
                x_velocities = [p.velocity_x for p in team]
                y_velocities = [p.velocity_y for p in team]
                ax.quiver(team[x_columns].to_numpy(dtype=float), team[y_columns].to_numpy(dtype=float), 1, 1,
                          color=color, scale_units='inches', scale=10., width=0.0015, headlength=5, headwidth=3, alpha=0.7)

            if self.annotate:
                [ax.text(team[x] + 0.5, team[y] + 0.5, x.split('_')[1], fontsize=10, color=color) for x, y in
                 zip(x_columns, y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))]'''

        # plot ball
        ax.plot(ball_position[0], ball_position[1], 'ko', markersize=6, alpha=1.0, linewidth=0)

        xgrid = np.linspace(-self.field_dimen[0] / 2., self.field_dimen[0] / 2., self.n_grid_cells_x)
        n_grid_cells_y = int(self.n_grid_cells_x * self.field_dimen[1] / self.field_dimen[0])
        ygrid = np.linspace(-self.field_dimen[1] / 2., self.field_dimen[1] / 2., n_grid_cells_y)
        if self.do_pitchcontrol:
            task = pc.CalcPitchControlFrame(match_id=self.match_id, frame_id=self.frame_id)
            d6t.run(task)
            PC = task.output()['PPCFa'].load()
            import torch
            from soccer_rep import cvae as sr
            model = sr.SoccerRepCVAE(n_channels=1, width=50, height=32, latent_dim=25)
            model.load_state_dict(
                torch.load(
                    'D:\Hugo\Sports_Analytics_Personal\Football\Data\SoccerRep\TrainAutoEncoder\cvae_att_0_1_1.pkl',
                    map_location=torch.device('cpu'))
            )
            PC_t = torch.from_numpy(PC[3, :, :])[None, None, :, :]
            inputs = torch.cat([PC_t, PC_t, PC_t, PC_t, PC_t, PC_t, PC_t, PC_t], dim=0)
            outputs = model(inputs)
            PC_s = outputs[0][2, 0, :, :].detach().numpy()
            ax.imshow(np.flipud(PC_s), extent=(np.amin(xgrid), np.amax(xgrid), np.amin(ygrid), np.amax(ygrid)),
                      interpolation='hanning',
                      vmin=0.0, vmax=1.0, cmap='bwr', alpha=0.625)
            cb = fig.colorbar(plt.cm.ScalarMappable(norm=None, cmap='bwr'), ax=ax, alpha=0.625, shrink=0.80)
            cb.ax.tick_params(labelsize=14)

        # plot axis labels
        ax.set_xlabel('x (m)', fontsize=20)
        ax.set_ylabel('y (m)', fontsize=20)
        ax.tick_params(labelsize=14)

        # ax.set_title(self.gameid, fontdict={'fontsize': 30})
        fig.tight_layout()
        fig.show()

        fig.savefig(d6t.settings.dir + '\\' + str(self.match_id) + '_' + str(self.frame_id))

        self.save(ax)