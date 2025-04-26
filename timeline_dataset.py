from riotwatcher import LolWatcher, RiotWatcher
from dotenv import load_dotenv
from requests.exceptions import HTTPError, RequestException
import json
import os
import time
from tqdm import tqdm

load_dotenv()

api_key = os.getenv('RIOT_API_KEY')

lolWatcher = LolWatcher(api_key)
riotWatcher = RiotWatcher(api_key)

dataset = 'test_dataset'
output_directory = 'test_timelines'

base_path = os.path.dirname(os.path.abspath(__file__))
path_to_dataset = os.path.join(base_path, dataset)
path_to_output = os.path.join(base_path, output_directory)

processed_matches = set()

for file in os.listdir(path_to_output):
    if file.endswith("_timeline.json"):
        match_id = file.replace("_timeline.json", "")
        processed_matches.add(match_id)

match_files = [
    f for f in os.listdir(path_to_dataset)
    if f.endswith(".json") and f.replace('.json', '') not in processed_matches
]

print(match_files, len(match_files))
print(processed_matches, len(processed_matches))

MAX_RETRIES = 5
BACKOFF_BASE = 1


for filename in tqdm(match_files, desc="Processing timelines"):
    match_id = filename.replace(".json", "")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            timeline = lolWatcher.match.timeline_by_match('eun1', match_id)
            first_15_minutes = timeline['info']['frames'][:16]
            out_file_path = os.path.join(path_to_output, f"{match_id}_timeline.json")
            with open(out_file_path, 'w', encoding='utf-8') as f:
                json.dump(first_15_minutes, f, indent=2)
            break
        except HTTPError as e:
            status_code = e.response.status_code if e.response else None
            if status_code in [502,503,504]:
                if attempt == MAX_RETRIES:
                    print(f"Failed to fetch match {match_id} after {MAX_RETRIES} attempts.")
                    break
                else:
                    wait_time = BACKOFF_BASE ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        except RequestException as e:
            wait_time = BACKOFF_BASE ** attempt
            print(f"\n{match_id}: Network error – retrying in {wait_time}s (attempt {attempt})")
            time.sleep(wait_time)
        except Exception as e:
            print(f"\n{match_id}: Unexpected error: {e}")
            break
    else:
        print(f"\n{match_id}: Failed after {MAX_RETRIES} retries, skipping.")