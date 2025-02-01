"""
    Project's main config.
"""

import os
import json
from dataclasses import dataclass
from environment import EnvironmentState, EnvironmentGraph
from utils_eval import get_nodes_information,construct_cdl, CrowControllerApplier, load_config, evaluation_task_loader, namespace_to_dict
from agent import VHAgent
from agent_LLM import LLM_Agent
from human import Human


@dataclass
# Baseline
class OursWG:

    exp_name: str = "Ours"
    task_split: bool = True
    refine: bool = True
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "behavior" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "OursWG"


@dataclass
# Baseline
class OursWOG:

    exp_name: str = "Ours"
    task_split: bool = True
    refine: bool = True
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "behavior" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "None" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "OursWOG"


@dataclass
# Baseline
class LLMWG:

    exp_name: str = "LLM"
    task_split: bool = False
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "LLMWG"


@dataclass
# Baseline
class LLMWOG:

    exp_name: str = "LLM"
    task_split: bool = False
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "None" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "LLMWOG"


@dataclass
# Baseline
class LLMPlusPWG:

    exp_name: str = "LLMPlusP"
    task_split: bool = False
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "LLMPlusPWG"


@dataclass
# Baseline
class LLMPlusPWOG:

    exp_name: str = "LLMPlusP"
    task_split: bool = False
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "None" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "LLMPlusPWOG"


@dataclass
# Baseline
class CAPWG:

    exp_name: str = "CAP"
    task_split: bool = True
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "CAPWG"


@dataclass
# Baseline
class CAPWOG:

    exp_name: str = "CAP"
    task_split: bool = True
    refine: bool = False
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "None" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "CAPWOG"


@dataclass
# Ablation1 - library study
class WOLibrary:

    exp_name: str = "Ours"
    task_split: bool = True
    refine: bool = True
    loop_feedback: bool = False
    library: bool = False
    extract_method: str = "None" # Method to embed the library, options: "whole", "rag"
    record_method: str = "None" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "WOLibrary"


@dataclass
# Ablation1 - library study
class ActionLibrary:

    exp_name: str = "Ours"
    task_split: bool = True
    refine: bool = True
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "actions" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "ActionLibrary"


@dataclass
# Ablation2 - refinement study
class WORefinement:

    exp_name: str = "Ours"
    task_split: bool = True
    refine: bool = False
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "behavior" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "WORefinement"


@dataclass
# Ablation3 - refinement study
class WOSplit:

    exp_name: str = "Ours"
    task_split: bool = False
    refine: bool = True
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "behavior" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "WOSplit"

@dataclass
# Ablation4 - Policy and Planning
class PvP:

    exp_name: str = "CAP"
    task_split: bool = True
    refine: bool = True
    loop_feedback: bool = False
    library: bool = True
    extract_method: str = "whole" # Method to embed the library, options: "whole", "rag"
    record_method: str = "behavior" # Method to record the library, options: 'behavior', 'actions'
    human_guidance: str = "LLM" # Guidance type, options: "LLM", "Manual", "None"
    scene_id: int = 0
    checkpoint: str = None
    logger_name: str = "PvP"



def load_scene(scene_id, epoch_path):
    """
    Load a predefined scene based on its ID.
    """
    scene_path=f'cdl_dataset/scenes/Scene_{scene_id}.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)

    # Generate CDL for NPO
    objects,states,relationships,properties,categories,classes,cat_statement,sizes=get_nodes_information(init_scene_graph,PO=False)
    INIT_PATH_NPO = f"{epoch_path}/init_scene_NPO.cdl"
    construct_cdl(INIT_PATH_NPO,objects,states,relationships,properties,cat_statement,sizes)

    # Generate CDL for PO
    objects,states,relationships,properties,categories,classes,cat_statement,sizes=get_nodes_information(init_scene_graph)
    INIT_PATH_PO = f"{epoch_path}/init_scene_PO.cdl"
    construct_cdl(INIT_PATH_PO,objects,states,relationships,properties,cat_statement,sizes)
    return classes,init_scene_graph



def set_agent(config, init_scene_graph, task_data, classes, task_logger, epoch_path):

    """
    Set the agent based on the experiment configuration.
    """
    INIT_PATH_PO = f"{epoch_path}/init_scene_PO.cdl"

    if config.exp_name in ['Ours','LLMPlusP','CAP']:

        if config.exp_name in ['CAP']: # policy agent
            config.agent_type='Policy'
        else:
            config.agent_type='Planning'
        agent = VHAgent(
            config=config, 
            filepath=INIT_PATH_PO, 
            task_logger=task_logger, 
            PO=True, 
            epoch_path=epoch_path
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR
        agent.download_behaviors_from_library()

    if config.exp_name in ['LLM']:

        long_task_list = [
            "/dataset/Put_groceries_in_Fridge/g3.txt",
            "/dataset/Put_groceries_in_Fridge/g5.txt"
            ]
        key_folder = "cdl_dataset"
        task_path = task_data['task_path'].split(key_folder)[1]
        if task_path in long_task_list:
            difficulty = 150
        else:
            difficulty = 50

        agent = LLM_Agent(
            config=config,
            filepath=INIT_PATH_PO,
            task_logger=task_logger,
            epoch_path=epoch_path,
            difficulty=difficulty
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],task_data['Task name'])#ini a GR
        agent.item_infoto_nl()

    return agent


# def test_human_guidance():
        ######## Test Human Guidance ########
    # log_path = f'log/epoch_{timestamp}/test_all_human_guidance.json'
    
    # # Ensure the file exists and has valid JSON
    # if os.path.exists(log_path):
    #     with open(log_path, 'r') as f:
    #         try:
    #             existing_data = json.load(f)
    #         except json.JSONDecodeError:
    #             existing_data = []
    # else:
    #     existing_data = []
    
    # Human_Guidance=[]
    # Human_Guidance.append({'task_name':log_name,'goal':task_data['Goal'],'guidance':task_data['Guidance']})
    # for sub_goal in agent.sub_goal_list:
    #     question=re.sub(r'^\d+[\.\:]?\s*', '', sub_goal.lower())
    #     question="Can you tell me how to "+question
    #     print("#"*80)
    #     print(question)
    #     print("#"*80)
    #     answer=agent.query_LLM_human(question)
    #     # Human_Guidance.append(answer)
    #     question_pair={'question':question,'answer':answer}
    #     Human_Guidance.append(question_pair)

    # existing_data.append(Human_Guidance)
    
    # # Save the updated data
    # with open(log_path, 'w') as f:
    #     json.dump(existing_data, f, indent=4)
    ######## Test Human Guidance ########