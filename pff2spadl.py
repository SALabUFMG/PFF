#imports

from pypff import pff
import pandas as pd
import numpy as np
from socceraction.spadl.config import bodyparts as bodyparts_spadl
from socceraction.spadl.config import results as results_spadl
from socceraction.spadl.config import actiontypes as actiontypes_spadl

url = 'https://faraday.pff.com/api'
key = #INSERT KEY



#data load

comps = pff.get_competitions(url, key)
comp = pff.get_competition(url, key, 1)
teams = pff.get_teams(url, key)
team = pff.get_team(url, key, 1)
games = pff.get_games(url, key, 1)
game = pff.get_game(url, key, 4490)
players_competition = pff.get_players_competition(url, key, 1)
player = pff.get_player(url, key, 2005)
roster = pff.get_roster(url, key, 4770)
game_events = pff.get_game_events(url, key, 4770)


#data prep

pff_events = pff.get_game_events(url, key, 4490)

pff_events = pff_events.rename(columns={
    "id": "event_id",
    "gameId": "game_id",
})

# Function to extract player name and id
def extract_player_info(row):
  if row["player"] is None:
    return pd.Series([None, None])
  return pd.Series([row["player"]["nickname"], row["player"]["id"]])

# Apply function to each row and create new columns
pff_events[["player_name", "player_id"]] = pff_events.apply(extract_player_info, axis=1)

def bodypart2spadl(row):
  bodyparts_pff = {
      "TWOHANDS": {"name": "other","id": bodyparts_spadl.index("other")},
      "BA": {"name": "other","id": bodyparts_spadl.index("other")}, # back
      "BO": {"name": "other","id": bodyparts_spadl.index("other")}, # bottom
      "CA": {"name": "other","id": bodyparts_spadl.index("other")}, # two hand catch
      "CH": {"name": "other","id": bodyparts_spadl.index("other")}, # chest
      "HE": {"name": "head","id": bodyparts_spadl.index("head")},
      "L": {"name": "foot_left","id": bodyparts_spadl.index("foot_left")},
      "LA": {"name": "other","id": bodyparts_spadl.index("other")},  # left arm
      "LB": {"name": "foot_left","id": bodyparts_spadl.index("foot_left")}, # left back heel
      "LC": {"name": "other","id": bodyparts_spadl.index("other")}, # left shoulder
      "LH": {"name": "other","id": bodyparts_spadl.index("other")}, # left hand
      "LK": {"name": "other","id": bodyparts_spadl.index("other")}, # Left knee
      "LS": {"name": "other","id": bodyparts_spadl.index("other")}, # left shin
      "LT": {"name": "other","id": bodyparts_spadl.index("other")}, # left thigh
      "PA": {"name": "other","id": bodyparts_spadl.index("other")}, # Two Hand Palm
      "PU": {"name": "other","id": bodyparts_spadl.index("other")}, # Two Hand Punch
      "R": {"name": "foot_right","id": bodyparts_spadl.index("foot_right")},
      "RA": {"name": "other","id": bodyparts_spadl.index("other")},  # right arm
      "RB": {"name": "foot_right","id": bodyparts_spadl.index("foot_right")}, # right back heel
      "RC": {"name": "other","id": bodyparts_spadl.index("other")}, # right shoulder
      "RH": {"name": "other","id": bodyparts_spadl.index("other")}, # right hand
      "RK": {"name": "other","id": bodyparts_spadl.index("other")}, # right knee
      "RS": {"name": "other","id": bodyparts_spadl.index("other")}, # right shin
      "RT": {"name": "other","id": bodyparts_spadl.index("other")}, # right thigh
      "VM": {"name": "other","id": bodyparts_spadl.index("other")}, # video missing
  }
  if row["bodyType"] is None:
    return pd.Series([None, None])

  return pd.Series([bodyparts_pff[row["bodyType"]]["name"], bodyparts_pff[row["bodyType"]]["id"]])

pff_events[["bodypart_name", "bodypart_id"]] = pff_events.apply(bodypart2spadl, axis=1)

half_index = pff_events.index[pff_events['gameEventType'] == 'SECONDKICKOFF'].tolist()[0]

