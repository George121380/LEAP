"""
    Project's main config.
"""

import os
import json
from dataclasses import dataclass
import sys

# Add simulator to path for environment imports
import sys
from pathlib import Path

# Use pathlib for cleaner path handling
BASE_DIR = Path(__file__).parent
SIMULATOR_DIR = BASE_DIR / 'simulator'

if str(SIMULATOR_DIR) not in sys.path:
    sys.path.append(str(SIMULATOR_DIR))

try:
    from environment import EnvironmentState, EnvironmentGraph
except ImportError:
    # Fallback for development/testing
    print("Warning: Could not import environment modules. Make sure VirtualHome simulator is properly set up.")
from utils.utils import get_nodes_information,construct_cdl, CrowControllerApplier, load_config, evaluation_task_loader, namespace_to_dict
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
    extract_method: str = "rag" # Method to embed the library, options: "whole", "rag"
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



def load_scene(scene_id: int, epoch_path: str) -> tuple:
    """
    Load a predefined scene based on its ID.
    
    Args:
        scene_id: ID of the scene to load (0, 1, or 2)
        epoch_path: Path to the epoch directory for saving CDL files
    
    Returns:
        tuple: (classes, init_scene_graph)
    """
    from paths import dataset_scenes_dir
    scene_path = Path(dataset_scenes_dir()) / f'Scene_{scene_id}.json'
    
    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_path}")
    
    with open(scene_path) as f:
        scene = json.load(f)
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

        # Adjust difficulty based on task complexity
        long_task_list = [
            "/dataset/Put_groceries_in_Fridge/g3.txt",
            "/dataset/Put_groceries_in_Fridge/g5.txt"
        ]
        key_folder = "cdl_dataset"
        task_path = task_data['task_path'].split(key_folder)[1]
        difficulty = 150 if task_path in long_task_list else 50


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


