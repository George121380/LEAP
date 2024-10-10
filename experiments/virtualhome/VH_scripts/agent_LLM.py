import sys
sys.path.append('prompt')
from ask_GPT import ask_GPT


class LLM_Agent:
    def __init__(self, llm_model):
        self.scene_info=None

    def load_scene(self,scene_graph):
        self.scene_info=scene_graph
        