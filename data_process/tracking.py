import itertools
import d6tflow as d6t
import numpy as np
import pandas as pd

import base

class LoadTrackingHalf(d6t.tasks.TaskPickle):
    match_id = d6t.IntParameter()
    half = d6t.IntParameter()
    path_name = d6t.Parameter()

    persist = ['frames', 'players', 'game_events', 'possession_events']

    def run(self):
        raw_frames = pd.read_json(self.path_name + "/" + str(self.match_id) + "_" + str(self.half) + ".jsonl", lines=True)

        clean_frames = raw_frames.drop_duplicates(subset='frameNum').reset_index(drop=True)
        clean_frames = clean_frames.rename(columns={
            'gameRefId': 'game_ref_id',
            'generatedTime': 'generated_time',
            'videoTimeMs': 'video_time_ms',
            'frameNum': 'frame_num',
            'periodElapsedTime': 'period_elapsed_time',
            'periodGameClockTime': 'period_game_clock_time',
        })

        clean_players = clean_frames.apply(base.players_loader, axis=1)
        clean_players = [x for x in clean_players if x is not None]
        clean_players = list(itertools.chain.from_iterable(clean_players))
        clean_players = pd.DataFrame(clean_players)
        clean_players = clean_players.rename(columns={'jerseyNum': 'shirt_number'})
        clean_players['shirt_number'] = clean_players['shirt_number'].astype(int)
        clean_frames = clean_frames.drop(['homePlayers', 'homePlayersSmoothed', 'awayPlayers', 'awayPlayersSmoothed'], axis=1)

        mask = ~clean_frames['ballsSmoothed'].isna()
        ball = clean_frames.loc[mask, 'ballsSmoothed'].values.tolist()
        ball = pd.DataFrame(ball)
        ball.columns = ['ball_' + c for c in list(ball.columns)]
        for c in list(ball.columns):
            clean_frames[c] = None
            clean_frames.loc[mask, c] = ball[c].values
            if len(c) <= 6:
                clean_frames[c] = clean_frames[c].astype(float)
        clean_frames = clean_frames.drop(['balls', 'ballsSmoothed'], axis=1)

        mask = ~clean_frames['game_event'].isna()
        game_events = clean_frames.loc[mask, 'game_event'].values.tolist()
        game_events = pd.DataFrame(game_events)
        game_events[['frame_num', 'game_event_id']] = clean_frames.loc[mask, ['frame_num', 'game_event_id']].values

        mask = ~clean_frames['possession_event'].isna()
        possession_events = clean_frames.loc[mask, 'possession_event'].values.tolist()
        possession_events = pd.DataFrame(possession_events)
        possession_events[['frame_num', 'possession_event_id']] = clean_frames.loc[mask, ['frame_num', 'possession_event_id']].values
        clean_frames = clean_frames.drop(['game_event_id', 'game_event', 'possession_event_id', 'possession_event'], axis=1)

        player_ids = game_events.groupby(by='player_id', as_index=False)[['shirt_number', 'team_id', 'home_team']].first()
        player_ids['team'] = 'home'
        player_ids.loc[~player_ids['home_team'], 'team'] = 'away'
        player_ids = player_ids.drop('home_team', axis=1)
        player_ids['shirt_number'] = player_ids['shirt_number'].astype(int)
        clean_players = player_ids.merge(right=clean_players, on=['shirt_number', 'team'], how='right')

        self.save({'frames': clean_frames, 'players': clean_players, 'game_events': game_events, 'possession_events': possession_events})
