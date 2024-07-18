import json
import sys
sys.path.append('../simulation')
import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import *
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph
from evolving_graph.preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination
from evolving_graph.environment import *



def state_translation(objname, state):

    mapping = {
    State.CLOSED: "closed[x: item]",
    State.OPEN: "open[x: item]",
    State.ON: "is_on[x: item]",
    State.OFF: "is_off[x: item]",
    State.SITTING: "sitting[x: character]",
    State.DIRTY: "dirty[x: item]",
    State.CLEAN: "clean[x: item]",
    State.LYING: "lying[x: character]",
    State.PLUGGED_IN: "plugged[x: item]",
    State.PLUGGED_OUT: "unplugged[x: item]",
    Property.SURFACES: "surfaces[x: item]",
    Property.GRABBABLE: "grabbable[x: item]",
    Property.SITTABLE: "sittable[x: item]",
    Property.LIEABLE: "lieable[x: item]",
    Property.HANGABLE: "hangable[x: item]",
    Property.DRINKABLE: "drinkable[x: item]",
    Property.EATABLE: "eatable[x: item]",
    Property.RECIPIENT: "recipient[x: item]",
    Property.CUTTABLE: "cuttable[x: item]",
    Property.POURABLE: "pourable[x: item]",
    Property.CAN_OPEN: "can_open[x: item]",
    Property.HAS_SWITCH: "has_switch[x: item]",
    Property.READABLE: "readable[x: item]",
    Property.LOOKABLE: "lookable[x: item]",
    Property.CONTAINERS: "containers[x: item]",
    Property.CLOTHES: "clothes[x: item]",
    Property.PERSON: "person[x: item]",
    Property.BODY_PART: "body_part[x: item]",
    Property.COVER_OBJECT: "cover_object[x: item]",
    Property.HAS_PLUG: "has_plug[x: item]",
    Property.HAS_PAPER: "has_paper[x: item]",
    Property.MOVABLE: "movable[x: item]",
    Property.CREAM: "cream[x: item]",
}

    feature = mapping.get(state, "Unknown feature")
    return feature.replace("x: item", f"{objname}").replace("x: character", f"x: {objname}")+" = True"

def relationship_translation(graph,edge):
    relation_mapping = {
        "ON": "on",
        "INSIDE": "inside",
        "BETWEEN": "between",
        "CLOSE": "close",
        "FACING": "facing",
        "HOLDS_RH": "holds_rh",
        "HOLDS_LH": "holds_lh"
    }
    from_obj_name=graph._node_map[edge['from_id']].class_name+'.'+str(edge['from_id'])
    to_obj_name=graph._node_map[edge['to_id']].class_name+'.'+str(edge['to_id'])
    relation_type=edge['relation_type']
    if relation_type in relation_mapping:
        relation = relation_mapping[relation_type]
        return f"{relation}[{from_obj_name},{to_obj_name}]=True"
    else:
        relation = "Unknown relation"

def print_node_names(n_list):
    if len(n_list) > 0:
        print([n.class_name for n in n_list])

def get_node_by_name(name,graph):
    nodes=graph.get_nodes()
    for node in nodes:
        if node.class_name == name:
            return node
    else:
        return None

def relationships_with_node(node,graph):
    graph_dict=graph.to_dict()
    id=node.id
    relationships=[]
    for edge in graph_dict['edges']:
        if edge['from_id']==id:
            relationships.append(edge)
    return relationships

def relationships_discription(relationships,graph):
    for relationship in relationships:
        print(relationship['relation_type'],graph.get_node_map()[relationship['to_id']])

def get_nodes_information(graph):
    nodes=graph.get_nodes()
    edges=graph.get_edges()
    objects=[]
    category=[]
    states=[]
    relationships=[]
    properties=[]
    for node in nodes:
        if node.category !='Characters':
            category.append(node.category)
            executable_objname=node.class_name+'.'+str(node.id)
            objects.append(executable_objname+":item")
            for state in node.states:
                state=state_translation(executable_objname,state)
                states.append(state)
            for property in node.properties:
                property=state_translation(executable_objname,property)
                properties.append(property)
    for edge in edges:
        relationship=relationship_translation(graph,edge)
        relationships.append(relationship)

            
            # print(node.class_name,node.states)
    return objects,states,relationships,properties

def run():
    graph = utils.load_graph('test_graph.json')
    get_nodes_information(graph)
    objects,states,relationships,properties=get_nodes_information(graph)
    # print("plate states are:", ini_plate.states)
    name_equivalence = utils.load_name_equivalence()
    plate = get_node_by_name('cup',graph)
    relationships=relationships_with_node(plate,graph)
    print(plate.states)   
    relationships_discription(relationships,graph)
    # script = read_script('example_scripts/example_script_1.txt')
    script = read_script('test_script.txt')
    executor = ScriptExecutor(graph, name_equivalence)
    state_enum = executor.find_solutions(script)
    state = next(state_enum, None)
    # # Add missing objects (random)
    # properties_data = utils.load_properties_data()
    # object_placing = utils.load_object_placing()
    # prepare_1 = AddMissingScriptObjects(name_equivalence, properties_data, object_placing)

    # # Add 10 random objects
    # prepare_2 = AddRandomObjects(properties_data, object_placing, choices=10)
    # prepare_3 = ChangeObjectStates(properties_data)
    # state_enum = executor.find_solutions(script, [prepare_1, prepare_2, prepare_3])
    # state = next(state_enum, None)
    if state is None:
        print('Script is not executable.')
    else:
        print('Script is executable')
        plate = state.get_nodes_by_attr('class_name', 'plate')
        if len(plate) > 0:
            print("plate states are:", plate[0].states)
        
        chars = state.get_nodes_by_attr('class_name', 'character')
        if len(chars) > 0:
            char = chars[0]
            print("Character holds:")
            print_node_names(state.get_nodes_from(char, Relation.HOLDS_RH))
            print_node_names(state.get_nodes_from(char, Relation.HOLDS_LH))
            print("Character is on:")
            print_node_names(state.get_nodes_from(char, Relation.ON))
            print("Character is in:")
            print_node_names(state.get_nodes_from(char, Relation.INSIDE))
            print("Character states are:", char.states)


if __name__ == '__main__':
    run()
    