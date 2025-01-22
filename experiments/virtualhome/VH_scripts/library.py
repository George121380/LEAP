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
import time
import random
sys.path.append('prompt')
import os
from sentence_transformers import SentenceTransformer, util


class behavior_library_simple:
    def __init__(self, config, epoch_path):
        self.config = config
        self.record_method = config.record_method # 'behavior' or 'actions'
        self.extract_method = config.extract_method # 'whole' or 'rag'
        # self.source_path='log/main_with_guidance/library_data.json'
        self.source_path=os.path.join(epoch_path,'library_data.json')
        self.visualize_path = os.path.join(epoch_path, 'visual.txt')
        if not os.path.exists(self.source_path):
            os.makedirs(os.path.dirname(self.source_path), exist_ok=True)
            with open(self.source_path, "w") as f:
                json.dump([], f)
        self.metadata = json.load(open(self.source_path, "r"))
        if self.extract_method == 'rag':
            self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            self.vec_metadata = []
            start_time = time.time()
            for record in self.metadata:
                self.vec_metadata.append(self.model.encode(record['source_sub_task'], convert_to_tensor=True))
            end_time = time.time()
            print(f"Time cost for encoding: {end_time-start_time}")

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
        config:
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
        count = 0
        k = 50
        if self.record_method == 'behavior':
            if self.extract_method == 'whole' or len(self.metadata) < k:
                if len(self.metadata) == 0:
                    return ""
                embeded_behaviors = '## Previous cases\n'
                embeded_behaviors += f"Here are some success cases for your reference and learning."
                for record in self.metadata:
                    count += 1
                    embeded_behaviors += f"\n# Case {count}:\n"
                    embeded_behaviors += f"When the sub-task is: {record['source_sub_task']}\n"
                    embeded_behaviors += f"A successful representation:\n"
                    embeded_behaviors += f"{record['cdl']}"
                return embeded_behaviors
            
            elif self.extract_method == 'rag':
                
                if len(self.metadata) == 0:
                    return ""
                embeded_behaviors = '## Previous cases\n'
                embeded_behaviors += f"Here are some success cases for your reference and learning."
                for record in self.get_similarity_score(sub_task_description, k):
                    count += 1
                    embeded_behaviors += f"\n# Case {count}:\n"
                    embeded_behaviors += f"When the sub-task is: {record['source_sub_task']}\n"
                    embeded_behaviors += f"A successful representation:\n"
                    embeded_behaviors += f"{record['cdl']}"
                return embeded_behaviors

        elif self.record_method == 'actions':
            if self.extract_method == 'whole':
                if len(self.metadata) == 0:
                    return ""
                embeded_behaviors = '## Previous cases\n'
                embeded_behaviors += f"Here are some success cases for your reference and learning."
                for record in self.metadata:
                    count += 1
                    embeded_behaviors += f"\n# Case {count}:\n"
                    embeded_behaviors += f"When the sub-task is: {record['source_sub_task']}\n"
                    embeded_behaviors += f"Successful actions:\n"
                    embeded_behaviors += f"{record['actions']}"
                return embeded_behaviors
            elif self.extract_method == 'rag':
                self.get_similarity_score(sub_task_description)


    def get_similarity_score(self, sentence, k=50):
       
        embedding = self.model.encode(sentence, convert_to_tensor=True)
        similarity_scores = []

        for index, vec in enumerate(self.vec_metadata):
            similarity = util.cos_sim(embedding, vec).item()
            similarity_scores.append((index, similarity))

        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        top_k_history = [self.metadata[item[0]] for item in similarity_scores[:k]]
        random.shuffle(top_k_history)

        return top_k_history