# from env_kitchen import Agent,KitchenEnvironment
import sys

sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/VH_scripts')

from utils_eval import get_from_dataset


def get_edges_related_to_node(node_id,graph):
    related_edges=[]
    for edges in graph.get_edges():
        if node_id==edges['from_id'] or node_id==edges['to_id']:
            related_edges.append(edges)
    for edge in related_edges:
        edge['from_id']=graph.get_node(edge['from_id']).class_name+'_'+str(edge['from_id'])
        edge['to_id']=graph.get_node(edge['to_id']).class_name+'_'+str(edge['to_id'])
    return related_edges

def load_scene(scene_idx,scenegraph=1):

    dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"
    file_id=scene_idx
    init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph, file_id))
    related_edges=get_edges_related_to_node(1000,init_scene_graph)
    return related_edges

if __name__=='__main__':
    scene_idx='469_2'
    scenegraph=1
    goal,additional_information,classes,init_scene_graph=load_scene(scene_idx,scenegraph)    