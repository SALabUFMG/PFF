# Library imports
import d6tflow as d6t
import matplotlib.pyplot as plt
import numpy as np

# Project imports
from ..data_process import tracking as tr
from ..pitch_control import pitchcontrol as pc
from . import pitch as pt


@d6t.inherits(tr.LoadTrackingHalf)
class Frame(d6t.tasks.TaskCache):
    frame_num = d6t.IntParameter()
    velocities = d6t.BoolParameter(default=True)
    shirt_number = d6t.BoolParameter(default=True)
    left_to_right = d6t.BoolParameter(
        default=False
    )  # attacking team always plays from left to right
    pitch_control = d6t.BoolParameter(default=False)

    def requires(self):
        reqs = {"tracking": self.clone(tr.LoadTrackingHalf)}
        if not self.pitch_control:
            return reqs
        else:
            reqs["pitch_control"] = self.clone(pc.CalcPitchControlFrame)
            return reqs

    def run(self):
        d6t.run(pt.Pitch(), forced_all=True)
        pitch = pt.Pitch().output().load()
        fig = pitch["fig"]
        ax = pitch["ax"]

        player_colors = ("r", "b")  # Player colors (red and blue)
        # surface_color = "Reds"

        frames = self.input()["tracking"]["frames"].load()
        frames = frames[frames["frame_num"] == self.frame_num]

        players = self.input()["tracking"]["players"].load()
        first_players = players[players["frame_num"] == players["frame_num"].min()]
        players = players[players["frame_num"] == self.frame_num]
        closest_right_touchline = first_players.loc[
            first_players["x"] == first_players["x"].max(), "team"
        ].values[0]

        if frames["home_ball"].values[0] == 1:
            if self.left_to_right and closest_right_touchline == "home":
                players[["x", "y", "vx", "vy", "ax", "ay"]] *= -1
                frames[["ball_x", "ball_y"]] *= -1
            attacking_players = players[players["team"] == "home"]
            defending_players = players[players["team"] == "away"]
        else:
            if self.left_to_right and closest_right_touchline == "away":
                players[["x", "y", "vx", "vy", "ax", "ay"]] *= -1
                frames[["ball_x", "ball_y"]] *= -1
            attacking_players = players[players["team"] == "away"]
            defending_players = players[players["team"] == "home"]

        # plot home & away teams in order
        for team, color in zip([attacking_players, defending_players], player_colors):
            ax.plot(
                team["x"],
                team["y"],
                color + "o",
                markeredgecolor="black",
                markersize=10,
                alpha=0.7,
            )  # plot player positions

            if self.velocities:
                ax.quiver(
                    team["x"],
                    team["y"],
                    team["vx"],
                    team["vy"],
                    color=color,
                    scale_units="x",
                    scale=1.0,
                    width=0.0015,
                    headlength=5,
                    headwidth=3,
                    alpha=0.7,
                )

            if self.shirt_number:
                for _, row in team.iterrows():
                    x_coord = row["x"] + 0.5
                    y_coord = row["y"] + 0.5
                    shirt_number = row["shirt_number"]
                    ax.text(x_coord, y_coord, shirt_number, fontsize=10, color=color)

        if self.pitch_control:
            field_dimen = (105.0, 68.0)
            n_grid_cells_x = 50
            xgrid = np.linspace(
                -field_dimen[0] / 2.0, field_dimen[0] / 2.0, n_grid_cells_x
            )
            n_grid_cells_y = int(n_grid_cells_x * field_dimen[1] / field_dimen[0])
            ygrid = np.linspace(
                -field_dimen[1] / 2.0, field_dimen[1] / 2.0, n_grid_cells_y
            )
            PPCFa = self.input()["pitch_control"]["PPCFa"].load()
            if (
                frames["home_ball"].values[0] == 1
                and not self.left_to_right
                and closest_right_touchline == "home"
            ) or (
                frames["home_ball"].values[0] == 0
                and not self.left_to_right
                and closest_right_touchline == "home"
            ):
                PPCFa = PPCFa[:, ::-1, ::-1]
            ax.imshow(
                np.flipud(PPCFa[-1, :, :]),
                extent=(np.amin(xgrid), np.amax(xgrid), np.amin(ygrid), np.amax(ygrid)),
                interpolation="hanning",
                vmin=0.0,
                vmax=1.0,
                cmap="bwr",
                alpha=0.625,
            )
            cb = fig.colorbar(
                plt.cm.ScalarMappable(norm=None, cmap="bwr"),
                ax=ax,
                alpha=0.625,
                shrink=0.80,
            )
            cb.ax.tick_params(labelsize=14)

        # plot ball
        ax.plot(
            frames["ball_x"],
            frames["ball_y"],
            "ko",
            markersize=6,
            alpha=1.0,
            linewidth=0,
        )

        # plot axis labels
        ax.set_xlabel("x (m)", fontsize=20)
        ax.set_ylabel("y (m)", fontsize=20)
        ax.tick_params(labelsize=14)

        # ax.set_title(self.gameid, fontdict={'fontsize': 30})
        fig.tight_layout()
        fig.show()

        # fig.savefig(
        #     d6t.settings.dir + '\\' + str(self.match_id) + '_' + str(self.frame_id)
        # )

        self.save(ax)
