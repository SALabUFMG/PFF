# Library imports
import d6tflow as d6t

# Project imports
import data_processing.dataimport as di
from data_processing import loaders as ld
from tqdm import tqdm

import pitch_control.pitchcontrol as pc
import pitch_control.transitionprobability as tp


class ScalePCTP(d6t.tasks.TaskCache):
    att_n = d6t.IntParameter()
    def_n = d6t.IntParameter()

    def requires(self):
        return (ld.FramesLoader(competition="PL"), ld.SPADLLoader(competition="PL"))

    def run(self):
        frames_general = self.input()[0]["frames_general"].load()
        frames_coords = self.input()[0]["frames_coords"].load()
        actions = self.input()[1].load()

        atts_n = (
            frames_coords[frames_coords["team_status"] == "offense"]
            .groupby(by="event_id", as_index=False)
            .size()
        )
        atts_n = atts_n[atts_n["size"] >= self.att_n]
        defs_n = (
            frames_coords[frames_coords["team_status"] == "defense"]
            .groupby(by="event_id", as_index=False)
            .size()
        )
        defs_n = defs_n[defs_n["size"] >= self.def_n]

        frames_general["frame_order"] = (
            frames_general.groupby("match_id", as_index=False)["frame"].rank(
                method="first"
            )
            - 1
        )
        frames_general["frame_order"] = frames_general["frame_order"].astype(int)
        # frames_general = frames_general[frames_general['type_id'] == 1]
        frames_general = frames_general[
            (frames_general["event_id"].isin(atts_n["event_id"]))
            & (frames_general["event_id"].isin(defs_n["event_id"]))
        ]
        actions = (
            actions[["event_id"]]
            .merge(
                frames_general[["event_id", "match_id", "frame_order"]], on="event_id"
            )
            .reset_index(drop=True)
        )

        match_ids = actions["match_id"].values.tolist()
        frame_ids = actions["frame_order"].values.tolist()
        for i in tqdm(range(len(match_ids))):
            task = tp.CalcTransitionProbabilityFrame(
                match_id=match_ids[i], frame_id=frame_ids[i]
            )
            if not task.complete():
                d6t.run(task)

        print("finished!")


class AggregatePCTP(d6t.tasks.TaskPickle):
    def requires(self):
        return {
            "event_type": di.GetAllEventTypeFrames(event_id=1),
            "min_players": di.GetAllMinPlayersFrames(min_att=7, min_def=7),
        }

    def run(self):
        match_frame_ids = self.input()["event_type"].load()
        min_players_ids = self.input()["min_players"].load()

        temp = set(min_players_ids)
        tups = [tup for tup in match_frame_ids if tup in temp]

        PPCFa = []
        match_frame_ids = []

        for tup in tqdm(tups, desc="Running PC and TP frames: "):
            if pc.CalcPitchControlFrame(match_id=tup[0], frame_id=tup[1]).complete():
                PPCFa.append(
                    pc.CalcPitchControlFrame(match_id=tup[0], frame_id=tup[1])
                    .output()["PPCFa"]
                    .load()
                )
                match_frame_ids.append(tup)

        self.save({"PPCFa": PPCFa, "match_frame_ids": match_frame_ids})
