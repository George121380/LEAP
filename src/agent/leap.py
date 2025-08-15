"""
VirtualHome Agent Implementation

This module contains the main agent implementation for the VirtualHome environment,
supporting both planning and policy-based approaches with library integration.
"""

import sys
import os
import concepts.dm.crow as crow
import numpy as np
import re
import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library import behavior_library_simple
from planning import VH_pipeline
from utils.Interpretation import exploration_VH,sub_goal_generater,obs_query,sub_goal_evaluate
from utils.action_explaination import controller_to_natural_language
import pdb
import time
from .base import BaseAgent

class VHAgent(BaseAgent):
    def __init__(self, config, filepath, task_logger, PO=True, epoch_path=None):
        
        # Initialize dictionaries
        super().__init__(config, filepath, task_logger, epoch_path, agent_base_type='behavior')

        self.agent_type = self.config.agent_type # Policy or Planning
        if self.agent_type=='Policy':
            self.commit_skeleton_everything=True
        if self.agent_type=='Planning':
            self.commit_skeleton_everything=False

        # Task information
        self.current_subgoal_nl=''
        self.current_subgoal_num=0
        self.self_evaluate_times_for_current_subgoal=0
        self.guidance_block=False
        if self.config.human_guidance=='None':
            self.guidance_block=True
        self.guidance_query_times=0
        self.sub_goal_list=[]
        self.completed_sub_goal_list=[]
        self.add_info_nl=''
        self.add_info_human_instruction=''
        self.add_info_trial_and_error_info=''
        self.current_subtask_guidance=''
        self.add_info_action_history=[]
        self.add_info_action_history_for_evaluation=[]
        self.add_info_action_history_for_current_subgoal=[]
        self.exploration_behavior = ""
        self.goal_representation = ""
        self.behaviors_from_library={} # all skills in library
        self.library_pool = []
        
        # Domain CDL path: allow override via env var VH_DOMAIN_CDL
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to src/
        self.basic_domain_knowledge_file_path = os.environ.get(
            'VH_DOMAIN_CDL',
            os.path.join(BASE_DIR, 'domain', 'virtualhome_partial.cdl')
        )
        self.reset_add_info_record()
        self.reset_goal_representation_record()
        self.need_replan=True # need replan, when find something new or regenerate a goal representation
        self.plan=[]
        self.current_step=0
        self.exp_fail_num=0
        self.empty_plan_times=0
        self.max_replan_num=3
        self.library=behavior_library_simple(config, epoch_path)
        self._parse_file(filepath)
        self.save_to_file()
        self.save_to_file(self.state_file_path)
        self.exp_helper_query_times=0

        self.goal_generate_times=0
        self.goal_correct_times=0

    """
    Functions for maintaining the library
    """
    def lift_behaviors(self):
        # add executable behaviors to the library
        if self.config.record_method == 'behavior':
            for behavior in self.library_pool:
                self.library.lift(behavior['task_name'],behavior['subgoal'],behavior['goal_representation'])
        
        elif self.config.record_method == 'actions':
            for actions in self.library_pool:
                self.library.lift(actions['task_name'],actions['subgoal'],actions['action_history'])
        
    def add_to_library_pool(self):
        if self.config.record_method == 'behavior':
            info={
                'task_name':self.task_name,
                'subgoal':self.current_subgoal_nl,
                'goal_representation':self.goal_representation,
            }
            self.library_pool.append(info)
        
        elif self.config.record_method == 'actions':
            action_history_str = ''
            idx = 1
            for action in self.add_info_action_history_for_current_subgoal:
                action_history_str+=f"Action{idx}: {action['action']} - Effect: {action['effects']}\n"
                idx+=1
    
            info={
                'task_name':self.task_name,
                'subgoal':self.current_subgoal_nl,
                'action_history':action_history_str
            }

            self.add_info_action_history_for_current_subgoal = []
            self.library_pool.append(info)


    def download_behaviors_from_library(self):
        # download behaviors from the library
        if self.config.library:
            self.behaviors_from_library=self.library.download_behaviors(self.goal_nl)
        else:
            self.behaviors_from_library['content']=[]
        return self.behaviors_from_library

    def reset_visited(self):
        # reset the visited state
        self.state['visited']=np.full(self.num_items , "uncertain", dtype=object)

    def query_LLM_human(self,question:str):
        # ask for LLM-based human guidance
        record='Record from func query_LLM_human in agent.py\n'
        record+=f'Question: {question}\n'
        task_info={}
        task_info['Goal']=self.goal_nl
        task_info['Subgoals']=self.sub_goal_list
        answer,re_decompose=self.human_helper.QA(question,task_info)
        record+=f'Answer: {answer}\n'
        record+=f'Re-decompose: {re_decompose}\n'
        self.logger.info("From agent.py -> query_LLM_human\n"+record)
        print("#"*60)
        print(record)
        print("#"*60)
        return answer,re_decompose
    
    def query_real_human(self,question:str):
        # ask for real human guidance
        record='Record from func query_real_human in agent.py\n'
        record+=f'Question: {question}\n'
        print(f"The current subgoal list: {self.sub_goal_list}")
        print(f"And I am doing: {self.current_subgoal_nl}")
        re_decompose= input("Do you think I should re-decompose the task? (y/n): ")
        if re_decompose=='y' or re_decompose=='yes':
            re_decompose=True
        else:
            re_decompose=False
        answer = input(f"{question}\nYour answer: ")
        record+=f'Answer: {answer}\n'
        record+=f'Re-decompose: {re_decompose}\n'
        print("#"*60)
        print(record)
        print("#"*60)
        self.logger.info("From agent.py\n"+record)
        print("Debug: ",re_decompose)
        return answer,re_decompose
    
    def ask_for_human_task_guidance(self):
        self.guidance_query_times+=1
        if self.guidance_query_times>=3:
            self.guidance_block=True
        re_decompose=False
        question=f'Can you teach me how to "{self.current_subgoal_nl.lower()}" ?'

        if self.config.human_guidance=='LLM':
            Human_Guidance, re_decompose=self.query_LLM_human(question)

        if self.config.human_guidance=='Manual':
            Human_Guidance, re_decompose=self.query_real_human(question)

        self.current_subtask_guidance=Human_Guidance
        self.update_add_info()

        self.record_add_info()
        self.empty_plan_times=0

        return re_decompose
    
    def set_initial_human_instruction(self,goal):
        # debug used
        self.goal_nl=goal
        ini_human_instruction=self.query_LLM_human(f"Can you tell me how to {self.goal_nl.lower()}")
        if ini_human_instruction!="I don't know.":
            self.add_info_human_instruction=f"To {self.goal_nl.replace('.',',').lower()} you can {ini_human_instruction.lower()}"
        self.update_add_info()
        

    def update_add_info(self):
        self.add_info_nl=''
        if self.add_info_human_instruction:
            self.add_info_nl+=f"Human Instruction: {self.add_info_human_instruction}\n"

        if self.current_subtask_guidance:
            self.add_info_nl+=f"Human Guidance: {self.current_subtask_guidance}\n"

        if self.add_info_trial_and_error_info:
            self.add_info_nl+=f"Trial and Error: {self.add_info_trial_and_error_info}\n"

        if self.add_info_action_history:
            self.add_info_nl+="The actions you have taken:\n"
            for id in range(len(self.add_info_action_history)):
                # self.add_info_nl+=f"Action {id+1}: {controller_to_natural_language(self.add_info_action_history[id]['action'])} -> effect: {self.add_info_action_history[id]['effects']}\n"
                self.add_info_nl+=f"Action {id+1}: {controller_to_natural_language(self.add_info_action_history[id]['action'])}\n"
    
    def updates(self,observation):
        if "You can not" in observation: # if this action is not executable, environment feedback
            self.add_info_trial_and_error_info+=observation
            self.update_add_info()
            self.record_add_info()
            self.reset_sub_goal()

        else:
            action_effects=''
            if not observation['exp_flag'] and not observation['obs_flag']:# other actions
                action_effects = self.regular_action_obs_update(observation)

            if observation['exp_flag']:# action==explore
                exp_target=observation['exp_target']
                exp_loc=observation['exp_loc']
                for new_known in observation['known']:
                        if 'character' in new_known:
                            continue
                        if self.exploration['unknown'][self.name2opid[new_known]]==True:
                            self.exploration['unknown'][self.name2opid[new_known]]=False
                            
                for check_place in observation['checked']:
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                if exp_target in observation['known'] or not self.exploration['unknown'][self.name2opid[exp_target]]:
                    print(f'{exp_target} is successfully explored around {exp_loc} or already known before')
                    action_effects+=f"Find {exp_target}. "
                    self.need_replan=True # find sth new

                else:
                    if self.exp_fail_num==5:
                        self.exp_helper_query_times+=1
                        human_answer, _ =self.query_LLM_human(f'Can you help me to find {exp_target} ?')
                        print(f'Query human about the location of {exp_target}.')
                        self.exp_fail_num=0
                        self.add_info_human_instruction+=human_answer+'\n'
                        self.update_add_info()
                        self.logger.info("From agent.py\n"+self.add_info_nl)
                        self.record_add_info()

                    self.exp_fail_num+=1
                    print(f'{exp_target} is not around {exp_loc}, re-explore')
                    action_effects+=f"Fail to find {exp_target} around {exp_loc}. "
                    self.save_to_file()
                    self.save_to_file(self.state_file_path)
                    self.exploration_behavior=exploration_VH(self.goal_nl,self.add_info_nl,self.internal_executable_file_path,self.exploration['checked'])
                    self.need_replan=True

            if observation['obs_flag']: # action==observe
                obs_target=observation['obs_target']
                self.state['visited'][self.name2opid[obs_target]]=True
                for new_known in observation['known']:
                    if 'character' in new_known:
                        continue
                    if self.exploration['unknown'][self.name2opid[new_known]]==True:
                        self.exploration['unknown'][self.name2opid[new_known]]=False
                
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
            self.add_info_action_history_for_current_subgoal.append({'action':str(observation['action']),'effects':action_effects})
            self.update_add_info()
            self.logger.info("From agent.py\n"+str(observation['action'])+"\n"+action_effects)
            self.record_add_info()
            self.save_to_file()
            self.save_to_file(self.state_file_path)   


    def organize_obs_result(self,observation):
        discription=''
        for info in observation:
            if 'from_name' in info:
                from_name=info['from_name']
                to_name=info['to_name']
                r=info['relation_type']
                if r=='CLOSE':
                    discription+=f' {from_name} is close to {to_name}.'
                elif r=='FACING':
                    discription+=f' {from_name} is facing {to_name}.'
                elif r=='INSIDE':
                    discription+=f' {from_name} is inside {to_name}.'
                elif r=='ON':
                    discription+=f' {from_name} is on {to_name}.'
                elif r=='BETWEEN':
                    discription+=f' {from_name} is between {to_name}.'
            if 'states' in info:
                discription+=info['states']
        return discription

    def obs_query(self,target_obj:str,observation,question=None):
        # target_obj: the name of the object that the observation is about
        discription=self.organize_obs_result(observation)
        obs_info=obs_query(target_obj,discription,question)
        return obs_info

    def get_state(self):
        # Get the current CDL state of the agent, "problem" will be used by CDL Solver
        domain = crow.load_domain_file(self.basic_domain_knowledge_file_path)
        problem = crow.load_problem_file(self.internal_executable_file_path, domain=domain)
        return problem

    def act(self):
        while True:
            if self.need_replan: # exp and know new items
                # pdb.set_trace()
                cdl_state = self.get_state()
                #time
                plans, stats = crow.crow_regression(
                    cdl_state.domain, cdl_state, goal=cdl_state.goal,
                    is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True,
                    enable_state_hash=False,
                    verbose=False,
                    algo='priority_tree_v1'
                )

                if plans == None or len(plans) == 0: # No plan found -> usually bind is not satisfied
                    self.empty_plan_times+=1
                    if self.empty_plan_times==self.max_replan_num:
                        print(f'Try to generate the plan for {self.max_replan_num} times, but failed.')
                        break
                    if self.current_subgoal_num==0:
                        print('No plan found. Reset the whole goal')
                        self.reset_goal(self.goal_nl,self.classes,self.task_name,First_time=False,sub_goal=True)
                    else:
                        print('No plan found. Reset the sub-goal')
                        self.reset_sub_goal()
                    continue

                plan = plans[0] # Get the first plan, when there are multiple plans found by the planner
                if len(plan) == 0:# This can also be a situation that this sub-task is already finished before.
                    self.empty_plan_times+=1
                    print('plan is a empty list')
                    if self.empty_plan_times==self.max_replan_num:
                        print(f'Try to generate the plan for {self.max_replan_num} times, but failed.')
                        break
                    if self.current_subgoal_num==0:
                            print('No plan found. Reset the whole goal')
                            self.reset_goal(self.goal_nl,self.classes,self.task_name,First_time=False,sub_goal=True)
                    else:
                        print('No plan found. Reset the sub-goal')
                        self.reset_sub_goal()
                    continue
                
                # When the plan is found, we need to lift the behaviors to the library
                print('Plan found')
                plan_print=''
                for action in plan:
                    plan_print+=(str(action))
                print(plan_print)
                self.logger.info("From agent.py-> find a plan in act()\n"+plan_print)
                action = plan[0]
                self.current_step=1
                self.plan=plan
                self.need_replan=False
                return action,plan #reset
            
            else: # stick to the current plan and execute the next step
                if self.current_step==len(self.plan):
                    print('This is the last step for current sub-task')

                    ########## evaluate current subgoal start ###########
                    while True: # avoid the situation that the output does not contain both yes and no
                        result,insrtuctions=self.evaluate_current_subgoal()
                        self.self_evaluate_times_for_current_subgoal+=1
                        
                        if result.lower()=='yes':
                            # The current subgoal is complete move to next subgoal
                            self.completed_sub_goal_list.append(self.current_subgoal_nl)
                            self.self_evaluate_times_for_current_subgoal=0
                            print('current subgoal is done')
                            self.add_to_library_pool()
                            self.current_subgoal_num+=1
                            if self.config.human_guidance!='None':
                                self.guidance_block=False # reset the guided flag
                            self.current_subtask_guidance=''
                            break
                            
                        if self.self_evaluate_times_for_current_subgoal==3:
                            self.self_evaluate_times_for_current_subgoal=0
                            print('Try to evaluate the sub-task for 3 times, but still failed. Force to move to the next sub task. Probably the current sub-task is unneccesary.')
                            result='yes'
                            self.current_subgoal_num+=1
                            if self.config.human_guidance!='None':
                                self.guidance_block=False # reset the guided flag
                            self.current_subtask_guidance=''
                            break

                        if result.lower()=='no':
                            # regenerate the subgoal
                            self.add_info_human_instruction=insrtuctions+'\n'
                            self.update_add_info()
                            self.logger.info("From agent.py\n"+self.add_info_nl)
                            self.reset_sub_goal()
                            self.need_replan=True
                            self.record_add_info()
                            break
                        
                        if result.lower()!='yes' and result.lower()!='no':
                            print('Evaluate error, try again')

                    if result.lower()=='no':
                        continue

                    ########## evaluate subgoal end ###########
                    if self.current_subgoal_num==len(self.sub_goal_list):
                        print('All sub-tasks are done')
                        return "over",None
                    
                    else: # generate goal representation for next sub-task
                        self.current_subgoal_nl=self.sub_goal_list[self.current_subgoal_num]
                        self.reset_sub_goal()
                        continue

                action=self.plan[self.current_step]
                self.current_step+=1
                return action,self.plan
            
        # Beyond the max replan number
        if not self.guidance_block: # if not guided by human
            print("Try to ask for human guidance in function 'act'")
            print(self.current_subgoal_nl)
            re_decompose=self.ask_for_human_task_guidance()
            if re_decompose:
                print('Re-decompose the goal')
                self.reset_goal_decomposition()
            print('Got human guidance')
            self.reset_sub_goal()
            return "human guided",None
        else:
            return "Failed",None

    def reset_goal_decomposition(self):
        if not self.config.task_split:
            self.sub_goal_list=[self.goal_nl]
        else:
            self.sub_goal_list=sub_goal_generater(self.goal_nl,self.completed_sub_goal_list,self.current_subtask_guidance) # Generate sub goals
        print(self.sub_goal_list)
        record='Reset goals: The sub-goals are: \n'+str(self.sub_goal_list)
        # block while test
        self.logger.info("From agent.py\n"+record)
        self.current_subgoal_nl=self.sub_goal_list[0]
        self.current_subgoal_num=0
        self.current_step=0
        self.self_evaluate_times_for_current_subgoal=0


    def reset_goal(self,goal,classes,task_name,First_time=False,sub_goal=True):
        """
        config:
            goal: Full goal of the whole task
            additional_information: Human instruction + Human guidance + Action history
            classes: the classes of the objects in the environment
            First_time: whether it is the first time to set the goal
            sub_goal: whether we want to split the goal into sub-goals
        """
        self.need_replan=True
        if First_time:
            self.goal_nl=goal
            self.task_name=task_name
            self.record_add_info()
            self.classes=classes

        self.reset_goal_decomposition()
        
        # # debug
        # return
        _, self.goal_representation, self.exploration_behavior, generate_times, correct_times = VH_pipeline(
            state_file=self.state_file_path,
            execute_file=self.internal_executable_file_path,
            current_subgoal=self.current_subgoal_nl,
            add_info=self.add_info_nl,
            long_horizon_goal=self.goal_nl,
            prev_sub_goal_list=self.sub_goal_list[:self.current_subgoal_num],
            classes=self.classes,
            checked_items=self.exploration['checked'],
            behavior_from_library=self.library.download_behaviors(self.current_subgoal_nl),
            partial_observation=True,
            agent_type=self.agent_type,
            refinement=self.config.refine,
            loop_feedback=self.config.loop_feedback,
            logger=self.logger
        )
        self.goal_generate_times+=generate_times
        self.goal_correct_times+=correct_times

        # block while test
        goal_representation_record=self.goal_representation
        if self.goal_representation==None:
            goal_representation_record='Fail to generate the goal representation'
        self.logger.info("From agent.py->reset_goal\n"+goal_representation_record)

        if self.goal_representation==None:
            if self.guidance_block:
                print("Fail to generate a valid goal representation")
                return "Failed", None
            else: # Try again after asking for human guidance
                print('Ask human guidance because the agent fail to generate a valid goal representation')
                print(self.current_subgoal_nl)

                re_decompose=self.ask_for_human_task_guidance()
                if re_decompose:
                    self.reset_goal_decomposition()
                
                _, self.goal_representation, self.exploration_behavior, generate_times, correct_times = VH_pipeline(
                    state_file=self.state_file_path,
                    execute_file=self.internal_executable_file_path,
                    current_subgoal=self.current_subgoal_nl,
                    add_info=self.add_info_nl,
                    long_horizon_goal=self.goal_nl,
                    prev_sub_goal_list=self.sub_goal_list[:self.current_subgoal_num],
                    classes=self.classes,
                    checked_items=self.exploration['checked'],
                    behavior_from_library=self.library.download_behaviors(self.current_subgoal_nl),
                    partial_observation=True,
                    agent_type=self.agent_type,
                    refinement=self.config.refine,
                    loop_feedback=self.config.loop_feedback,
                    logger=self.logger
                )
                self.goal_generate_times+=generate_times
                self.goal_correct_times+=correct_times

                if self.goal_representation==None:
                    print("Fail to generate the goal representation after asking for human guidance")
                    return "Failed", None

    def reset_sub_goal(self):
        self.need_replan=True
        
        _, self.goal_representation, self.exploration_behavior, generate_times, correct_times = VH_pipeline(
            state_file=self.state_file_path,
            execute_file=self.internal_executable_file_path,
            current_subgoal=self.current_subgoal_nl,
            add_info=self.add_info_nl,
            long_horizon_goal=self.goal_nl,
            prev_sub_goal_list=self.sub_goal_list[:self.current_subgoal_num],
            classes=self.classes,
            checked_items=self.exploration['checked'],
            behavior_from_library=self.library.download_behaviors(self.current_subgoal_nl),
            partial_observation=True,
            agent_type=self.agent_type,
            refinement=self.config.refine,
            loop_feedback=self.config.loop_feedback,
            logger=self.logger
        )
        self.goal_generate_times+=generate_times
        self.goal_correct_times+=correct_times

        if self.goal_representation==None:
            if self.guidance_block:
                print("Fail to generate the goal representation")
                return "Failed", None
            else: # Try again after asking for human guidance
                print("Try to ask for human guidance in function 'reset_sub_goal'")
                print(self.current_subgoal_nl)
                re_decompose=self.ask_for_human_task_guidance()
                if re_decompose:
                    self.reset_goal_decomposition()
                
                _, self.goal_representation, self.exploration_behavior, generate_times, correct_times = VH_pipeline(
                    state_file=self.state_file_path,
                    execute_file=self.internal_executable_file_path,
                    current_subgoal=self.current_subgoal_nl,
                    add_info=self.add_info_nl,
                    long_horizon_goal=self.goal_nl,
                    prev_sub_goal_list=self.sub_goal_list[:self.current_subgoal_num],
                    classes=self.classes,
                    checked_items=self.exploration['checked'],
                    behavior_from_library=self.library.download_behaviors(self.current_subgoal_nl),
                    partial_observation=True,
                    agent_type=self.agent_type,
                    refinement=self.config.refine,
                    loop_feedback=self.config.loop_feedback,
                    logger=self.logger
                )
                self.goal_generate_times+=generate_times
                self.goal_correct_times+=correct_times

                if self.goal_representation==None:
                    print("Fail to generate the goal representation after asking for human guidance")
                    return "Failed", None
                
        # block while test
        if self.goal_representation != None:
            self.logger.info("From agent.py->reset_sub_goal\n"+self.goal_representation)
        self.reset_visited()
        self.record_goal_representation()
        self.save_to_file()
        self.save_to_file(self.state_file_path)
        

    def evaluate_current_subgoal(self):
        if self.current_subgoal_num==len(self.sub_goal_list)-1:
            result,insrtuctions=sub_goal_evaluate(self.goal_representation,self.add_info_action_history,self.current_subgoal_nl,self.goal_nl, 'This is the last sub-task',self.add_info_nl,self.name2opid.keys())
        else:
            print(f"current_subgoal_num: {self.current_subgoal_num}")
            result,insrtuctions=sub_goal_evaluate(self.goal_representation,self.add_info_action_history,self.current_subgoal_nl,self.goal_nl, self.sub_goal_list[self.current_subgoal_num+1],self.add_info_nl,self.name2opid.keys())

        self.logger.info("From agent.py -> evaluate_current_subgoal()\n"+"The evaluation result for current subgoal: "+str(result)+"\nThe feedback instruction: "+insrtuctions)
        return result,insrtuctions
    
    def final_human_check(self): # ask human to check whether the task is done, removed
        print('Ask human to check whether the task is done')
        pass

    def final_important_numbers_report(self):
        info={
            'exp_helper_query_times':self.exp_helper_query_times,
            'guidance_query_times':self.guidance_query_times,
            'library_scale':len(self.library.metadata),
            'goal_generate_times':self.goal_generate_times,
            'goal_correct_times':self.goal_correct_times,
        }
        return info
    
    def reset_add_info_record(self):
        record_path='visualization/add_info_monitor.txt'
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path,'w') as f:
            f.write('')

    def record_add_info(self):
        record_path='visualization/add_info_monitor.txt'
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path,'w') as f:
            f.write(self.add_info_nl)

    def reset_goal_representation_record(self):
        record_path='visualization/goal_representation_monitor.txt'
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path,'w') as f:
            f.write('')
    
    def record_goal_representation(self):
        record_path='visualization/goal_representation_monitor.txt'
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path,'w') as f:
            f.write(self.goal_representation)