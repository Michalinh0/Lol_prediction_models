import os
import json
import pandas as pd
import time

timeline_directory = 'large_timelines'
dataset_directory = 'large_dataset'

base_path = os.path.dirname(os.path.abspath(__file__))
path_to_timeline = os.path.join(base_path, timeline_directory)
path_to_dataset = os.path.join(base_path, dataset_directory)

data = []

def extract_kda(match_data, participant_index):
    kda = [0,0,0]
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'CHAMPION_KILL':
                if event['killerId'] == participant_index:
                    kda[0] += 1
                elif event['victimId'] == participant_index:
                    kda[1] += 1
                if 'assistingParticipantIds' in event and participant_index in event['assistingParticipantIds']:
                    kda[2] += 1
    return kda

def extract_wards(match_data, participant_index):
    wards = 0
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'WARD_PLACED' and event['creatorId'] == participant_index:
                wards += 1
    return wards

def extract_turrets(match_data, team_index):
    if team_index == 1:
        event_team = 200
    else:
        event_team = 100
    turrets = 0
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER_BUILDING':
                if event['teamId'] == event_team:
                    turrets += 1
    return turrets

def extract_turret_plates(match_data, team_index):
    if team_index == 1:
        event_team = 200
    else:
        event_team = 100
    turret_plates = 0
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'TURRET_PLATE_DESTROYED':
                if event['teamId'] == event_team:
                    turret_plates += 1
    return turret_plates

def extract_dragons(match_data, team_index):
    if team_index == 1:
        event_team = 100
    else:
        event_team = 200
    dragons = 0
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'ELITE_MONSTER_KILL' and event['monsterType'] == 'DRAGON':
                if event['killerTeamId'] == event_team:
                    dragons += 1
    return dragons

def extract_grubs(match_data, team_index):
    if team_index == 1:
        event_team = 100
    else:
        event_team = 200
    grubs = 0
    for frame in match_data:
        for event in frame['events']:
            if event['type'] == 'ELITE_MONSTER_KILL' and event['monsterType'] == 'HORDE':
                if event['killerTeamId'] == event_team:
                    grubs += 1
    return grubs


start = time.time()

for i, filename in enumerate(os.listdir(path_to_dataset)):
    if i % 100 == 0:
        print(f"{i} files processed... {time.time() - start} seconds elapsed")

    with open(os.path.join(path_to_dataset, filename), 'r') as file:
        match_result = json.load(file)
    file.close()

    match_path = os.path.join(path_to_dataset, filename)
    timeline_filename = filename.replace(".json", "_timeline.json")
    timeline_path = os.path.join(path_to_timeline, timeline_filename)

    with open(os.path.join(path_to_timeline, timeline_filename), 'r') as file:
        timeline = json.load(file)
    file.close()

    #FEATURE EXTRACTION
    match_data = {}
    match_data["game_duration"] = match_result["info"]["gameDuration"]

    for i in range(1,11):
        kda = extract_kda(timeline, i)
        wards = extract_wards(timeline, i)
        match_data[f"player{i}_champion"] = match_result["info"]["participants"][i-1]["championName"]
        match_data[f"player{i}_kills"] = kda[0]
        match_data[f"player{i}_deaths"] = kda[1]
        match_data[f"player{i}_assists"] = kda[2]
        match_data[f"player{i}_gold"] = timeline[-1]["participantFrames"][str(i)]["totalGold"]
        match_data[f"player{i}_experience"] = timeline[-1]["participantFrames"][str(i)]["xp"]
        match_data[f"player{i}_damage_dealt"] = timeline[-1]["participantFrames"][str(i)]['damageStats']["totalDamageDoneToChampions"]
        match_data[f"player{i}_damage_taken"] = timeline[-1]["participantFrames"][str(i)]['damageStats']["totalDamageTaken"]
        match_data[f"player{i}_creep_score"] = timeline[-1]["participantFrames"][str(i)]["minionsKilled"] + timeline[-1]["participantFrames"][str(i)]["jungleMinionsKilled"]
        match_data[f"player{i}_wards"] = wards
    for i in range(1,3):
        match_data[f"team{i}_turret_plates"] = extract_turret_plates(timeline, i)
        match_data[f"team{i}_turrets"] = extract_turrets(timeline, i)
        match_data[f"team{i}_dragons"] = extract_dragons(timeline, i)
        match_data[f"team{i}_grubs"] = extract_grubs(timeline, i)
    match_data["Winning team"] = int(match_result["info"]["teams"][0]["win"])
    data.append(match_data)
    
df = pd.DataFrame(data)

df.to_csv("ranked_matches_at_15_large.csv", index=False)


