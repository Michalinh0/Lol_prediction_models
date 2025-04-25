from riotwatcher import LolWatcher, RiotWatcher
from dotenv import load_dotenv
import json
import os

load_dotenv()

api_key = os.getenv('RIOT_API_KEY')

lolWatcher = LolWatcher(api_key)
riotWatcher = RiotWatcher(api_key)

dataset = 'test_dataset'
output_directory = 'test_timelines'

base_path = os.path.dirname(os.path.abspath(__file__))
path_to_dataset = os.path.join(base_path, dataset)
path_to_output = os.path.join(base_path, output_directory)

counter = 0

for filename in os.listdir(path_to_dataset):
    file_path = os.path.join(path_to_dataset, filename)

    if not os.path.isfile(file_path) or not filename.endswith(".json"):
        continue

    match_id = filename.replace(".json", "")

    timeline = lolWatcher.match.timeline_by_match('eun1', match_id)

    first_15_frames = timeline['info']['frames'][:16]

    out_file_path = os.path.join(path_to_output, f"{match_id}_timeline.json")

    with open(out_file_path, 'w', encoding='utf-8') as f:
        json.dump(first_15_frames, f, indent=2)

    counter += 1
    if(counter % 50 == 0):
        print(f"Processed {counter} files")