import json
import matplotlib.pyplot as plt
import numpy as np

# 读取任务-场景对数据
with open('task_scene_counts.json', 'r') as f:
    task_scene_counts = json.load(f)

# 读取原始动作统计以获取关键动作信息
with open('action_counts.json', 'r') as f:
    action_stats = json.load(f)

# 创建一个字典来存储加权后的动作数量
weighted_counts = {}

# 计算加权后的动作数量
for task_scene, count in task_scene_counts.items():
    # 从task_scene中提取任务名称
    task_name = task_scene.split('_scene')[0]
    
    # 获取该任务的关键动作信息
    task_info = None
    for category in action_stats.values():
        if task_name in category:
            task_info = category[task_name]
            break
    
    if task_info and 'Key Actions' in task_info and any(task_info['Key Actions']):
        # 如果有关键动作，将关键动作数量乘以2
        key_actions = sum(task_info['Key Actions'])
        weighted_count = count + key_actions  # 原始数量加上额外的一倍关键动作
    else:
        weighted_count = count
    
    weighted_counts[task_scene] = weighted_count

# 提取所有加权后的动作数量
weighted_action_counts = list(weighted_counts.values())

# 创建直方图
plt.figure(figsize=(12, 6))
plt.hist(weighted_action_counts, bins=30, edgecolor='black', color='skyblue', alpha=0.7)

# 设置图表标题和标签
plt.title('Distribution of Weighted Action Counts (Key Actions × 2)', fontsize=14)
plt.xlabel('Number of Actions (Key Actions Weighted)', fontsize=12)
plt.ylabel('Number of Task-Scene Pairs', fontsize=12)

# 添加网格线
plt.grid(True, linestyle='--', alpha=0.7)

# 计算并显示一些统计信息
mean_actions = np.mean(weighted_action_counts)
median_actions = np.median(weighted_action_counts)
max_actions = max(weighted_action_counts)
min_actions = min(weighted_action_counts)

# 在图表上添加统计信息
stats_text = f'Mean: {mean_actions:.1f}\nMedian: {median_actions:.1f}\nMax: {max_actions}\nMin: {min_actions}'
plt.text(0.95, 0.95, stats_text,
         transform=plt.gca().transAxes,
         verticalalignment='top',
         horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 保存图表
plt.savefig('weighted_action_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 打印统计信息
print(f"Total number of task-scene pairs: {len(weighted_action_counts)}")
print(f"Mean number of weighted actions: {mean_actions:.1f}")
print(f"Median number of weighted actions: {median_actions:.1f}")
print(f"Maximum number of weighted actions: {max_actions}")
print(f"Minimum number of weighted actions: {min_actions}")
print(f"Standard deviation: {np.std(weighted_action_counts):.1f}")

# 保存加权后的数据
with open('weighted_task_scene_counts.json', 'w') as f:
    json.dump(weighted_counts, f, indent=4) 