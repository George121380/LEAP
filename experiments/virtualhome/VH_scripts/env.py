import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
from execution import ScriptExecutor
from utils import load_name_equivalence
from utils_eval import transform_action,check_unexplorable
from scripts import *



class VH_Env:
    def __init__(self, graph):
        self.graph = graph
        self.name_equivalence = load_name_equivalence()
        self.scripts_index=1
        self.char=None
        self.char_room=None

    def check_related_edges(self,node_id):
        related_edges=[]
        for edges in self.graph.get_edges():
            if node_id==edges['from_id'] or node_id==edges['to_id']:
                related_edges.append(edges)
        print(related_edges)
        return related_edges

    def find_room(self,node_id):
        for edge in self.graph.get_edges():
            if edge['from_id']==node_id and edge['relation_type']=='INSIDE':
                return f"{self.graph.get_node(edge['to_id']).class_name}_{edge['to_id']}"
        return None

    def step(self, action):
        exp_flag=True
        exp_target=None
        exp_loc=None
        observation={}

        if action.name!='exp':
            exp_flag=False
            self.executor = ScriptExecutor(self.graph, self.name_equivalence)
            # if 'grab' in action.name.lower():
            #     print('debug')

            action=transform_action(action,self.scripts_index)
            self.scripts_index+=1
            script=Script(action)
            state_enum = self.executor.find_solutions(script)
            state = next(state_enum, None)
            if state is None:
                print('Script is not executable.')
                raise Exception('Script is not executable.')
            else:
                print('Script is executable')
            self.char=state.get_nodes_by_attr('class_name', 'character')[0]

            for edge in state._new_edges_from:
                from_id=edge[0]
                relation=edge[1]
                to_id_list=list(state._new_edges_from[edge])
                if len(to_id_list)==0:
                    continue
                for to_id in to_id_list:
                    self.graph.add_edge(state._graph.get_node(from_id), relation, state._graph.get_node(to_id))
                    
            for edge in state._removed_edges_from:
                from_id=edge[0]
                relation=edge[1]
                to_id_list=list(state._removed_edges_from[edge])
                if len(to_id_list)==0:
                    continue
                for to_id in to_id_list:
                    self.graph.delete_edge(state._graph.get_node(from_id), relation, state._graph.get_node(to_id))

            for node in state._new_nodes:
                self.graph._node_map[node].states=state._new_nodes[node].states
        else:
            exp_target=action.arguments[0].name
            exp_loc=action.arguments[1].name
            ###obs###
        
        self.char_room=self.find_room(self.char.id)
            
        around_ids=[]
        state_updates={}
        state_check_set=set()
        relations_updates=[]
        known_updates=[]
        for edge in self.graph.get_edges():
            if edge['from_id']==self.char.id:
                add_relation={}
                add_state={}
                from_name='char'
                to_name=f"{self.graph.get_node(edge['to_id']).class_name}_{edge['to_id']}"
                known_updates.append(to_name)
                if not check_unexplorable(to_name) and edge['to_id'] not in around_ids:
                    around_ids.append(edge['to_id'])

                add_relation['from_name']=from_name
                add_relation['to_name']=to_name
                add_relation['relation_type']=edge['relation_type']
                relations_updates.append(add_relation)
                to_obj=self.graph.get_node(edge['to_id'])
                add_state[to_name]=list(to_obj.states)
                state_updates.update(add_state)
                state_check_set.add(to_name)

        for edge in self.graph.get_edges():
            if (edge['to_id'] in around_ids) or (edge['from_id'] in around_ids):
                add_relation={}

                from_name=f"{self.graph.get_node(edge['from_id']).class_name}_{edge['from_id']}"
                if 'character' in from_name:
                    continue

                to_name=f"{self.graph.get_node(edge['to_id']).class_name}_{edge['to_id']}"
                if 'character' in to_name:
                    if edge['relation_type']!='ON':
                        continue
                    to_name='char'
                
                from_room=self.find_room(edge['from_id'])
                to_room=self.find_room(edge['to_id'])
                if from_room!=self.char_room or to_room!=self.char_room:
                    continue


                add_relation['from_name']=from_name
                add_relation['to_name']=to_name
                add_relation['relation_type']=edge['relation_type']

                relations_updates.append(add_relation)
                if from_name not in state_check_set:
                    add_state={}
                    add_state[from_name]=list(self.graph.get_node(edge['from_id']).states)
                    state_updates.update(add_state)
                    state_check_set.add(from_name)
                    known_updates.append(from_name)
                if to_name not in state_check_set:
                    add_state={}
                    add_state[to_name]=list(self.graph.get_node(edge['to_id']).states)
                    state_updates.update(add_state)
                    state_check_set.add(to_name)
                    known_updates.append(to_name)

        checked_name_list=[]
        for node_id in around_ids:
            checked_name=f"{self.graph.get_node(node_id).class_name}_{node_id}"
            checked_name_list.append(checked_name)

        observation['relations']=relations_updates
        observation['states']=state_updates
        observation['known']=known_updates
        observation['exp_flag']=exp_flag
        observation['exp_target']=exp_target
        observation['exp_loc']=exp_loc
        observation['checked']=checked_name_list

        return observation