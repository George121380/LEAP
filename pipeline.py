import json
import sys
sys.path.append('../simulation')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation')
import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import *
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph
from evolving_graph.preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination
from evolving_graph.environment import *
from utils import get_nodes_information,construct_cdl,sampler,transform_plan
from Interpretation import goal_interpretation,refiner,feedbackloop,exploration
from solver import goal_solver
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from auto_debugger import auto_debug

def print_node_names(n_list):
    if len(n_list) > 0:
        print([n.class_name for n in n_list])
    
def remove_special_characters(input_string):
    allowed_characters = {',', ':', '(', ')', '_', '#', ' ', '\n','!=','=','[',']'}
    return ''.join(char for char in input_string if char.isalnum() or char in allowed_characters)

def virtualhome_run(graph_path,script_path,goal,additional_information,debug=False):
    #import objects and stats information from graph
    graph = utils.load_graph(graph_path)
    get_nodes_information(graph)
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(graph)
    construct_cdl(objects,states,relationships,properties,cat_statement)
    GTscript,brief_discription,introduction = read_script(script_path)
    #goal interpretation
    if debug:
        introduction=goal
    goal_int=goal_interpretation(introduction,additional_information,classes)
    goal_int=refiner(goal_int,additional_information,classes,goal_int)
    with open("generated.cdl", "r") as file:
        original_content = file.read()
    combined_content = original_content + "\n" + goal_int
    new_file_path = "combined_generated.cdl"
    with open(new_file_path, "w") as file:
        file.write(combined_content)
    
    print(f"Combined content saved to {new_file_path}")
    #planning
    planning_try_count = 0
    while planning_try_count < 5:
        try:
            plan=goal_solver(original_content + "\n" + goal_int)
            break
        except TransformationError as e:
            error_info=e.errors
            print("Error information: ",error_info)
            goal_int=auto_debug(error_info,original_content,goal_int,introduction,additional_information,classes)
            combined_content = original_content + "\n" + goal_int
            new_file_path = "combined_generated.cdl"
            with open(new_file_path, "w") as file:
                file.write(combined_content)

        
    if len(plan)==0:
        print('No plan found or the goal is already satisfied.')
        return
    plan=transform_plan(plan)
    script=Script(plan)
    #execution
    name_equivalence = utils.load_name_equivalence()
    executor = ScriptExecutor(graph, name_equivalence)
    state_enum = executor.find_solutions(script)
    state = next(state_enum, None)
    
    if state is None:
        print('Script is not executable.')
    else:
        print('Script is executable')
        dishwasher = state.get_node(81).states
        if len(dishwasher) > 0:
            print("dishwasher states are:", dishwasher)
        
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

def kitchen_goal_generation(goal,additional_information,objlist,loop,First_time):
    classes=objlist
    generate_time=0
    exploration_content=""
    while generate_time<5:
        try:
            

            goal_int=goal_interpretation(goal,additional_information,classes)
            goal_int=remove_special_characters(goal_int)
            # goal_int=refiner(goal_int,additional_information,classes,goal_int)
            if First_time:
                new_file_path = "combined_generated.cdl"
                with open("kitchen_problem_partial_ability.cdl", "r") as file:
                    original_content = file.read()
            if not First_time:
                new_file_path = "agent_internal_state.cdl"
                with open("agent_internal_state_only.cdl", "r") as file:
                    original_content = file
            combined_content = original_content + "\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            if exploration_content=="":
                exploration_content=exploration(goal,additional_information,new_file_path)
            exploration_content=remove_special_characters(exploration_content)
            combined_content=original_content+"\n"+"\n#goal_representation\n"+exploration_content+'\n\n' + goal_int+"\n#goal_representation_end\n"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            print(f"Combined content saved to {new_file_path}")
            #planning
            correct_time = 0
            while correct_time < 5:
                try:
                    plan=goal_solver(original_content + "\n" + goal_int)
                    if loop:
                        if len(plan)==0:
                            break
                        if len(plan)>0:
                            print('=' * 80)
                            print("goal representation before loop:")
                            print('=' * 80)
                            print(goal_int)
                            goal_int=feedbackloop(goal,additional_information,
                            classes,goal_int,plan[0])
                            with open(new_file_path, "w") as file:
                                    combined_content = original_content + "\n" + goal_int
                                    file.write(combined_content)
                            
                            # exploration_content=exploration(goal,additional_information,new_file_path)
                            # exploration_content=remove_special_characters(exploration_content)
                            combined_content=original_content+"\n"+"\n#goal_representation\n"+exploration_content+'\n\n' + goal_int+"\n#goal_representation_end\n"
                            with open(new_file_path, "w") as file:
                                file.write(combined_content)
                            plan_afterloop=goal_solver(original_content + "\n" + goal_int)
                            
                            if len(plan_afterloop)==0:
                                break
                            if len(plan_afterloop)>0:
                                print('=' * 80)
                                print("Plan found.")
                                print('=' * 80)
                                print("Goal representation:")
                                print(goal_int)
                                print('=' * 80)
                                
                                return plan_afterloop,goal_int
                    else:
                        return plan,exploration_content+'\n\n' + goal_int


                except TransformationError as e:
                    error_info=e.errors
                    print("Error information: ",error_info)
                    goal_int=auto_debug(error_info,original_content,goal_int,goal,additional_information,classes)
                    goal_int=remove_special_characters(goal_int)
                    combined_content=original_content+"\n"+"\n#goal_representation\n"+exploration_content+'\n\n' + goal_int+"\n#goal_representation_end\n"
                    with open(new_file_path, "w") as file:
                        file.write(combined_content)
                    correct_time+=1

        except:
            print("Error in generating plan, try again.")
            generate_time+=1

def pipeline(goal,additional_information,loop=False,First_time=False):
    classes=['tomato','egg','pan','stove','sink','bowl','oil','salt','pepper','faucet','fridge','knife','spatula','sugar','countertop','water','bread','onion','bacon','cheese','pot','noodles','chicken','garlic','ginger','vegetables','oven','plate','potato','beef','shrimp','cuttingboard']
    plan,goal_int=kitchen_goal_generation(goal,additional_information,classes,loop,First_time)
    return goal_int
    
if __name__ == '__main__':
    goal="Write an email"
    additional_information="I go to my bed room and sit on the chair and in front of me is my desktop computer and start writing an email."
    virtualhome_run