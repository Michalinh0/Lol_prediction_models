import os
import re

dataset = 'large_dataset'
timeline = 'large_timelines'

base_path = os.path.dirname(os.path.abspath(__file__))
dir_a = os.path.join(base_path, dataset)
dir_b = os.path.join(base_path, timeline)

# Helper function to extract numbers from filenames
def extract_numbers(file_list, pattern):
    numbers = set()
    for f in file_list:
        match = re.match(pattern, f)
        if match:
            numbers.add(match.group(1))
    return numbers

# Get list of filenames
files_a = os.listdir(dir_a)
files_b = os.listdir(dir_b)

# Extract numbers
pattern_a = r'EUN1_(\d+)$'
pattern_b = r'EUN1_(\d+)_timeline$'

nums_a = extract_numbers(files_a, pattern_a)
nums_b = extract_numbers(files_b, pattern_b)

# Compare
only_in_a = nums_a - nums_b
only_in_b = nums_b - nums_a

# Report
if only_in_a:
    print("Missing in timeline directory:")
    for num in sorted(only_in_a):
        print(f"EUN1_{num}_timeline")

if only_in_b:
    print("\nMissing in base directory:")
    for num in sorted(only_in_b):
        print(f"EUN1_{num}")

if not only_in_a and not only_in_b:
    print("All files are properly matched.")