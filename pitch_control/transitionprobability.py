# Library imports
import numpy as np
import d6tflow as d6t
import luigi
from scipy.stats import multivariate_normal

# Project imports
import interfaces as itf
from pitch_control import generaltasks as gt
from pitch_control import parameters as pr
from pitch_control import pitchcontrol as pc
from pitch_control.ctransitionprobability import cCalcTransitionProbabilityFrame

@d6t.inherits(itf.Pitch, itf.Frame)
class CalcTransitionProbabilityFrame(d6t.tasks.TaskPickle):
    def requires(self):
        return {'params': pr.TModelParameters(),
                'init_frame': self.clone(gt.InitialiseFrame),
                'pc_frame': self.clone(pc.CalcPitchControlFrame)}

    def run(self):
        params = self.input()['params'].load()
        ball_position = self.input()['init_frame'].load()['ball_position']
        PPCFa = self.input()['pc_frame']['PPCFa'].load()[-1, :, :]

        # normalize T to unity
        TP = cCalcTransitionProbabilityFrame(PPCFa, ball_position[0], ball_position[1], params, self.n_grid_cells_x, self.field_dimen[0], self.field_dimen[1])

        self.save(TP)