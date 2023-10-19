# Library imports
import numpy as np
import d6tflow as d6t
import luigi
from tqdm import tqdm

# Project imports
import pitch_control.generaltasks as gt
import pitch_control.parameters as pr
from pitch_control.cpitchcontrol import cCalcPitchControlFrame

class CalcPitchControlFrame(d6t.tasks.TaskPickle):
    match_id = d6t.IntParameter()
    half = d6t.IntParameter()
    frame_num = d6t.IntParameter()

    persist = ['PPCFa', 'PPCFd']

    def requires(self):
        return {'params': pr.PCModelParameters(),
                'init_frame': self.clone(gt.InitialiseFrame)}

    def run(self):
        params = self.input()['params'].load()  # Model parameters
        attacking_players = self.input()['init_frame'].load()['attacking_players']
        defending_players = self.input()['init_frame'].load()['defending_players']
        ball_position = self.input()['init_frame'].load()['ball_position']

        field_dimen = (105.0, 68.0)
        n_grid_cells_x = 50

        PPCFa, PPCFd = cCalcPitchControlFrame(attacking_players, defending_players, ball_position[0], ball_position[1], params,
                                              n_grid_cells_x, field_dimen[0], field_dimen[1])

        self.save({'PPCFa': PPCFa, 'PPCFd': PPCFd})