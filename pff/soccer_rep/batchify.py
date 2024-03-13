# Library imports
import os
import pickle
from tqdm import tqdm
import d6tflow as d6t
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader

# Project imports
from pff.data_process import tracking as tr
from pff.pitch_control import pitchcontrol as pc

class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

class SurfaceBatches(d6t.tasks.TaskCache):
    frames = d6t.ListParameter()
    batch_size = d6t.IntParameter(default=32)
    shuffle = d6t.BoolParameter(default=False)

    def requires(self):
        reqs = []
        for f in self.frames:
            reqs.append(pc.CalcPitchControlFrame(match_id=4494, half=1, frame_num=f))

        return reqs

    def run(self):
        PPCFs = []

        for ppcf in self.input():
            ppcf = ppcf['PPCFa'].load()
            PPCFs.append(ppcf[-1:, :, :])

        PPCFs = np.concatenate(PPCFs)

        PPCFs = PPCFs.reshape((PPCFs.shape[0], 1, PPCFs.shape[1], PPCFs.shape[2]))

        PPCFs = DataLoader(CustomDataset(PPCFs), batch_size=self.batch_size, shuffle=self.shuffle)

        self.save(PPCFs)