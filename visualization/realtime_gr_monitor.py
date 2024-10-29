import time
import re
import os

# file_path = 'experiments/virtualhome/CDLs/internal_executable.cdl'

def get_latest_epoch_file(folder_path):
    # List all files in the given folder
    files = os.listdir(folder_path)
    
    # Filter out files that start with "epoch"
    epoch_files = [f for f in files if f.startswith("epoch")]
    
    if not epoch_files:
        return None  # No epoch files found
    
    # Define a function to extract the date and time for sorting
    def extract_datetime(file_name):
        parts = file_name.split('_')
        date = parts[1]  # The date part
        time = parts[2]  # The time part
        return date, time
    
    # Sort files by date and then by time
    latest_file = max(epoch_files, key=lambda x: extract_datetime(x))
    
    return latest_file

def read_goal_representation():
    file_path = os.path.join('log',get_latest_epoch_file('log'),'internal_executable.cdl')
    # print(file_path)
    with open(file_path, 'r') as file:
        content = file.read()
    match = re.search(r'#goal_representation(.*?)#goal_representation_end', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

previous_content = read_goal_representation()

print("Monitoring the file for changes...")

try:
    while True:
        current_content = read_goal_representation()
        if current_content != previous_content:
            os.system('clear')
            print(current_content)
            previous_content = current_content
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped monitoring.")
