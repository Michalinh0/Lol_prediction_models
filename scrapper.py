from riotwatcher import LolWatcher, RiotWatcher
from collections import deque
from dotenv import load_dotenv
from requests.exceptions import HTTPError
import json
import time
import os
import signal
import sys

load_dotenv()

api_key = os.getenv('RIOT_API_KEY')

lolWatcher = LolWatcher(api_key)
riotWatcher = RiotWatcher(api_key)

ranked_queue = 420
region = 'eun1'
match_region = 'europe'
me = os.getenv('MY_PUUID')

summoner_queue = deque()
processed_players = set()
processed_matches = set()

match_counter = 0

state_file = 'queue_state.json'

def save_state():
    state = {
        'summoner_queue': list(summoner_queue),
        'processed_players': list(processed_players),
        'processed_matches': list(processed_matches),
        'match_counter': match_counter
    }
    with open(state_file, 'w', encoding='utf-8') as file:
        json.dump(state, file, indent=4)

def load_state():
    global summoner_queue, processed_players, processed_matches, match_counter
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as file:
            state = json.load(file)
            summoner_queue = deque(state['summoner_queue'])
            processed_players = set(state['processed_players'])
            processed_matches = set(state['processed_matches'])
            match_counter = state['match_counter']
        print("Resuming work...")
    else:
        print("No saved state found, starting fresh. Loading players...")
        summoner_queue.append(me)
        get_players(7,"IRON")
        get_players(7,"BRONZE")
        get_players(7,"SILVER")
        get_players(7,"GOLD")
        get_players(7,"PLATINUM")
        get_players(7,"EMERALD")
        get_players(7,"DIAMOND")

def handle_interrupt(signal, frame):
    print("Interrupt received. Saving state...")
    print(f"\nProcessed {match_counter} matches.")
    print(f"Remaining Players in Queue: {len(summoner_queue)}")
    save_state()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

def get_players(count, tier):
    players = lolWatcher.league.entries(region=region, queue='RANKED_SOLO_5x5', tier=tier, division='I')
    counter = 0
    for player in players:
        if(counter >= count):
            break
        summoner_queue.append(player["puuid"])
        counter+=1

def get_matches(player):
    try:
        match_ids = lolWatcher.match.matchlist_by_puuid(match_region,player,20)
    except HTTPError:
        print(f"Error processing matchlist of {player}")
        return
    return match_ids

def process_match(match):
    global match_counter
    if match in processed_matches:
        return
    try:
        match_data = lolWatcher.match.by_id(match_region, match)
    except HTTPError:
        print(f"Error processing match {match}")
        return
    queue_id = match_data["info"]["queueId"]
    game_v = match_data["info"]["gameVersion"]
    game_duration = match_data["info"]["gameDuration"]

    if queue_id != 420 or  not game_v.startswith("15.") or game_duration < 1200:
        return
    
    filePath = f"match_data/{match}.json"
    with open(filePath, "w", encoding="utf-8") as file:
        json.dump(match_data, file, indent=4)
    
    for player in match_data["info"]["participants"]:
        puuid = player["puuid"]
        if puuid not in processed_players and puuid not in summoner_queue and len(summoner_queue) <= 1000:
            summoner_queue.append(puuid)
    
    processed_matches.add(match)
    match_counter += 1

startTime = time.time()
last_print_time = time.time()
duration = 8 * 60 * 60

load_state()

try:
    while ( time.time() - startTime < duration and match_counter < 65000):
        if not(summoner_queue):
            print("Queue empty, refilling")
            get_players(5,"IRON")
            get_players(5,"BRONZE")
            get_players(5,"SILVER")
            get_players(5,"GOLD")
            get_players(5,"PLATINUM")
            get_players(5,"EMERALD")
            get_players(5,"DIAMOND")
        puuid = summoner_queue.popleft()
        #print(f"Next player, {len(summoner_queue)} left in queue")
        processed_players.add(puuid)
        matches = get_matches(puuid)
        if(matches):
            for match in matches:
                process_match(match)
                if match_counter % 100 == 0 and match_counter > 0:
                    print(f"Processed {match_counter} matches")
        
        if time.time() - last_print_time >= 15 * 60:
            elapsed_time = time.time() - startTime
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            print(f"{hours} hours {minutes} minutes passed")
            print(f"Processed {match_counter} matches.")
            print(f"Remaining Players in Queue: {len(summoner_queue)}")
            last_print_time = time.time()

    print(f"Processed {match_counter} matches.")
    print(f"Remaining Players in Queue: {len(summoner_queue)}")
    save_state()
except KeyboardInterrupt:
    print(f"\nProcessed {match_counter} matches.")
    print(f"Remaining Players in Queue: {len(summoner_queue)}")
    save_state()