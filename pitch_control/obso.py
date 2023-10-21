# Library imports
import d6tflow as d6t

# Project imports
import dataimport as di
import numpy as np

import execution as ex
import xg


class OBSO(d6t.tasks.TaskCache):
    def requires(self):
        return {
            "PCTP": ex.AggregatePCTP(),
            "xG": xg.CalcXGFrame(),
            "event_type": di.GetAllEventTypeFrames(event_id=1),
            "min_players": di.GetAllMinPlayersFrames(min_att=7, min_def=7),
        }

    def run(self):
        pctp = self.input()["PCTP"].load()
        ppcfa = pctp["PPCFa"]
        tp = pctp["TP"]
        del pctp
        xgg = self.input()["xG"].load()

        obso = []

        for i in range(len(ppcfa)):
            obso.append(ppcfa[i] * tp[i] * xgg)

        obso = np.concatenate(obso)
        totals = np.sum(a=obso, axis=(1, 2))
        maxes = np.argsort(totals)

        match_frame_ids = self.input()["event_type"].load()
        min_players_ids = self.input()["min_players"].load()

        temp = set(min_players_ids)
        tups = [tup for tup in match_frame_ids if tup in temp]

        ordered_tups = []
        for i in range(len(ppcfa)):
            counter = 0
            for j in range(len(ppcfa)):
                counter += ppcfa[j].shape[0]
                if counter >= maxes[-(i + 1)]:
                    break
            ordered_tups.append(tups[j])

        self.save(ordered_tups)
