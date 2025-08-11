import numpy as np
import re
import sys
import json
from sentence_transformers import SentenceTransformer
import faiss
sys.path.append('utils')
from Interpretation import Exp_helper,Guidance_helper, Guidance_helper_woreplan
from environment import EnvironmentState, EnvironmentGraph

import logging
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Robust path setup using absolute paths for simulator and CDL scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR_DIR = os.path.normpath(os.path.join(BASE_DIR, 'simulator'))
# Use dataset scripts under VirtualHome-HG
CDL_SCRIPTS_DIR = os.path.normpath(os.path.join(BASE_DIR, '../VirtualHome-HG/scripts'))
for p in (SIMULATOR_DIR, CDL_SCRIPTS_DIR):
    if p not in sys.path:
        sys.path.append(p)

class Human:
    def __init__(self, scene_graph,guidance):
        self.scene_graph = scene_graph
        self.name2id = {}
        self.guidance=guidance
        ############################
        # self.RAG_model=SentenceTransformer('all-MiniLM-L6-v2')
        # self.init_RAG()
        ############################

    # def init_RAG(self):
    #     self.knowledge_embedding = self.RAG_model.encode(list(self.knowledge.keys()),clean_up_tokenization_spaces=False)
    #     dimension = self.knowledge_embedding .shape[1]
    #     self.index = faiss.IndexFlatL2(dimension)
    #     self.index.add(np.array(self.knowledge_embedding))
    #     self.knowledge_keys = list(self.knowledge.keys())
    #     self.knowledge_values = list(self.knowledge.values())

    # def RAG_query(self,question):
    #     question_embedding = self.RAG_model.encode(question,clean_up_tokenization_spaces=False)
    #     D, I = self.index.search(np.reshape(question_embedding,(1,-1)), 5)
    #     relavant_knowledge = {self.knowledge_keys[idx]: self.knowledge_values[idx] for idx in I[0]}
    #     return relavant_knowledge

    def set_name2id(self,name2id):
        self.name2id = name2id

    def QA(self,question,task_info=None):
        """
        Args:
            input: question (str)
            Returns: LLM_answer (str)
        """
        if 'help me to find' in question: # exploration problem
            target=re.search(r'find (.*?) \?', question).group(1)
            target_id=self.name2id[target]
            target_related_info=self.check_related_edges(target_id)
            discription=''
            for relation in target_related_info:
                from_name=relation['from_name']
                to_name=relation['to_name']
                r=relation['relation_type']
                if r=='CLOSE':
                    discription+=f'- {from_name} is close to {to_name}'
                elif r=='FACING':
                    discription+=f'- {from_name} is facing {to_name}'
                elif r=='INSIDE':
                    discription+=f'- {from_name} is inside {to_name}'
                elif r=='ON':
                    discription+=f'- {from_name} is on {to_name}'
                elif r=='BETWEEN':
                    discription+=f'- {from_name} is between {to_name}'
                discription+='\n'
            answer=Exp_helper(target,discription)
            print(answer)
            return answer, None
        
        if 'how to' in question: # ask for guidance
            # guidance=Guidance_helper(question,self.knowledge)
            # RAG_query_result=self.RAG_query(question)
            # guidance=Guidance_helper(question,RAG_query_result)
            guidance,re_decompose=Guidance_helper(question,self.guidance,task_info)
            return guidance,re_decompose
        
    def QA_woreplan(self,question,task_info=None):
        """
        Args:
            input: question (str)
            Returns: LLM_answer (str)
        """
        if 'help me to find' in question: # exploration problem
            target=re.search(r'find (.*?) \?', question).group(1)
            target_id=self.name2id[target]
            target_related_info=self.check_related_edges(target_id)
            discription=''
            for relation in target_related_info:
                from_name=relation['from_name']
                to_name=relation['to_name']
                r=relation['relation_type']
                if r=='CLOSE':
                    discription+=f'- {from_name} is close to {to_name}'
                elif r=='FACING':
                    discription+=f'- {from_name} is facing {to_name}'
                elif r=='INSIDE':
                    discription+=f'- {from_name} is inside {to_name}'
                elif r=='ON':
                    discription+=f'- {from_name} is on {to_name}'
                elif r=='BETWEEN':
                    discription+=f'- {from_name} is between {to_name}'
                discription+='\n'
            answer=Exp_helper(target,discription)
            print(answer)
            return answer, None
        
        if 'how to' in question: # ask for guidance
            # guidance=Guidance_helper(question,self.knowledge)
            # RAG_query_result=self.RAG_query(question)
            # guidance=Guidance_helper(question,RAG_query_result)
            guidance=Guidance_helper_woreplan(question,self.guidance,task_info)
            return guidance
    
    def check_related_edges(self,node_id):
        related_edges=[]
        for edges in self.scene_graph.get_edges():
            if node_id==edges['from_id'] or node_id==edges['to_id']:
                from_id=edges['from_id']
                to_id=edges['to_id']
                from_name=f"{self.scene_graph.get_node(from_id).class_name}_{from_id}"
                to_name=f"{self.scene_graph.get_node(to_id).class_name}_{to_id}"
                idy_edge={'from_name':from_name,'to_name':to_name,'relation_type':edges['relation_type']}
                related_edges.append(idy_edge)
        # print(related_edges)
        return related_edges

    def human_evaluation(self,goal):
        pass

def load_task():
    scene_path='cdl_dataset/assert/Scene.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)
    return init_scene_graph

if __name__=='__main__':
    scene_graph=load_task()
    human=Human(scene_graph)