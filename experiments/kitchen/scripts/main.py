# from env_kitchen import Agent,KitchenEnvironment
import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/evaluation/action_sequence/scripts')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
from virtualhome_env import VHAgent,VirtualhomeEnvironment



def main(goal,additional_information,task):
    init_path="combined_generated.cdl"
    # if task=='kitchen':
    #     env=KitchenEnvironment(init_path)
    #     agent=Agent(init_path)
    if task=='virtualhome':
        env=VirtualhomeEnvironment(init_path)
        agent=VHAgent(init_path)
    # agent.reset_goal(goal,additional_information,First_time=True)#ini a GR
    while True:
        action,plan = agent.act() #Planning    
        # action=ACTION('walk_executor')
        if action is None:
            agent.reset_goal(goal,additional_information,First_time=True)
            continue #Planning failed -> reset goal base on current state
        print('Action:', action)
        observation = env.step(action) #Execute action
        knowledge=agent.updates(observation) #Update agent's state

if __name__ == '__main__':
    goal="make a sandwich"
    additional_information="Clean all the ingradients before cooking. I want to add some cheese, bacon and tomato in the sandwich."
    task='virtualhome'
    main(goal,additional_information,task)