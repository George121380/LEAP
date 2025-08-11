import os
import matplotlib.pyplot as plt
import networkx as nx
import json
from collections import defaultdict

def read_task_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 解析任务文件
    task_info = {
        'name': '',
        'goal': '',
        'guidance': '',
        'logic': '',
        'behaviors': [],
        'states': []
    }
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('Task name:'):
            task_info['name'] = line.replace('Task name:', '').strip()
        elif line.startswith('Goal:'):
            task_info['goal'] = line.replace('Goal:', '').strip()
        elif line.startswith('Guidance:'):
            task_info['guidance'] = line.replace('Guidance:', '').strip()
        elif line.startswith('Logic:'):
            task_info['logic'] = line.replace('Logic:', '').strip()
        elif line.startswith('S') and '_Actions:' in line:
            task_info['states'].append(line.strip())
        elif line.startswith('behavior'):
            task_info['behaviors'].append(line.strip())
    
    return task_info

def create_task_design_graph(task_info):
    G = nx.DiGraph()
    
    # 添加主节点
    G.add_node('Task', pos=(0, 0))
    G.add_node('Goal', pos=(0, 1))
    G.add_node('Guidance', pos=(0, -1))
    G.add_node('Logic', pos=(1, 0))
    
    # 添加边
    G.add_edge('Task', 'Goal')
    G.add_edge('Task', 'Guidance')
    G.add_edge('Task', 'Logic')
    
    # 添加行为节点
    for i, behavior in enumerate(task_info['behaviors']):
        behavior_name = behavior.split('(')[0].strip()
        G.add_node(behavior_name, pos=(2, i))
        G.add_edge('Logic', behavior_name)
    
    # 添加状态节点
    for i, state in enumerate(task_info['states']):
        state_name = state.split('_Actions:')[0].strip()
        G.add_node(state_name, pos=(-1, i))
        G.add_edge('Task', state_name)
    
    return G

def visualize_task_design(task_info, output_path):
    plt.figure(figsize=(12, 8))
    G = create_task_design_graph(task_info)
    
    # 获取节点位置
    pos = nx.get_node_attributes(G, 'pos')
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=2000, alpha=0.7)
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                          arrows=True, arrowsize=20)
    
    # 添加标签
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    # 添加标题
    plt.title(f"Task Design: {task_info['name']}", pad=20)
    
    # 保存图片
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建任务文件路径
    task_file = os.path.join(os.path.dirname(current_dir), 'dataset', 'Cook_some_food', 'g1.txt')
    output_path = os.path.join(current_dir, 'task_design_visualization.png')
    
    # 读取任务信息
    task_info = read_task_file(task_file)
    
    # 生成可视化
    visualize_task_design(task_info, output_path)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    main() 