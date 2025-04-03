import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import matplotlib as mpl

# 设置全局字体样式
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 16,
    "axes.labelsize": 18,
    "axes.titlesize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.titleweight": "bold",
})

# 读取类别信息
with open('Category_abl.json', 'r') as f:
    categories = json.load(f)

# 读取任务-场景对数据
with open('task_scene_counts.json', 'r') as f:
    task_scene_counts = json.load(f)

# 读取原始动作统计以获取关键动作信息
with open('action_counts.json', 'r') as f:
    action_stats = json.load(f)

# 创建一个字典来存储每个类别的动作数量
category_actions = defaultdict(list)

# 对每个类别
for category_name, task_paths in categories.items():
    # 对每个任务路径
    for task_path in task_paths:
        # 提取任务名称（去掉路径和.txt）
        task_name = '/'.join(task_path.split('/')[-2:]).replace('.txt', '')
        
        # 对每个场景
        for scene_num in range(3):
            task_scene_key = f"{task_name}_scene{scene_num}"
            if task_scene_key in task_scene_counts:
                # 获取基础动作数量
                count = task_scene_counts[task_scene_key]
                
                # 获取该任务的关键动作信息
                task_info = None
                for cat in action_stats.values():
                    if task_name in cat:
                        task_info = cat[task_name]
                        break
                
                # 计算加权后的动作数量
                if task_info and 'Key Actions' in task_info and any(task_info['Key Actions']):
                    key_actions = sum(task_info['Key Actions'])
                    weighted_count = count + key_actions
                else:
                    weighted_count = count
                
                category_actions[category_name].append(weighted_count)

# 创建图表
plt.figure(figsize=(12, 7))  # 进一步增大图表尺寸

# 准备数据
categories_to_plot = [cat for cat in categories.keys() if category_actions[cat]]
data = [category_actions[cat] for cat in categories_to_plot]
labels = [cat.replace('novel_task', 'ambiguous').replace('_', '-') for cat in categories_to_plot]  # 替换novel_task为ambiguous

# 设置专业的配色方案
colors = ['#4878D0', '#EE854A', '#6ACC64', '#D65F5F', '#956CB4']

# 创建箱线图
box_plot = plt.boxplot(data, 
                      labels=labels, 
                      patch_artist=True,
                      medianprops=dict(color="black", linewidth=2),
                      flierprops=dict(marker='o', markerfacecolor='gray', markersize=5, alpha=0.5),
                      boxprops=dict(linewidth=2),
                      whiskerprops=dict(linewidth=2),
                      capprops=dict(linewidth=2))

# 设置箱体颜色
for patch, color in zip(box_plot['boxes'], colors[:len(data)]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# 添加数据点（以散点形式）
for i, d in enumerate(data, 1):
    # 添加抖动以更好地显示分布
    x = np.random.normal(i, 0.04, size=len(d))
    plt.plot(x, d, 'o', alpha=0.3, color='black', markersize=4)

# 设置图表标题和标签
plt.title('Distribution of Action Counts by Category', pad=10, fontsize=20, fontweight='bold')
plt.xlabel('Category', labelpad=10, fontsize=18, fontweight='bold')
plt.ylabel('Number of Actions', labelpad=10, fontsize=18, fontweight='bold')

# 添加网格线
plt.grid(True, axis='y', linestyle='--', alpha=0.3)

# 计算并显示每个类别的统计信息
stats_text = ""
for i, category in enumerate(categories_to_plot):
    actions = category_actions[category]
    category_name = category.replace('novel_task', 'ambiguous').replace('_', '-')
    stats_text += f"{category_name}:\n"
    stats_text += f"μ = {np.mean(actions):.1f}\n"
    stats_text += f"σ = {np.std(actions):.1f}\n"
    stats_text += f"n = {len(actions)}\n\n"

# 在图表上添加统计信息
plt.text(1.25, 0.98, stats_text,
         transform=plt.gca().transAxes,
         verticalalignment='top',
         horizontalalignment='left',
         fontsize=14,
         fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.5', 
                  facecolor='white', 
                  edgecolor='gray',
                  alpha=0.9))

# 调整布局以适应统计信息和图例
plt.subplots_adjust(right=0.85)

# 设置y轴范围，留出一些空间
plt.ylim(bottom=-5)

# 保存高质量图表
plt.savefig('category_action_distribution.pdf', 
            dpi=300, 
            bbox_inches='tight',
            format='pdf')

# 同时保存PNG版本
plt.savefig('category_action_distribution.png', 
            dpi=300, 
            bbox_inches='tight')
plt.close()

# 打印统计信息
print("Category Statistics:")
print("-" * 50)
for category in categories_to_plot:
    actions = category_actions[category]
    print(f"\n{category.replace('_', '-')}:")
    print(f"  Number of task-scene pairs: {len(actions)}")
    print(f"  Mean actions: {np.mean(actions):.1f}")
    print(f"  Median actions: {np.median(actions):.1f}")
    print(f"  Max actions: {max(actions)}")
    print(f"  Min actions: {min(actions)}")
    print(f"  Standard deviation: {np.std(actions):.1f}") 