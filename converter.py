import os
import json
import pandas as pd
import time

data_directory = "large_dataset"

data = []
previous = "0"
counter = 0
start = time.time()
quarters = 0
mistakes = 0

for i,filename in enumerate(os.listdir(data_directory)):
    if(i%100 == 0):
        print(i)
    path = os.path.join(data_directory, filename)
    with open(path,"r") as file:
        match = json.load(file)
        counter+=1

    if(match["info"]["queueId"] != 420 or not match['info']['gameVersion'].startswith("15.")):
        mistakes += 1
        print(f"{match["info"]["queueId"]}, {mistakes}, {counter}")

    match_data = {
         "game_duration": match["info"]["gameDuration"]
    }
    file.close()
    
    for i, participant in enumerate(match["info"]["participants"]):
        player_num = i + 1
        match_data[f"player{player_num}_kills"] = participant["kills"]
        match_data[f"player{player_num}_deaths"] = participant["deaths"]
        match_data[f"player{player_num}_assists"] = participant["assists"]
        
        
        match_data[f"player{player_num}_gold"] = participant["goldEarned"]
        match_data[f"player{player_num}_experience"] = participant["champExperience"]
        match_data[f"player{player_num}_damage_dealt"] = participant["totalDamageDealtToChampions"]
        match_data[f"player{player_num}_damage_taken"] = participant["totalDamageTaken"]
        match_data[f"player{player_num}_vision_score"] = participant["visionScore"]
        match_data[f"player{player_num}_crowd_control_score"] = participant["timeCCingOthers"]
        match_data[f"player{player_num}_cs"] = participant["totalMinionsKilled"] + participant.get("neutralMinionsKilled", 0)
    for i, team in enumerate(match["info"]["teams"]):
         team_id = i + 1
         match_data[f"team{team_id}_atakhan"] = team.get("objectives", {}).get("atakhan", {}).get("kills", 0)
         match_data[f"team{team_id}_barons"] = team["objectives"]["baron"]["kills"]
         match_data[f"team{team_id}_champions"] = team["objectives"]["champion"]["kills"]
         match_data[f"team{team_id}_dragons"] = team["objectives"]["dragon"]["kills"]
         match_data[f"team{team_id}_grubs"] = team["objectives"]["horde"]["kills"]
         match_data[f"team{team_id}_inhibitors"] = team["objectives"]["inhibitor"]["kills"]
         match_data[f"team{team_id}_rift_herald"] = team["objectives"]["riftHerald"]["kills"]
         match_data[f"team{team_id}_turret"] = team["objectives"]["tower"]["kills"]
    match_data["Winning team"] = int(match["info"]["teams"][0]["win"])
    data.append(match_data)
    if counter % 100 == 0 and counter > 0:
        print(f"Processed {counter} matches")
        print(f"{time.time() - start} seconds passed")

print(f"{counter} matches in dataset")

df = pd.DataFrame(data)

df.to_csv("ranked_matches_large.csv", index=False)

print("CSV file has been successfully created!")