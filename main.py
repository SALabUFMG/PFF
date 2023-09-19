import d6tflow as d6t
from data_process import tracking as tr

d6t.settings

d6t.run(tr.LoadTrackingHalf(match_id=4494, half=1, path_name="/Users/hugo-gemini/Documents/UFMG/SALab/Data/PFF/Raw"))