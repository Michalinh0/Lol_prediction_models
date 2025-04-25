import os
import shutil

def move_files(source_dir, target_dir, num_files):
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Get a list of all files in the source directory
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    print(len(files))
    files_to_move = files[:num_files]

    for file_name in files_to_move:
        src_path = os.path.join(source_dir, file_name)
        dst_path = os.path.join(target_dir, file_name)
        shutil.move(src_path, dst_path)

    print(f"Moved {len(files_to_move)} files from '{source_dir}' to '{target_dir}'.")

# Example usage
source_directory = "match_data"
target_directory = "test_dataset"
number_of_files = 5000 # Specify the exact number of files to move

move_files(source_directory, target_directory, number_of_files)