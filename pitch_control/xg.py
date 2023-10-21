# Library imports
import d6tflow as d6t

# Project imports
import interfaces as itf
import luigi
import numpy as np


@d6t.inherits(itf.Pitch)
class CalcXGTarget(d6t.tasks.TaskCache):
    target_position = luigi.Parameter()

    def run(self):
        x = self.field_dimen[0] / 2 - self.target_position[0]
        y = self.target_position[1]

        a = np.arctan(7.32 * x / (x**2 + abs(y) ** 2 - (7.32 / 2) ** 2))
        if a < 0:
            a = np.pi + a
        angle = a
        distance = np.sqrt(x**2 + abs(y) ** 2)

        # coefficient determined thanks to expected goals modelhttps
        # https://github.com/Gabsrol/liverpool_analytics_challenge/blob/master/expected_goals_model.ipynb # noqa
        c1 = 0.1155
        c2 = -1.2594
        intercept = 0.7895

        bsum = intercept + c1 * distance + c2 * angle

        xG = 1 / (1 + np.exp(bsum))

        self.save(xG)


@d6t.inherits(itf.Pitch)
class CalcXGFrame(d6t.tasks.TaskPickle):
    def run(self):
        # break the pitch down into a grid
        n_grid_cells_y = int(
            self.n_grid_cells_x * self.field_dimen[1] / self.field_dimen[0]
        )
        xgrid = np.linspace(
            -self.field_dimen[0] / 2.0, self.field_dimen[0] / 2.0, self.n_grid_cells_x
        )
        ygrid = np.linspace(
            -self.field_dimen[1] / 2.0, self.field_dimen[1] / 2.0, n_grid_cells_y
        )

        # initialise expected goals
        xG = np.zeros(shape=(len(ygrid), len(xgrid)))

        # calculate pitch pitch control model at each location on the pitch
        for i in range(len(ygrid)):
            for j in range(len(xgrid)):
                target_position = np.array([xgrid[j], ygrid[i]])
                d6t.run(CalcXGTarget(target_position=tuple(target_position)))
                xG[i, j] = (
                    CalcXGTarget(target_position=tuple(target_position)).output().load()
                )

        self.save(xG)
