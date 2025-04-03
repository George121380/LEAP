import json
import os

# 读取类别数据
with open('Category.json', 'r') as f:
    categories = json.load(f)

# 创建新的数据结构来存储任务内容
task_contents = {}

# 遍历每个类别
for category, tasks in categories.items():
    task_contents[category] = {}
    
    # 遍历每个任务文件
    for task_path in tasks:
        try:
            # 获取任务名称（去掉路径和.txt后缀）
            task_name = task_path.split('/')[-1].replace('.txt', '')
            
            # 读取任务文件内容
            with open(task_path, 'r') as f:
                content = f.read()
                
                # 提取goal信息
                goal = None
                if 'goal:' in content.lower():
                    goal_start = content.lower().find('goal:')
                    goal_end = content.find('\n', goal_start)
                    if goal_end == -1:
                        goal_end = len(content)
                    goal = content[goal_start+5:goal_end].strip()
                
                # 提取其他信息（可以根据需要添加更多字段）
                task_contents[category][task_name] = {
                    'path': task_path,
                    'goal': goal,
                    'full_content': content
                }
                
        except Exception as e:
            print(f"Error reading file {task_path}: {str(e)}")
            task_contents[category][task_name] = {
                'path': task_path,
                'error': str(e)
            }

# 将结果保存到新的JSON文件
with open('task_contents.json', 'w') as f:
    json.dump(task_contents, f, indent=4)

print("Task contents have been saved to 'task_contents.json'")

# 打印统计信息
print("\nTask Statistics:")
print("-" * 40)
for category, tasks in task_contents.items():
    print(f"{category.capitalize()}: {len(tasks)} tasks")
    print("-" * 40) 