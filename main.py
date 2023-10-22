import d6tflow as d6t
from pff.visualize import frame as fr

d6t.settings

# Para dar build no módulo de Pitch Control
# Instale Cython no seu ambiente de programação
# (pip install cython ou conda install cython)
# No terminal:
# cd 'your_path/PFF/pitch_control'
# python setup.py build_ext --inplace

# d6t.run(tr.LoadTrackingHalf(match_id=4494, half=1))

d6t.run(fr.Frame(match_id=4494, half=1, frame_num=3786, pitch_control=True))

# d6t.run(pc.CalcPitchControlFrame(match_id=4494, half=1, frame_num=717))