pff_events['period_id'] = pff_events.index <= half_index

pff_events.loc[pff_events['period_id'], 'period_id'] = 1
pff_events.loc[pff_events['period_id'] == False,'period_id'] = 2

pff_events["seconds"] = pff_events["gameClock"]


def actionresutl2spadl_noinsert(row):
  # pffPossessionEventType = {
  #   "BC": "dribble", # ball carry
  #   "CH": ['foul','tackle','interception'], # challenge
  #   "CL": 'clearence',  # clearence
  #   "CR": "cross",
  #   "PA": "pass",
  #   "RE": "shot",
  #   "SH": "shot"
  # }

  # pffSetpieceType = {
  #   "C": "corner",
  #   "D": "Drop Ball",
  #   "F": "free kick",
  #   "G": "goal kick",
  #   "K": "Kickoff",
  #   "P": "penalty",
  #   "T": "throw in"
  # }

  finalEvent = {
      "actiontype_name": "non_action",
      "actiontype_id": actiontypes_spadl.index("non_action"),
      "result_name": None,
      "result_id": None
  }

  if row["possessionEvents"] == []:
    return pd.Series([
      finalEvent["actiontype_name"],
      finalEvent["actiontype_id"],
      finalEvent["result_name"],
      finalEvent["result_id"]
  ])

  possessionEvent = row["possessionEvents"][0]
  setpieceType = row["setpieceType"]

  # pass
  if possessionEvent["possessionEventType"] == "PA":
    passEvent = possessionEvent["passingEvent"]
    passOutcome = "success" if passEvent["passOutcomeType"] == "C" else "fail"
    #Filtro de impedimento - Leo:
    if (possessionEvent['fouls'] != [] and possessionEvent['fouls'][0]['potentialOffenseType'] == 'O'):
      passOutcome = 'offside'
    # TODO: checar solução pra impedimentos acima

    # pass action type based on set piece
    passActionType = "pass"
    if setpieceType == "T":
      passActionType == "throw_in"
    elif setpieceType == "K": # kickoff
      passActionType = "pass"
    elif setpieceType == "C": # corner
      passActionType = "corner_short"
    elif setpieceType == "F": # freekick
      passActionType = "freekick_short"
    elif setpieceType == "G": # goalkick
      passActionType = "goalkick"

    finalEvent["actiontype_name"] = passActionType
    finalEvent["actiontype_id"] = actiontypes_spadl.index(passActionType)
    finalEvent["result_name"] = passOutcome
    finalEvent["result_id"] = results_spadl.index(passOutcome)

  # cross
  if possessionEvent["possessionEventType"] == "CR":
    crossEvent = possessionEvent["crossEvent"]
    crossOutcome = "success" if crossEvent["crossOutcomeType"] == "C" else "fail"
    #Filtro de impedimento - Leo:
    if (possessionEvent['fouls'] != [] and possessionEvent['fouls'][0]['potentialOffenseType'] == 'O'):
      crossOutcome = 'offside'
    # TODO: checar solução pra impedimentos acima

    # cross action type based on set piece
    crossActionType = "cross"
    if setpieceType == "C": # corner
      crossActionType = "corner_crossed"
    elif setpieceType == "F": # freekick
      crossActionType = "freekick_crossed"
    elif setpieceType == "G": # goalkick
      crossActionType = "goalkick"


    finalEvent["actiontype_name"] = crossActionType
    finalEvent["actiontype_id"] = actiontypes_spadl.index(crossActionType)
    finalEvent["result_name"] = crossOutcome
    finalEvent["result_id"] = results_spadl.index(crossOutcome)

  # shot
  if possessionEvent["possessionEventType"] == "SH":
    shotEvent = possessionEvent["shootingEvent"]
    shotOutcome = "success" if shotEvent["shotOutcomeType"] == "G" else "fail" # goal or not goal

    # shot action type based on set piece
    shotActionType = "shot"
    if setpieceType == "P": # penalty
      shotActionType = "shot_penalty"
    elif setpieceType == "F": # freekick
      shotActionType = "shot_freekick"


    finalEvent["actiontype_name"] = shotActionType
    finalEvent["actiontype_id"] = actiontypes_spadl.index(shotActionType)
    finalEvent["result_name"] = shotOutcome
    finalEvent["result_id"] = results_spadl.index(shotOutcome)

  # TODO: treat this type
  if possessionEvent["possessionEventType"] == "RE":
    pass

  # ball carry
  if possessionEvent["possessionEventType"] == "BC":
    ballCarryType = "dribble"
    ballCarryOutcome = "success"

    if possessionEvent["ballCarryEvent"]["ballCarryType"] == "C": # dribble
      ballCarryType = "dribble"
      ballCarryOutcome = "success"

    elif possessionEvent["ballCarryEvent"]["ballCarryType"] == "D": # take on
      ballCarryType = "take_on"
      # SUCCESS -> B = keeps ball with contact, F = foul, K = keeps ball,
      # FAIL -> H = mishit, O forced out of play, L = beats man loses ball, M = missed foul, S = successful tackle
      ballCarryOutcome = "success" if row["ballCarryEvent"]["dribbleOutcomeType"] in ["B","F","K"] else "fail"

    elif possessionEvent["ballCarryEvent"]["ballCarryType"] == "T":
      ballCarryType = "bad_touch"
      ballCarryOutcome = "fail"
      # shot action type based on touch
      if possessionEvent["ballCarryEvent"]["touchOutcomeType"] == "W": # own goal https://d1ztjbijp0kuqr.cloudfront.net/#definition-TouchOutcomeType
        ballCarryType = "shot"
        ballCarryOutcome = "owngoal"


    finalEvent["actiontype_name"] = ballCarryType
    finalEvent["actiontype_id"] = actiontypes_spadl.index(ballCarryType)
    finalEvent["result_name"] = ballCarryOutcome
    finalEvent["result_id"] = results_spadl.index(ballCarryOutcome)

  # challenge
  if possessionEvent["possessionEventType"] == "CH":
    challengeEvent = possessionEvent["challengeEvent"]

    if challengeEvent["challengeOutcomeType"] == "F":
      finalEvent["actiontype_name"] = "foul"
      finalEvent["actiontype_id"] = actiontypes_spadl.index("foul")

      #https://d1ztjbijp0kuqr.cloudfront.net/#definition-FoulOutcomeType
      foul = possessionEvent["fouls"][0]
      foulOutcome = "fail"
      if foul["foulOutcomeType"] == "Y":
        foulOutcome = "yellow_card"
      if foul["foulOutcomeType"] == "S" or foul["foulOutcomeType"] == "R":
        foulOutcome = "red_card"

      finalEvent["result_name"] = foulOutcome
      finalEvent["result_id"] = results_spadl.index(foulOutcome)


    if challengeEvent["tackleAttemptType"] == "G": # on ball tackle
      finalEvent["actiontype_name"] = "tackle"
      finalEvent["actiontype_id"] = actiontypes_spadl.index("tackle")
      finalEvent["result_name"] = "success"
      finalEvent["result_id"] = results_spadl.index("success")
    else: # tackle error
      finalEvent["actiontype_name"] = "tackle"
      finalEvent["actiontype_id"] = actiontypes_spadl.index("tackle")
      finalEvent["result_name"] = "fail"
      finalEvent["result_id"] = results_spadl.index("fail")


    # TODO other chllenge types

  # clearence
  if possessionEvent["possessionEventType"] == "CL":
    finalEvent["actiontype_name"] = "clearance"
    finalEvent["actiontype_id"] = actiontypes_spadl.index("clearance")
    finalEvent["result_name"] = "success"
    finalEvent["result_id"] = results_spadl.index("success")

  return pd.Series([
      finalEvent["actiontype_name"],
      finalEvent["actiontype_id"],
      finalEvent["result_name"],
      finalEvent["result_id"]
  ])


