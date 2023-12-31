# Library imports
import d6tflow as d6t
import matplotlib.pyplot as plt
import numpy as np


class Pitch(d6t.tasks.TaskCache):
    linewidth = d6t.IntParameter(default=2)
    markersize = d6t.IntParameter(default=20)
    field_color = d6t.Parameter(default="white")

    def run(self):
        field_dimen = (105.0, 68.0)  # Field dimensions

        fig, ax = plt.subplots(figsize=(12, 8))  # create a figure

        # decide what color we want the field to be.
        # Default is green, but can also choose white
        if self.field_color == "green":
            ax.set_facecolor("mediumseagreen")
            lc = "whitesmoke"  # line color
            pc = "w"  # 'spot' colors
        elif self.field_color == "white":
            lc = "k"
            pc = "k"
        # ALL DIMENSIONS IN m
        border_dimen = (3, 3)  # include a border arround of the field of width 3m
        meters_per_yard = 0.9144  # unit conversion from yards to meters
        half_pitch_length = field_dimen[0] / 2.0  # length of half pitch
        half_pitch_width = field_dimen[1] / 2.0  # width of half pitch
        signs = [-1, 1]
        # Soccer field dimensions typically defined in yards,
        # so we need to convert to meters
        goal_line_width = 8 * meters_per_yard
        box_width = 20 * meters_per_yard
        box_length = 6 * meters_per_yard
        area_width = 44 * meters_per_yard
        area_length = 18 * meters_per_yard
        penalty_spot = 12 * meters_per_yard
        corner_radius = 1 * meters_per_yard
        D_length = 8 * meters_per_yard
        D_radius = 10 * meters_per_yard
        D_pos = 12 * meters_per_yard
        centre_circle_radius = 10 * meters_per_yard
        # plot half way line # center circle
        ax.plot(
            [0, 0], [-half_pitch_width, half_pitch_width], lc, linewidth=self.linewidth
        )
        ax.scatter(0.0, 0.0, marker="o", facecolor=lc, linewidth=0, s=self.markersize)
        y = np.linspace(-1, 1, 50) * centre_circle_radius
        x = np.sqrt(centre_circle_radius**2 - y**2)
        ax.plot(x, y, lc, linewidth=self.linewidth)
        ax.plot(-x, y, lc, linewidth=self.linewidth)
        for s in signs:  # plots each line seperately
            # plot pitch boundary
            ax.plot(
                [-half_pitch_length, half_pitch_length],
                [s * half_pitch_width, s * half_pitch_width],
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length],
                [-half_pitch_width, half_pitch_width],
                lc,
                linewidth=self.linewidth,
            )
            # goal posts & line
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length],
                [-goal_line_width / 2.0, goal_line_width / 2.0],
                pc + "s",
                markersize=6 * self.markersize / 20.0,
                linewidth=self.linewidth,
            )
            # 6 yard box
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length - s * box_length],
                [box_width / 2.0, box_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length - s * box_length],
                [-box_width / 2.0, -box_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                [
                    s * half_pitch_length - s * box_length,
                    s * half_pitch_length - s * box_length,
                ],
                [-box_width / 2.0, box_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            # penalty area
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length - s * area_length],
                [area_width / 2.0, area_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                [s * half_pitch_length, s * half_pitch_length - s * area_length],
                [-area_width / 2.0, -area_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                [
                    s * half_pitch_length - s * area_length,
                    s * half_pitch_length - s * area_length,
                ],
                [-area_width / 2.0, area_width / 2.0],
                lc,
                linewidth=self.linewidth,
            )
            # penalty spot
            ax.scatter(
                s * half_pitch_length - s * penalty_spot,
                0.0,
                marker="o",
                facecolor=lc,
                linewidth=0,
                s=self.markersize,
            )
            # corner flags
            y = np.linspace(0, 1, 50) * corner_radius
            x = np.sqrt(corner_radius**2 - y**2)
            ax.plot(
                s * half_pitch_length - s * x,
                -half_pitch_width + y,
                lc,
                linewidth=self.linewidth,
            )
            ax.plot(
                s * half_pitch_length - s * x,
                half_pitch_width - y,
                lc,
                linewidth=self.linewidth,
            )
            # draw the D
            y = (
                np.linspace(-1, 1, 50) * D_length
            )  # D_length is the chord of the circle that defines the D
            x = np.sqrt(D_radius**2 - y**2) + D_pos
            ax.plot(s * half_pitch_length - s * x, y, lc, linewidth=self.linewidth)

        # remove axis labels and ticks
        """ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])"""
        # set axis limits
        xmax = field_dimen[0] / 2.0 + border_dimen[0]
        ymax = field_dimen[1] / 2.0 + border_dimen[1]
        ax.set_xlim([-xmax, xmax])
        ax.set_ylim([-ymax, ymax])
        ax.set_axisbelow(True)

        self.save({"fig": fig, "ax": ax})
