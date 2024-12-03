"""
This is a simplified version of library

Lift: Directly lift all the behaviors and functions without any operations

Download: Copy directly

	# History K:
	When the sub-task is: abcdefg
	A successful representation:


"""

import json
import sys
import re
sys.path.append('prompt')
import os

class behavior_library_simple:
    def __init__(self, args, epoch_path):
        self.args = args
        self.record_method = args.library.record_method # 'behavior' or 'actions'
        self.extract_method = args.library.extract_method # 'whole' or 'rag'
        # self.source_path='experiments/virtualhome/resources/library_data.json'
        self.source_path=os.path.join(epoch_path,'library_data.json')
        self.visualize_path = os.path.join(epoch_path, 'visual.txt')
        if not os.path.exists(self.source_path):
            os.makedirs(os.path.dirname(self.source_path), exist_ok=True)
            with open(self.source_path, "w") as f:
                json.dump([], f)
        self.metadata = json.load(open(self.source_path, "r"))

    def save_library(self):
        data_to_save = self.metadata
        with open(self.source_path, "w") as file:
            json.dump(data_to_save, file, indent=4)
        if self.record_method == 'behavior':
            with open(self.visualize_path, "w") as f:
                for record in self.metadata:
                    f.write("#"*60+'\n')
                    f.write(f"When the sub-task is: {record['source_sub_task']}\n")
                    f.write(f"A successful representation:\n")
                    f.write(f"{record['cdl']}\n")

        elif self.record_method == 'actions':
            with open(self.visualize_path, "w") as f:
                for record in self.metadata:
                    f.write("#"*60+'\n')
                    f.write(f"When the sub-task is: {record['source_sub_task']}\n")
                    f.write(f"Actions:\n")
                    f.write(f"{record['actions']}\n")

    def lift(self, task_name: str, source_sub_task: str, content: str):
        """
        Args:
            source_sub_task: where the behavior is created
            behavior_cdl: cdl representation for this behavior
        """
        if self.record_method == 'behavior':
            history_info = {
                'task_name': task_name,
                'source_sub_task': source_sub_task,
                'cdl': content,
            }
        elif self.record_method == 'actions':
            history_info = {
                'task_name': task_name,
                'source_sub_task': source_sub_task,
                'actions': content,
            }
        self.metadata.append(history_info)
        self.save_library()

    def download_behaviors(self, sub_task_description: str):
        if self.record_method == 'behavior':
            if self.extract_method == 'whole':
                if len(self.metadata) == 0:
                    return ""
                embeded_behaviors = '# Previous cases\n'
                for record in self.metadata:
                    embeded_behaviors += f"When the sub-task is: {record['source_sub_task']}\n"
                    embeded_behaviors += f"A successful representation:\n"
                    embeded_behaviors += f"{record['cdl']}"
                return embeded_behaviors
            
            elif self.extract_method == 'rag':
                pass

        elif self.record_method == 'actions':
            if self.extract_method == 'whole':
                if len(self.metadata) == 0:
                    return ""
                embeded_behaviors = '# Previous cases\n'
                for record in self.metadata:
                    embeded_behaviors += f"When the sub-task is: {record['source_sub_task']}\n"
                    embeded_behaviors += f"Actions:\n"
                    embeded_behaviors += f"{record['actions']}"
                return embeded_behaviors
            elif self.extract_method == 'rag':
                pass