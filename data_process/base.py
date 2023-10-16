from tqdm import tqdm
import pandas as pd

def players_loader(row):
    players = []
    for team in ['home', 'away']:
        team_players = row[team + 'PlayersSmoothed']
        if team_players is None:
            return None
        else:
            for p in team_players:
                p['frame_num'] = row['frame_num']
                p['team'] = team
            players += team_players
    return players