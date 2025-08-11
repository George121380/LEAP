# from env_kitchen import Agent,KitchenEnvironment
import sys
import json
from preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination
from execution import Relation, State
from utils_eval import get_from_dataset
import utils as utils
from environment import EnvironmentState, EnvironmentGraph


def set_size(size_dict):
    """Update node sizes in the draft scene graph used for simulation setup."""
    draft_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VirtualHome-HG', 'assert', 'draft.json')
    graph_dict = json.load(open(draft_path, "r"))
    for node in graph_dict['nodes']:
        if node['id'] in size_dict:
            assert node['class_name']==size_dict[node['id']]['name']
            node['size']=size_dict[node['id']]['size']

    with open(draft_path, 'w') as f:
        json.dump(graph_dict, f)

def scene_0_add_items_round1():
    change=[
        AddObject('basket_for_clothes', [Destination.close(42),Destination.close(30),Destination.close(22),Destination.close(37),Destination.close(36),Destination.close(43),Destination.close(32),Destination.close(31),Destination.close(33),Destination.close(34)], [State.OPEN]),
        AddObject('washing_machine', [Destination.close(42)], [State.CLEAN,State.OFF,State.CLOSED,State.PLUGGED_OUT]),
        AddObject('food_steak', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_apple', [Destination.inside(289)], [State.DIRTY]),
        AddObject('food_bacon', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_banana', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_bread', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_cake', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_carrot', [Destination.inside(289)], [State.DIRTY]),
        AddObject('food_cereal', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_cheese', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_chicken', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_dessert', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_donut', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_egg', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_fish', [Destination.inside(289)], [State.DIRTY]),
        AddObject('food_food', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_fruit', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_hamburger', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_ice_cream', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_jam', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_kiwi', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_lemon', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_noodles', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_oatmeal', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_orange', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_onion', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_peanut_butter', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_pizza', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_potato', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_rice', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_salt', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_snack', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_sugar', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_turkey', [Destination.inside(289)], [State.CLEAN]),
        AddObject('food_vegetable', [Destination.inside(289)], [State.DIRTY]),
        AddObject('dry_pasta', [Destination.inside(289)], [State.CLEAN]),
        AddObject('milk', [Destination.inside(289)], []),
        AddObject('clothes_dress', [Destination.on(105)], [State.DIRTY]),
        AddObject('clothes_hat', [Destination.on(107)], [State.CLEAN]),
        AddObject('clothes_gloves', [Destination.on(107)], [State.CLEAN]),
        AddObject('clothes_jacket', [Destination.on(352)], [State.DIRTY]),
        AddObject('clothes_scarf', [Destination.on(105)], [State.DIRTY]),
        AddObject('clothes_underwear', [Destination.on(105)], [State.DIRTY]),
        AddObject('knife', [Destination.on(230)], [State.CLEAN]),
        AddObject('cutting_board', [Destination.on(230)], [State.CLEAN]),
        AddObject('remote_control', [Destination.on(352)], [State.OFF]),
        AddObject('soap', [Destination.on(42)], [State.CLEAN]),
        AddObject('soap', [Destination.on(231)], [State.CLEAN]),
        AddObject('cat', [Destination.on(352)], []),
        AddObject('towel', [Destination.on(31)], [State.CLEAN]),
        AddObject('towel', [Destination.on(32)], [State.CLEAN]),
        AddObject('towel', [Destination.on(33)], [State.CLEAN]),
        AddObject('towel', [Destination.on(34)], [State.CLEAN]),
        AddObject('cd_player', [Destination.on(225)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('dvd_player', [Destination.on(353)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('headset', [Destination.on(355)], []),
        AddObject('cup', [Destination.on(230)], []),
        AddObject('cup', [Destination.on(230)], []),
        AddObject('stove', [Destination.on(230)], [State.OFF,State.CLOSED]),
        AddObject('book', [Destination.on(354)], []),
        AddObject('book', [Destination.on(354)], []),
        AddObject('coffee_table', [Destination.inside(319)], []),
        AddObject('pot', [Destination.on(230)], [State.CLOSED]),
        AddObject('vacuum_cleaner', [Destination.close(352)], [State.OFF,State.CLEAN,State.PLUGGED_OUT]),
        AddObject('bowl', [Destination.on(226)], [State.DIRTY]),
        AddObject('bowl', [Destination.on(226)], [State.DIRTY]),
        AddObject('cleaning_solution', [Destination.on(42)], []),
        AddObject('ironing_board', [Destination.inside(1)], []),
        AddObject('cd', [Destination.on(225)], []),
        AddObject('headset', [Destination.on(357)], []),
        AddObject('phone', [Destination.on(357)], [State.OFF,State.CLEAN]),
        AddObject('sauce', [Destination.inside(289)], []),
        AddObject('oil', [Destination.on(230)], []),
        AddObject('fork', [Destination.on(226)], []),
        AddObject('fork', [Destination.on(226)], []),
        AddObject('spectacles', [Destination.on(355)], []),
        AddObject('fryingpan', [Destination.on(230)], [State.CLEAN]),
        AddObject('detergent', [Destination.on(42)], [State.CLEAN]),

        ChangeState('television', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('computer', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('plate', [State.DIRTY]),
        ChangeState('sink', [State.DIRTY]),
        ChangeState('freezer', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.ON]),
        ChangeState('light', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('dishwasher', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('window', [State.CLOSED,State.DIRTY]),
        ChangeState('book', [State.CLOSED]),
    ]
    

    dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"
    #scene1
    file_id='1047_2'
    scenegraph=1

    init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph, file_id))
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    prepare_1 = StatePrepare(properties_data, change)
    
    state=EnvironmentState(init_scene_graph,name_equivalence)
    prepare_1.apply_changes(state)
    state.save_graph(draft_path)

def scene_0_add_items_round2():
    change=[
        AddObject('clothes_pants', [Destination.inside(2006)], [State.DIRTY]),
        AddObject('clothes_shirt', [Destination.inside(2006)], [State.DIRTY]),
        AddObject('clothes_socks', [Destination.inside(2006)], [State.DIRTY]),
        AddObject('clothes_skirt', [Destination.inside(2006)], [State.DIRTY]),
        AddObject('iron', [Destination.on(2074)], [State.CLEAN,State.OFF,State.PLUGGED_OUT]),
        AddObject('toilet_paper', [Destination.close(37)], [State.CLEAN]),
    ]

    graph_dict = json.load(open(draft_path, "r"))
    init_scene_state = graph_dict
    init_scene_graph = EnvironmentGraph(init_scene_state)
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    
    state=EnvironmentState(init_scene_graph,name_equivalence)

    prepare_2 = StatePrepare(properties_data, change)
    prepare_2.apply_changes(state)
    state.save_graph(draft_path)

def scene_0_set_size():
    size_dict={
        290:{'name':'coffe_maker', 'size': 8},
        2063:{'name':'cup', 'size': 10},
        2064:{'name':'cup', 'size': 5},
        2055:{'name':'cat', 'size': 15},
        42:{'name':'sink', 'size': 20},
        231:{'name':'sink', 'size': 12},
        2071:{'name':'bowl', 'size': 3},
        2072:{'name':'bowl', 'size': 10},
        2041:{'name':'food_vegetable', 'size': 5},
    }
    # add vegetable size, add pot size
    set_size(size_dict)

def scene_0():
    scene_0_add_items_round1()
    scene_0_add_items_round2()
    scene_0_set_size()

###############################################################################

def scene_1_add_items_round1():
    change=[
        AddObject('basket_for_clothes', [Destination.close(126),Destination.close(120)], [State.OPEN]),
        AddObject('washing_machine', [Destination.close(120),Destination.close(126)], [State.CLEAN,State.OFF,State.CLOSED,State.PLUGGED_OUT]),
        AddObject('food_steak', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_apple', [Destination.inside(126)], [State.DIRTY]),
        AddObject('food_bacon', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_banana', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_bread', [Destination.on(114)], [State.CLEAN]),
        AddObject('food_cake', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_carrot', [Destination.inside(126)], [State.DIRTY]),
        AddObject('food_cereal', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_cheese', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_chicken', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_dessert', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_donut', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_egg', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_fish', [Destination.inside(126)], [State.DIRTY]),
        AddObject('food_food', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_fruit', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_hamburger', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_ice_cream', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_jam', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_kiwi', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_lemon', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_noodles', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_oatmeal', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_orange', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_onion', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_peanut_butter', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_pizza', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_potato', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_rice', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_salt', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_snack', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_sugar', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_turkey', [Destination.inside(126)], [State.CLEAN]),
        AddObject('food_vegetable', [Destination.inside(126)], [State.DIRTY]),
        AddObject('dry_pasta', [Destination.on(114)], [State.CLEAN]),
        AddObject('milk', [Destination.on(114)], []),
        AddObject('clothes_dress', [Destination.on(197)], [State.DIRTY]),
        AddObject('clothes_hat', [Destination.on(114)], [State.CLEAN]),
        AddObject('clothes_gloves', [Destination.on(114)], [State.CLEAN]),
        AddObject('clothes_jacket', [Destination.on(198)], [State.DIRTY]),
        AddObject('clothes_scarf', [Destination.on(197)], [State.DIRTY]),
        AddObject('clothes_underwear', [Destination.on(197)], [State.DIRTY]),
        AddObject('knife', [Destination.on(114)], [State.CLEAN]),
        AddObject('cutting_board', [Destination.on(119)], [State.CLEAN]),
        AddObject('remote_control', [Destination.on(273)], [State.OFF]),
        AddObject('soap', [Destination.on(19)], [State.CLEAN]),
        AddObject('soap', [Destination.on(120)], [State.CLEAN]),
        AddObject('cat', [Destination.on(198)], []),
        AddObject('towel', [Destination.inside(33)], [State.CLEAN]),
        AddObject('cd_player', [Destination.on(273)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('dvd_player', [Destination.on(273)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('headset', [Destination.on(273)], []),
        AddObject('cup', [Destination.on(114)], []),
        AddObject('cup', [Destination.on(114)], []),
        AddObject('cup', [Destination.on(114)], []),
        AddObject('stove', [Destination.on(119)], [State.OFF,State.CLOSED]),
        AddObject('book', [Destination.on(124)], []),
        AddObject('book', [Destination.on(124)], []),
        AddObject('pot', [Destination.on(119)], [State.CLOSED]),
        AddObject('vacuum_cleaner', [Destination.close(99)], [State.OFF,State.CLEAN,State.PLUGGED_OUT]),
        AddObject('bowl', [Destination.on(119)], [State.DIRTY]),
        AddObject('bowl', [Destination.on(119)], [State.DIRTY]),
        AddObject('bowl', [Destination.on(119)], [State.DIRTY]),
        AddObject('cleaning_solution', [Destination.on(19)], []),
        AddObject('ironing_board', [Destination.inside(41)], []),
        AddObject('cd', [Destination.on(273)], []),
        AddObject('headset', [Destination.on(272)], []),
        AddObject('phone', [Destination.on(272)], [State.OFF,State.CLEAN]),
        AddObject('sauce', [Destination.inside(126)], []),
        AddObject('oil', [Destination.on(123)], []),
        AddObject('fork', [Destination.on(119)], [State.CLEAN]),
        AddObject('fork', [Destination.on(119)], [State.CLEAN]),
        AddObject('plate', [Destination.on(119)], [State.CLEAN]),
        AddObject('spectacles', [Destination.on(122)], []),
        AddObject('fryingpan', [Destination.on(122)], [State.CLEAN]),
        AddObject('detergent', [Destination.on(19)], [State.CLEAN]),
        AddObject('window', [Destination.inside(1)], [State.CLOSED,State.DIRTY]),
    ]
    

    dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"

    #scene2
    file_id='4_1'
    scenegraph=2
    init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph, file_id))
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    prepare_1 = StatePrepare(properties_data, change)
    
    state=EnvironmentState(init_scene_graph,name_equivalence)
    prepare_1.apply_changes(state)
    state.save_graph('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/assert/draft.json')

def scene_1_add_items_round2():
    change=[
        AddObject('clothes_pants', [Destination.inside(2078)], [State.DIRTY]),
        AddObject('clothes_shirt', [Destination.inside(2078)], [State.DIRTY]),
        AddObject('clothes_socks', [Destination.inside(2078)], [State.DIRTY]),
        AddObject('clothes_skirt', [Destination.inside(2078)], [State.DIRTY]),
        AddObject('iron', [Destination.on(2142)], [State.CLEAN,State.OFF,State.PLUGGED_OUT]),
        ChangeState('television', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('computer', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('plate', [State.DIRTY]),
        ChangeState('sink', [State.DIRTY]),
        ChangeState('freezer', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.ON]),
        ChangeState('light', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('dishwasher', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('window', [State.CLOSED,State.DIRTY]),
        ChangeState('book', [State.CLOSED]),
    ]

    graph_dict = json.load(open(draft_path, "r"))
    init_scene_state = graph_dict
    init_scene_graph = EnvironmentGraph(init_scene_state)
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    
    state=EnvironmentState(init_scene_graph,name_equivalence)

    prepare_2 = StatePrepare(properties_data, change)
    prepare_2.apply_changes(state)
    state.save_graph(draft_path)


def scene_1_set_size():
    size_dict={
        130:{'name':'coffe_maker', 'size': 8},
        2132:{'name':'cup', 'size': 10},
        2133:{'name':'cup', 'size': 5},
        2134:{'name':'cup', 'size': 9},
        2069:{'name':'cat', 'size': 15},
        19:{'name':'sink', 'size': 20},
        120:{'name':'sink', 'size': 12},
        2140:{'name':'bowl', 'size': 3},
        2141:{'name':'bowl', 'size': 10},
        2142:{'name':'bowl', 'size': 4},
        2113:{'name':'food_vegetable', 'size': 5},
        2089:{'name':'food_chicken', 'size': 8},
        2138:{'name':'pot', 'size': 4},
        78:{'name':'pot', 'size': 10},
        2040:{'name':'pot', 'size': 15},
        2093:{'name':'food_fish', 'size': 8},

    }
    # add vegetable size, add pot size
    # add vegetable size, add pot size
    set_size(size_dict)


def scene_1():
    scene_1_add_items_round1()
    scene_1_add_items_round2()
    scene_1_set_size()


###############################################################################

def scene_2_add_items_round1():
    change=[
        AddObject('basket_for_clothes', [Destination.close(287),Destination.close(297)], [State.OPEN]),
        AddObject('washing_machine', [Destination.close(287),Destination.close(297)], [State.CLEAN,State.OFF,State.CLOSED,State.PLUGGED_OUT]),
        AddObject('food_steak', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_apple', [Destination.inside(140)], [State.DIRTY]),
        AddObject('food_bacon', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_banana', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_cake', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_carrot', [Destination.inside(140)], [State.DIRTY]),
        AddObject('food_cereal', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_cheese', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_chicken', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_dessert', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_donut', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_egg', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_fish', [Destination.inside(140)], [State.DIRTY]),
        AddObject('food_food', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_fruit', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_hamburger', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_ice_cream', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_jam', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_kiwi', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_lemon', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_noodles', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_oatmeal', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_peanut_butter', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_pizza', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_potato', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_rice', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_salt', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_snack', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_sugar', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_turkey', [Destination.inside(140)], [State.CLEAN]),
        AddObject('food_vegetable', [Destination.inside(140)], [State.DIRTY]),

        AddObject('dry_pasta', [Destination.on(140)], [State.CLEAN]),
        AddObject('milk', [Destination.on(140)], []),
        AddObject('clothes_dress', [Destination.on(264)], [State.DIRTY]),
        AddObject('clothes_hat', [Destination.on(238)], [State.CLEAN]),
        AddObject('clothes_gloves', [Destination.on(238)], [State.CLEAN]),
        AddObject('clothes_jacket', [Destination.on(264)], [State.DIRTY]),
        AddObject('clothes_scarf', [Destination.on(264)], [State.DIRTY]),
        
        AddObject('cutting_board', [Destination.on(128)], [State.CLEAN]),
        AddObject('remote_control', [Destination.on(135)], [State.OFF]),
        AddObject('cat', [Destination.on(192)], []),
        AddObject('towel', [Destination.on(298)], [State.CLEAN]),
        AddObject('cd_player', [Destination.on(135)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('dvd_player', [Destination.on(135)], [State.CLOSED,State.OFF,State.PLUGGED_OUT]),
        AddObject('headset', [Destination.on(262)], []),
        AddObject('cup', [Destination.on(123)], []),
        AddObject('cup', [Destination.on(123)], []),
        AddObject('cup', [Destination.on(137)], []),
        AddObject('stove', [Destination.on(129)], [State.OFF,State.CLOSED]),
        AddObject('book', [Destination.on(136)], []),
        AddObject('book', [Destination.on(137)], []),
        AddObject('pot', [Destination.on(129)], [State.CLOSED]),
        AddObject('vacuum_cleaner', [Destination.close(192)], [State.OFF,State.CLEAN,State.PLUGGED_OUT]),
        AddObject('bowl', [Destination.on(123)], [State.DIRTY]),
        AddObject('bowl', [Destination.on(127)], [State.DIRTY]),
        AddObject('bowl', [Destination.on(127)], [State.DIRTY]),
        AddObject('cleaning_solution', [Destination.on(133)], []),
        AddObject('ironing_board', [Destination.inside(220)], []),
        AddObject('cd', [Destination.on(186)], []),
        AddObject('sauce', [Destination.inside(140)], []),
        AddObject('oil', [Destination.on(129)], []),
        AddObject('fork', [Destination.on(123)], [State.CLEAN]),
        AddObject('fork', [Destination.on(127)], [State.CLEAN]),
        AddObject('plate', [Destination.on(127)], [State.CLEAN]),
        AddObject('spectacles', [Destination.on(128)], []),
        AddObject('fryingpan', [Destination.on(129)], [State.CLEAN]),
        AddObject('detergent', [Destination.on(307)], [State.CLEAN]),
        AddObject('window', [Destination.inside(1)], [State.CLOSED,State.DIRTY]),
        AddObject('computer', [Destination.on(193)], [State.PLUGGED_IN,State.CLEAN,State.OFF]),

    ]
    

    dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"

    #scene2
    file_id='273_1'
    scenegraph=3
    init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph, file_id))
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    prepare_1 = StatePrepare(properties_data, change)
    
    state=EnvironmentState(init_scene_graph,name_equivalence)
    prepare_1.apply_changes(state)
    state.save_graph('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/assert/draft.json')

def scene_2_add_items_round2():
    change=[
        AddObject('keyboard', [Destination.on(193),Destination.close(2110)], [State.PLUGGED_IN,State.CLEAN]),
        AddObject('mouse', [Destination.on(193),Destination.close(2110)], [State.PLUGGED_OUT,State.CLEAN]),
        AddObject('clothes_pants', [Destination.inside(2040)], [State.DIRTY]),
        AddObject('clothes_shirt', [Destination.inside(2040)], [State.DIRTY]),
        AddObject('clothes_socks', [Destination.inside(2040)], [State.DIRTY]),
        AddObject('clothes_skirt', [Destination.inside(2040)], [State.DIRTY]),
        AddObject('iron', [Destination.on(2099)], [State.CLEAN,State.OFF,State.PLUGGED_OUT]),
        AddObject('toilet_paper', [Destination.close(302)], [State.CLEAN]),
        AddObject('chair', [Destination.close(2110),Destination.close(193)], [State.PLUGGED_IN,State.CLEAN]),
        ChangeState('television', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('computer', [State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('plate', [State.DIRTY]),
        ChangeState('sink', [State.DIRTY]),
        ChangeState('freezer', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.ON]),
        ChangeState('light', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('dishwasher', [State.CLOSED,State.CLEAN,State.PLUGGED_IN,State.OFF]),
        ChangeState('window', [State.CLOSED,State.DIRTY]),
        ChangeState('book', [State.CLOSED]),
    ]

    graph_dict = json.load(open('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/assert/draft.json', "r"))
    init_scene_state = graph_dict
    init_scene_graph = EnvironmentGraph(init_scene_state)
    properties_data = utils.load_properties_data()
    name_equivalence = utils.load_name_equivalence()
    
    state=EnvironmentState(init_scene_graph,name_equivalence)

    prepare_2 = StatePrepare(properties_data, change)
    prepare_2.apply_changes(state)
    state.save_graph('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/assert/draft.json')

def scene_2_set_size():
    size_dict={
        147:{'name':'coffe_maker', 'size': 8},
        2006:{'name':'cup', 'size': 10},
        2087:{'name':'cup', 'size': 5},
        2088:{'name':'cup', 'size': 8},
        2089:{'name':'cup', 'size': 9},
        2082:{'name':'cat', 'size': 15},
        133:{'name':'sink', 'size': 20},
        307:{'name':'sink', 'size': 12},
        2095:{'name':'bowl', 'size': 3},
        2096:{'name':'bowl', 'size': 10},
        2097:{'name':'bowl', 'size': 4},
        2072:{'name':'food_vegetable', 'size': 5},
        2050:{'name':'food_chicken', 'size': 8},
        2093:{'name':'pot', 'size': 4},
        54:{'name':'pot', 'size': 10},
        2054:{'name':'food_fish', 'size': 8},

    }
    # add vegetable size, add pot size
    # add vegetable size, add pot size
    set_size(size_dict)

def scene_2():
    scene_2_add_items_round1()
    scene_2_add_items_round2()
    scene_2_set_size()



if __name__=='__main__':
    scene_2()
    