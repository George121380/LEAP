import matplotlib.pyplot as plt
import numpy as np
import json
import os

# 读取类别数据
with open('Category.json', 'r') as f:
    categories = json.load(f)

# 统计每个类别的任务数量
category_names = list(categories.keys())
task_counts = [len(tasks) for tasks in categories.values()]

# 设置颜色
colors = ['#ff6f61', '#6b8e23', '#4682b4', '#ffcc00']

# 创建图表
plt.figure(figsize=(6, 4))

# 创建柱状图
bars = plt.bar(category_names, task_counts, color=colors, edgecolor='black', linewidth=1.5)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom', fontsize=14)

# 设置标题和标签
plt.title('Task Distribution Across Categories', fontsize=16, pad=20)
plt.xlabel('Category', fontsize=14)
plt.ylabel('Number of Tasks', fontsize=14)

# 设置刻度标签
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# 添加网格线
plt.grid(axis='y', linestyle='--', alpha=0.7, color='gray')

# 调整布局
plt.tight_layout()

# 显示图表
plt.show()

# 存储所有任务的goal信息
task_goals = {}

for category, tasks in categories.items():
    # 提取任务名称（去掉路径和.txt后缀）
    task_names = []
    for task in tasks:
        task_name = task.split('/')[-1].replace('.txt', '')
        task_names.append(task_name)
        
        # 读取任务文件内容
        try:
            with open(task, 'r') as f:
                content = f.read()
                # 提取goal信息
                if 'goal:' in content.lower():
                    goal_start = content.lower().find('goal:')
                    goal_end = content.find('\n', goal_start)
                    if goal_end == -1:
                        goal_end = len(content)
                    goal = content[goal_start+5:goal_end].strip()
                    task_goals[task_name] = goal
                else:
                    task_goals[task_name] = "No goal found"
        except Exception as e:
            task_goals[task_name] = f"Error reading file: {str(e)}"

# 创建LaTeX文件
with open('task_tables.tex', 'w') as f:
    # 写入第一个表格
    f.write("\\begin{table}[htbp]\n")
    f.write("\\centering\n")
    f.write("\\caption{Task Distribution Across Categories}\n")
    f.write("\\begin{tabular}{l|l}\n")
    f.write("\\hline\n")
    f.write("\\textbf{Category} & \\textbf{Tasks} \\\\\n")
    f.write("\\hline\n")

    for category, tasks in categories.items():
        # 提取任务名称（去掉路径和.txt后缀）
        task_names = [task.split('/')[-1].replace('.txt', '') for task in tasks]
        # 将任务名称用逗号分隔
        tasks_str = ', '.join(task_names)
        # 将类别名首字母大写
        category_name = category.capitalize()
        # 输出LaTeX行
        f.write(f"{category_name} & {tasks_str} \\\\\n")

    f.write("\\hline\n")
    f.write("\\end{tabular}\n")
    f.write("\\label{tab:task_categories}\n")
    f.write("\\end{table}\n\n")

    # 写入第二个表格
    f.write("\\begin{table}[htbp]\n")
    f.write("\\centering\n")
    f.write("\\caption{Task Goals by Category}\n")
    f.write("\\begin{tabular}{l|l|l}\n")
    f.write("\\hline\n")
    f.write("\\textbf{Category} & \\textbf{Task} & \\textbf{Goal} \\\\\n")
    f.write("\\hline\n")

    for category, tasks in categories.items():
        category_name = category.capitalize()
        first_row = True
        for task in tasks:
            task_name = task.split('/')[-1].replace('.txt', '')
            goal = task_goals.get(task_name, "No goal found")
            if first_row:
                f.write(f"{category_name} & {task_name} & {goal} \\\\\n")
                first_row = False
            else:
                f.write(f" & {task_name} & {goal} \\\\\n")

    f.write("\\hline\n")
    f.write("\\end{tabular}\n")
    f.write("\\label{tab:task_goals}\n")
    f.write("\\end{table}\n")

print("LaTeX tables have been saved to 'task_tables.tex'")

# 打印详细统计信息
print("\nDetailed Statistics:")
print("-" * 40)
for category, tasks in categories.items():
    print(f"{category.capitalize()}: {len(tasks)} tasks")
    # 统计每个类别中的具体任务类型
    task_types = set()
    for task in tasks:
        task_type = task.split('/')[-2]  # 获取任务类型
        task_types.add(task_type)
    print(f"  Task types: {', '.join(sorted(task_types))}")
    print("-" * 40) 