pff_events[["actiontype_name","actiontype_id","result_name","result_id"]] = pff_events.apply(actionresutl2spadl_noinsert, axis=1)































#XY coordinates:

first_half = pd.read_json("4490_1.jsonl", lines=True)
second_half = pd.read_json("4490_2.jsonl", lines=True)
tracking = pd.concat([first_half,second_half],axis=0)
del first_half
del second_half

tracking = tracking[pd.notna(tracking.game_event_id)]

def extract_ball_coordinates(row):
    ball_dict = {}
    if len(row['balls']) > 0:
      ball = row['balls'][0]
      ball_dict['start_x'] = ball['x']
      ball_dict['start_y'] = ball['y']
    else:
      ball_dict['start_x'] = None
      ball_dict['start_y'] = None
    return ball_dict

tracking['ball_coordinates'] = tracking.apply(extract_ball_coordinates, axis=1)
tracking['start_x'] = tracking['ball_coordinates'].apply(lambda x: x['start_x'])
tracking['start_y'] = tracking['ball_coordinates'].apply(lambda x: x['start_y'])
tracking=tracking[["game_event_id","possession_event_id","start_x","start_y"]]
tracking[["start_x","start_y"]] = np.asarray(tracking[["start_x","start_y"]]) + np.array([105/2,68/2])
tracking[["end_x","end_y"]] = np.asarray(tracking[["start_x","start_y"]]) + np.array([105/2,68/2])
# Agrupando pelo event_id e pegando o último valor de ball_x e ball_y
final_values = tracking.groupby('game_event_id').last().rename(columns={'start_x': 'end_x', 'start_y': 'end_y'})

