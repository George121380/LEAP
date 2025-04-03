import json
import os
import glob

def get_max_key_state_actions(task_path, scene_files):
    """计算完成关键状态所需的最大动作数量"""
    max_actions = 0
    
    for scene_file in scene_files:
        try:
            with open(scene_file, 'r') as f:
                scene_data = json.load(f)
                if task_path in scene_data:  # 使用完整路径匹配
                    for key_states in scene_data[task_path].values():
                        # 计算当前关键状态组合的动作总数
                        current_sum = sum(key_states.values())
                        max_actions = max(max_actions, current_sum)
        except Exception as e:
            print(f"Error reading scene file {scene_file}: {str(e)}")
    
    return max_actions

def get_key_action_count(task_path):
    """计算关键动作数量"""
    try:
        with open(task_path, 'r') as f:
            content = f.read()
            # 查找所有场景的关键动作
            key_actions = [0, 0, 0]  # 初始化为3个场景的默认值
            has_key_actions = False
            for scene_num in range(3):  # 场景0,1,2
                scene_key = f"S{scene_num}_Actions:"
                if scene_key in content:
                    has_key_actions = True
                    # 提取该场景的关键动作
                    start_idx = content.find(scene_key) + len(scene_key)
                    end_idx = content.find('\n', start_idx)
                    if end_idx == -1:
                        end_idx = len(content)
                    actions = content[start_idx:end_idx].strip()
                    if actions:
                        key_actions[scene_num] = len(actions.split(','))
            
            return key_actions, has_key_actions
    except Exception as e:
        print(f"Error reading task file {task_path}: {str(e)}")
        return [0, 0, 0], False

def get_task_category(task_path):
    """根据任务路径确定其类别"""
    # 烹饪相关任务
    cooking_tasks = ['Cook_some_food', 'Make_coffee', 'Prepare_breakfast', 'Prepare_dinner', 'Drink']
    # 清洁相关任务
    cleaning_tasks = ['Clean_the_bathroom', 'Vacuum_the_living_room', 'Wash_dishes_with_dishwasher', 'Wash_windows']
    # 洗衣相关任务
    laundry_tasks = ['Iron_clothes', 'Wash_clothes']
    # 整理相关任务
    arrangement_tasks = ['Change_TV_channel', 'Listen_to_music', 'Pet_cat', 'Prepare_a_reading_space', 
                        'Put_groceries_in_Fridge', 'Turn_on_light', 'Write_an_email']
    
    # 从路径中提取任务类型
    task_type = task_path.split('/')[-2]
    
    if task_type in cooking_tasks:
        return 'cooking'
    elif task_type in cleaning_tasks:
        return 'cleaning'
    elif task_type in laundry_tasks:
        return 'laundry'
    elif task_type in arrangement_tasks:
        return 'arrangement'
    else:
        return None

# 场景文件路径
scene_files = [
    'cdl_dataset/scenes/diff_0.json',
    'cdl_dataset/scenes/diff_1.json',
    'cdl_dataset/scenes/diff_2.json'
]

# 创建结果数据结构
action_counts = {
    "cooking": {},
    "cleaning": {},
    "laundry": {},
    "arrangement": {}
}

# 创建任务-场景对的结果数据结构
task_scene_counts = {}

# 获取所有任务文件
all_tasks = glob.glob('cdl_dataset/dataset/**/g*.txt', recursive=True)
# 过滤掉包含bug的任务
all_tasks = [task for task in all_tasks if 'bug' not in task.lower()]

# 遍历每个任务
for task_path in all_tasks:
    # 获取任务类别
    category = get_task_category(task_path)
    if category is None:
        print(f"Warning: Cannot determine category for task {task_path}")
        continue
        
    task_name = os.path.join(task_path.split('/')[-2], task_path.split('/')[-1].replace('.txt', ''))
    
    # 获取关键状态动作数量
    key_state_actions = get_max_key_state_actions(task_path, scene_files)
    
    # 获取关键动作数量
    key_actions, has_key_actions = get_key_action_count(task_path)
    
    # 计算每个场景的总动作数量
    scene_totals = []
    for i in range(3):
        # 如果没有定义关键动作，只使用关键状态动作数量
        if not has_key_actions:
            total = key_state_actions
        else:
            total = key_state_actions + key_actions[i]
        scene_totals.append(total)
        
        # 添加到任务-场景对的结果中
        task_scene_key = f"{task_name}_scene{i}"
        task_scene_counts[task_scene_key] = total
    
    # 存储结果
    action_counts[category][task_name] = {
        'key_state_actions': key_state_actions,
        'key_actions': key_actions,
        'has_key_actions': has_key_actions,
        'scene_totals': scene_totals,
        'path': task_path
    }

# 保存分类结果到JSON文件
with open('action_counts.json', 'w') as f:
    json.dump(action_counts, f, indent=4)

# 保存任务-场景对结果到JSON文件
with open('task_scene_counts.json', 'w') as f:
    json.dump(task_scene_counts, f, indent=4)

print("Action counts have been saved to 'action_counts.json'")
print("Task-scene pair counts have been saved to 'task_scene_counts.json'")

# 打印统计信息
print("\nAction Count Statistics:")
print("-" * 60)
total_tasks = 0
total_actions = 0
tasks_with_key_actions = 0
tasks_without_key_actions = 0

for category, tasks in action_counts.items():
    print(f"\n{category.capitalize()}:")
    category_total = 0
    category_tasks_with_key_actions = 0
    for task_name, counts in sorted(tasks.items()):
        task_total = sum(counts['scene_totals'])
        category_total += task_total
        if counts['has_key_actions']:
            category_tasks_with_key_actions += 1
            tasks_with_key_actions += 1
        else:
            tasks_without_key_actions += 1
        print(f"  {task_name}:")
        print(f"    Path: {counts['path']}")
        print(f"    Key State Actions: {counts['key_state_actions']}")
        print(f"    Key Actions: {counts['key_actions']}")
        print(f"    Has Key Actions: {counts['has_key_actions']}")
        print(f"    Scene Totals: {counts['scene_totals']}")
    print(f"  Category Total: {category_total}")
    print(f"  Tasks with Key Actions: {category_tasks_with_key_actions}")
    print(f"  Tasks without Key Actions: {len(tasks) - category_tasks_with_key_actions}")
    total_tasks += len(tasks)
    total_actions += category_total

print("\nOverall Statistics:")
print(f"Total Tasks: {total_tasks}")
print(f"Tasks with Key Actions: {tasks_with_key_actions}")
print(f"Tasks without Key Actions: {tasks_without_key_actions}")
print(f"Total Actions Across All Scenes: {total_actions}")
print(f"Average Actions per Task: {total_actions/total_tasks:.2f}")
print(f"Total Task-Scene Pairs: {len(task_scene_counts)}") 