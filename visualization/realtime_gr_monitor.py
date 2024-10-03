import time
import re
import os

file_path = 'experiments/virtualhome/CDLs/internal_executable.cdl'

def read_goal_representation():
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