# Fazendo merge com o dataframe original
tracking = tracking.merge(final_values, on='game_event_id')




tracking = tracking.drop_duplicates(subset='game_event_id', keep='first')
tracking.game_event_id = tracking.game_event_id.astype(int)
pff_events.event_id =  pff_events.event_id.astype(int)
pff_events = pff_events.merge(
    tracking[["game_event_id","start_x","start_y","end_x","end_y"]],
    how="left",
    left_on="event_id",
    right_on="game_event_id"
)














def actionresutl2spadl_insert(df):
  for i, row in df.iterrows():

    finalEvent = {
      "actiontype_name": "non_action",
      "actiontype_id": actiontypes_spadl.index("non_action"),
      "result_name": None,
      "result_id": None
    }

    # TODO: interception
    if row["possessionEvents"] != []:

      possessionEvent = row["possessionEvents"][0]

      # pass
      if possessionEvent["possessionEventType"] == "PA":

        passEvent = possessionEvent["passingEvent"]

        if passEvent["deflectorPlayer"] is not None:

          player_id = passEvent["deflectorPlayer"]["id"]
          player_name = passEvent["deflectorPlayer"]["nickname"]

          interceptionOutcome = "success" if passEvent["passOutcomeType"] != "C" else "fail"

          row["player_name"] = player_name
          row["player_id"] = player_id
          row["actiontype_name"] = "interception"
          row["actiontype_id"] = actiontypes_spadl.index("interception")
          row["result_name"] = interceptionOutcome
          row["result_id"] = results_spadl.index(interceptionOutcome)
          df = pd.concat([df.loc[:i], row, df.loc[i + 1:]]).reset_index(drop=True)
          i += 1

      # cross
      elif possessionEvent["possessionEventType"] == "CR":

        crossEvent = possessionEvent["crossEvent"]

        if crossEvent["deflectorPlayer"] is not None:

          player_id = crossEvent["deflectorPlayer"]["id"]
          player_name = crossEvent["deflectorPlayer"]["nickname"]

          interceptionOutcome = "success" if crossEvent["crossOutcomeType"] != "C" else "fail"

          row["player_name"] = player_name
          row["player_id"] = player_id
          row["actiontype_name"] = "interception"
          row["actiontype_id"] = actiontypes_spadl.index("interception")
          row["result_name"] = interceptionOutcome
          row["result_id"] = results_spadl.index(interceptionOutcome)
          df = pd.concat([df.loc[:i], row, df.loc[i + 1:]]).reset_index(drop=True)
          i += 1


    # TODO: goalkeeper


    # new_row = pd.DataFrame([[value1, value2, ...]], columns=df.columns)  # Create a new row
    # df = pd.concat([df.loc[:index], new_row, df.loc[index + 1:]]).reset_index(drop=True)
    # index += 1  # Increment the index to skip the newly inserted row

  return df


pff_events = actionresutl2spadl_insert(pff_events)



