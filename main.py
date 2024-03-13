import d6tflow as d6t
from torch import nn

from pff.data_process import tracking as tr
from pff.pitch_control import pitchcontrol as pc
from pff.soccer_rep import batchify as btf

d6t.settings

# Para dar build no módulo de Pitch Control
# Instale Cython no seu ambiente de programação
# (pip install cython ou conda install cython)
# No terminal:
# cd 'your_path/PFF/pitch_control'
# python setup.py build_ext --inplace

# d6t.run(tr.LoadTrackingHalf(match_id=4494, half=1))

task_1 = tr.LoadTrackingHalf(match_id=4494, half=1)
d6t.run(task_1)
frames = task_1.output()["frames"].load()
players = task_1.output()["players"].load()
game_events = task_1.output()["game_events"].load()
possession_events = task_1.output()["possession_events"].load()

passes = possession_events[possession_events['possession_event_type'] == 'PA']
frames = passes['start_frame'].unique().tolist()

calc_frames = []
for f in frames:
    task = pc.CalcPitchControlFrame(match_id=4494, half=1, frame_num=f)
    if task.complete():
        calc_frames.append(f)

task = btf.SurfaceBatches(frames=calc_frames)
d6t.run(task)

batches = task.output().load()

conv1 = nn.Sequential(
    nn.ZeroPad2d(1),
    nn.Conv2d(1, 8, kernel_size=(3, 3), stride=1, padding='valid', dtype=float),
    nn.ReLU(),
    nn.MaxPool2d(2, 2)
)
conv2 = nn.Sequential(
    nn.ZeroPad2d(1),
    nn.Conv2d(8, 8, kernel_size=(3, 3), stride=1, padding='valid', dtype=float),
    nn.ReLU(),
    nn.MaxPool2d(2, 2)
)
fusion = nn.Sequential(
    nn.ZeroPad2d(1),
    nn.Conv2d(8, 1, kernel_size=(3, 3), stride=1, padding='valid', dtype=float),
    nn.ReLU()
)

for batch in batches:
    continue

forw1 = conv1(batch)
forw2 = conv2(forw1)
forw3 = conv2(forw2)
z1 = fusion(forw1)
z2 = fusion(forw2)
z3 = fusion(forw3)