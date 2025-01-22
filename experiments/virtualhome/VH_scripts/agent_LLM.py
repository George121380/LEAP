import sys
sys.path.append('prompt')
import json
import random
import numpy as np
import re
from utils_eval import get_nodes_information,construct_cdl
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from agent_base import BaseAgent

from ask_GPT import ask_GPT
from baselines.baseline_LLM import LLM_Agent_Prompt

class Argument:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Action:
    def __init__(self, executor_string):
        self.executor_string = executor_string
        self.name = None
        self.arguments = []
        self.parse_executor_string()

    def parse_executor_string(self):
        pattern = r'(\w+_executor)\(([^)]*)\)'
        match = re.match(pattern, self.executor_string)
        
        if not match:
            raise ValueError(f"Invalid format: {self.executor_string}")
        
        self.name = match.group(1)
        
        arguments = match.group(2).split(',')
        self.arguments = [Argument(arg.strip()) for arg in arguments]

    def __str__(self):
        return self.executor_string

class LLM_Agent(BaseAgent):
    def __init__(self,config,filepath,task_logger,epoch_path,difficulty):

        super().__init__(config, filepath, task_logger, epoch_path, agent_base_type='action')
    
        self.model=SentenceTransformer('paraphrase-MiniLM-L6-v2')  # You can choose other models

        self.scene_info=None
        # Task information
        
        self.self_evaluate_num=0
        self.add_info_nl=''
        self.add_info_human_instruction=''
        self.add_info_trial_and_error_info=''
        self.add_info_action_history=[]
        self.add_info_action_history_for_evaluation=[]
        
        """
        path to the CDL files
        internal_executable_file_path: the file can be solve py planner: state + goal
        basic_domain_knowledge_file_path: domain knowledge
        state_file_path: the file contains the current state: state (only)        
        """
        self.internal_executable_file_path = 'experiments/virtualhome/CDLs/internal_executable.cdl'
        self.basic_domain_knowledge_file_path = 'experiments/virtualhome/CDLs/virtualhome_partial.cdl'
        self.state_file_path = 'experiments/virtualhome/CDLs/current_agent_state.cdl'

        self.plan=[]
        self.current_step=0

        self.exp_fail_num=0
        self.error_times=0
        self._parse_file(filepath)
        self.save_to_file()
        self.relavant_objects=[]
        
        self.relavant_item_info=''
        self.action_counting={}
        self.fail_to_find_dict={}
        self.exp_helper_query_times=0
        self.guidance_query_times=0 

        self.failed_execution_flag=False
        self.query_human_flag=False

        self.difficulty=1.5*difficulty
        self.max_trying_times=3*difficulty

        self.exp_query_record=[] # record all the items that already queried the location
        self.replan_times=0

    def reset_goal(self, goal, taskname):
        self.goal_nl=goal
        self.task_name=taskname
        relavant=self.select_relevant_items()
        self.relavant_objects=relavant

    def updates(self,observation):
        if "You can not" in observation: # if this action is not executable
            # self.add_info_trial_and_error_info+=(observation+'\n')
            error="You get this error: "+observation+'\n'
            self.add_info_action_history.append(error)
            self.failed_execution_flag=True

        else:
            action_effects=''
            if not observation['exp_flag'] and not observation['obs_flag']:# other actions
                action_effects = self.regular_action_obs_update(observation)

            if observation['exp_flag']:# exploration
                exp_target=observation['exp_target']
                exp_loc=observation['exp_loc']
                for new_known in observation['known']:
                        if 'character' in new_known:
                            continue
                        if self.exploration['unknown'][self.name2opid[new_known]]==True:
                            self.exploration['unknown'][self.name2opid[new_known]]=False
                            self.newfind=True # find sth new
                
                for check_place in observation['checked']:
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                if exp_target in observation['known'] or not self.exploration['unknown'][self.name2opid[exp_target]]:
                    print(f'{exp_target} is successfully explored around {exp_loc} or already known before')
                    action_effects+=f"Find {exp_target}. "
                else:
                    if self.exp_fail_num==5:
                        human_answer=self.query_LLM_human(f'Can you help me to find {exp_target} ?')
                        print(f'Query human about the location of {exp_target}.')
                        self.exp_fail_num=0
                        self.add_info_human_instruction+=human_answer+'\n'
                        self.logger.info("From agent_LLM.py->updates"+self.add_info_nl)

                    self.exp_fail_num+=1
                    print(f'{exp_target} is not around {exp_loc}, re-explore')
                    action_effects+=f"Failed to find {exp_target} around {exp_loc}. "
                    self.save_to_file()
                    
            if observation['obs_flag']:
                obs_target=observation['obs_target']
                self.state['visited'][self.name2opid[obs_target]]=True
                for new_known in observation['known']:
                    if 'character' in new_known:
                        continue
                    if self.exploration['unknown'][self.name2opid[new_known]]==True:
                        self.exploration['unknown'][self.name2opid[new_known]]=False
                        # self.newfind=True # find sth new
                
                for check_place in observation['checked']:
                    if 'character' in check_place:
                        continue
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                # obs_information=self.obs_query(observation['obs_target'],observation['obs_result'],observation['question'])+'\n'# Query LLM
                obs_information=self.organize_obs_result(observation['obs_result']) # Use observation information directly
                action_effects+=f"Get this information: {obs_information}"

            # update character state
            if observation['action'].name=='standup_executor':
                self.character_state['standing']=True
                self.character_state['sitting']=False
                self.character_state['lying']=False
                self.character_state['sleeping']=False
            
            if observation['action'].name=='sit_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=True
                self.character_state['lying']=False
                self.character_state['sleeping']=False
            
            if observation['action'].name=='lie_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=False
                self.character_state['lying']=True
                self.character_state['sleeping']=False
            
            if observation['action'].name=='sleep_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=False
                self.character_state['lying']=False
                self.character_state['sleeping']=True

            if observation['action'].name=='grab_executor':
                hold_rl=np.any(self.state['holds_lh']==True)
                hold_rr=np.any(self.state['holds_rh']==True)
                if hold_rl and hold_rr:
                    self.character_state['has_a_free_hand']=False
                self.state['inhand'][self.name2opid[observation['action'].arguments[0].name]]=True
                
            if observation['action'].name=='put_executor' or observation['action'].name=='putin_executor':
                self.character_state['has_a_free_hand']=True
                self.state['inhand'][self.name2opid[observation['action'].arguments[0].name]]=False

            self.annotation(observation)
            self.add_info_action_history.append({'action':str(observation['action']),'effects':action_effects})
            self.add_info_action_history_for_evaluation.append({'action':str(observation['action']),'effects':action_effects})
            self.logger.info("From agent_LLM.py->updates"+str(observation['action']),action_effects)


    def query_LLM_human(self,question:str):
        record='Record from func query_human in agent.py\n'
        record+=f'Question: {question}\n'
        task_info={}
        task_info['Goal']=self.goal_nl
        task_info['Subgoals']=[self.goal_nl]
        answer=self.human_helper.QA(question,task_info)
        record+=f'Answer: {answer}\n'
        self.logger.info("From agent_LLM -> query_LLM_human"+record)
        return answer
    

    def ask_for_human_task_guidance(self):
        self.guidance_query_times+=1
        question=f'Can you teach me how to "{self.goal_nl.lower()}" ?'

        if self.config.human_guidance=='LLM':
            Human_Guidance, re_decompose=self.query_LLM_human(question)

        if self.config.human_guidance=='Manual':
            print("still developing")

        self.add_info_nl+=Human_Guidance

    
    def select_relevant_items(self, k=100):
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # You can choose other models
        task_instruction = self.goal_nl
        task_embedding = model.encode([task_instruction])  # Convert task instruction to vector
        item_list=list(self.name2opid.keys()) # Get all item names
        item_embeddings = model.encode(item_list)          # Convert each item name to vector
        
        similarities = cosine_similarity(task_embedding, item_embeddings)[0]  # 1D array of similarities
        
        # Step 4: Sort items by similarity and select top k
        top_k_indices = np.argsort(similarities)[-k:][::-1]  # Indices of top k most similar items
        top_k_items = [item_list[i] for i in top_k_indices]  # Get the corresponding item names
        self.relavant_objects=top_k_items

    def item_infoto_nl(self):
        self.select_relevant_items()
        description = ""

        for item_name in self.relavant_objects:
            item_id = self.name2opid[item_name]
            description += f"Item name: {item_name}\n"
            
            properties = [prop_name.replace('_', ' ') for prop_name, prop_values in self.properties.items() if prop_values[item_id]==True]
            if properties:
                # description += self.generate_properties_description(properties)
                description += f"  Properties: {'; '.join(properties)}.\n"
            else:
                description += "  Properties: None.\n"
            
            states = [state_name.replace('_', ' ') for state_name, state_values in self.state.items() if state_values[item_id]==True]
            if states:
                description += f"  States: {'; '.join(states)}.\n"
            
            
            relations = []
            for relation_name, relation_matrix in self.relations.items():
                for other_id, has_relation in enumerate(relation_matrix[item_id]):
                    if has_relation==True:
                        other_name = self.opid2name[other_id]
                        relations.append(f"{relation_name.replace('_', ' ')} {other_name}")

            if relations:
                description += f"  Relations: {'; '.join(relations)}.\n"

            if not relations and not states:
                description += "  The item is not find yet. You cannot perform any actions on it.\n"
            
                
            description += "\n"
        with open('visualization/scene_graph_to_nl.txt','w') as f:
            f.write(description)
        self.relavant_item_info=description
        return description

    def check_action(self,action): # check if the action is executable
        
        if action.name=='grab_executor':
            # robot can not grab an item by two hands at the same time
            if self.state['inhand'][self.name2opid[action.arguments[0].name]]==True:
                print(f"Debug: Do grab when the robot is already holding {action.arguments[0].name}")
                return False
        
        for involved_obj in action.arguments:
            obj_name=involved_obj.name

            if not obj_name in self.name2opid:
                print(f"Debug: Use an undefined object: '{obj_name}'")
                return False

            obj_id=self.name2opid[obj_name]
            if self.exploration['unknown'][obj_id]:
                print(f"Debug: Use an unfound object: '{obj_name}'")
                if obj_id in self.fail_to_find_dict:
                    self.fail_to_find_dict[obj_id]+=1
                    if self.fail_to_find_dict[obj_id]>5 and not obj_id in self.exp_query_record:
                        self.exp_query_record.append(obj_id)
                        answer=f'To find {obj_name}, the human give you this guidance:\n'
                        answer+=self.query_LLM_human(f'Can you help me to find {obj_name} ?')[0]
                        self.add_info_nl+=answer+'\n'
                        self.exp_helper_query_times+=1

                else:
                    self.fail_to_find_dict[obj_id]=1
                
                return False
        return True

    def get_character_info(self):
        char_information=''
        lh_hold=np.where(self.state['holds_lh']==True)[0]
        rh_hold=np.where(self.state['holds_rh']==True)[0]
        if len(lh_hold)>0:
            for lh in lh_hold:
                char_information+=f'Robot is holding {self.opid2name[lh]} by left hand. '
        if len(rh_hold)>0:
            for rh in rh_hold:
                char_information+=f'Robot is holding {self.opid2name[rh]} by right hand. '
        if not len(lh_hold)>0 and not len(rh_hold)>0:
            char_information+="Robot's arms are empty, holding nothing"
        return char_information
    
    def get_unknwon_list(self):
        unknown_list=[]
        for obj_id, is_unknown in enumerate(self.exploration['unknown']):
            if is_unknown:
                unknown_list.append(self.opid2name[obj_id])
        random.shuffle(unknown_list)
        return unknown_list

    def preprocess_for_action_list(self,action_list):
        filtered_action_list=action_list.replace('python','')
        filtered_action_list=filtered_action_list.replace('`','')
        filtered_action_list=filtered_action_list.replace('\n','')
        python_action_list=eval(filtered_action_list)
        executable_action_list=[Action(action) for action in python_action_list]
        print("#"*80)
        print("Find a plan:")
        # print all the actions with idx
        for idx, action in enumerate(executable_action_list):
            print(f"{idx}: {action}")
        print("#"*80)
        return executable_action_list

    def act(self):
        
        for action_str, count in self.action_counting.items():
            # if count > 10:
            #     print("Debug: repeat a single action for more than 10 times")
            #     return 'Failed', None
            if len(self.add_info_action_history)>self.max_trying_times:
                print(f"Debug: more than {self.max_trying_times} actions have been executed")
                self.logger.info(f"From agent_LLM.py->act: more than {self.max_trying_times} actions have been executed")
                return 'Failed',None
            
            if len(self.fail_to_find_dict)>0:
                if max(self.fail_to_find_dict.values())>15:
                    print("fail to find an item for more than 15 times")
                    self.logger.info("From agent_LLM.py->act: fail to find an item for more than 15 times")
                    return 'Failed',None
                        
            if len(self.add_info_action_history)==self.difficulty==0 and not self.query_human_flag:
                #ask for human guidance
                self.query_human_flag=True
                self.ask_for_human_task_guidance()
            
        if self.current_step == len(self.plan) and len(self.plan) > 0:
                print("The plan is all executed")
                self.logger.info("From agent_LLM.py->act: The plan is all executed")
                return 'over', None
            
        elif self.plan and self.current_step <= len(self.plan) and self.check_action(self.plan[self.current_step]) and not self.failed_execution_flag:
            
            # regular action
            action = self.plan[self.current_step]
            self.logger.info("From agent_LLM.py->act: "+str(action))
            self.current_step += 1
            return action, None

        else:
            self.failed_execution_flag=False
            human_exp_guidance=''            
            try_times=0
            while True:
                try:
                    try_times+=1
                    if try_times>10:
                        print("Debug: auto debug for more than 10 times")
                        self.logger.info("From agent_LLM.py->act: auto debug for more than 10 times")
                        return 'Failed',None
                    
                    # Get prompt for generate a plan
                    content_prompt=LLM_Agent_Prompt(self.goal_nl,self.add_info_nl,self.relavant_item_info,self.add_info_action_history,self.get_unknwon_list(),self.get_character_info(),human_exp_guidance)
                    system_prompt='I need you to help me output a sequence of actions based on the information I provide.'
                    response=ask_GPT(system_prompt,content_prompt)
                    self.plan=self.preprocess_for_action_list(response)
                    action = self.plan[0]
                    self.current_step = 1

                    # make sure the action is executable
                    assert self.check_action(action)
                    
                    # Count each actions
                    if str(action) in self.action_counting:
                        self.action_counting[str(action)]+=1
                    else:
                        self.action_counting[str(action)]=1

                    return action,None
                
                except:
                    continue


    def final_important_numbers_report(self):
        info={
            'exp_helper_query_times':self.exp_helper_query_times,
            'guidance_query_times':self.guidance_query_times,
            'library_scale': 0,
        }
        return info