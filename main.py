import d6tflow as d6t
from data_process import tracking as tr
from visualize import frame as fr

d6t.settings

#d6t.run(tr.LoadTrackingHalf(match_id=4494, half=1))

d6t.run(fr.Frame(match_id=4494, half=1, frame_num=717))