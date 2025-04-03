import matplotlib.pyplot as plt
import numpy as np

# 数据
difficulties = ['Medium', 'Hard']
methods = ['LLMWOG', 'OurWOG', 'OurWG', 'Ours(continual)']
success_rates = [
    [0.60, 0.75, 0.80, 0.87],  # Medium difficulty
    [0.40, 0.55, 0.61, 0.72],  # Hard difficulty
]

# 颜色列表，给每个方法指定不同颜色
colors = ['#4682b4', '#ff6f61', '#6b8e23', '#ffcc00']

# 每组的宽度和间距设置
bar_width = 0.22  # 减小柱子的宽度
index = np.arange(len(difficulties))

# 创建柱状图
plt.figure(figsize=(4, 8))  # 调整宽高比为更窄更高

for i, method in enumerate(methods):
    # 为每个方法绘制柱状图
    bars = plt.bar(index + i * bar_width, [success_rates[j][i] for j in range(len(difficulties))],
            bar_width, label=method, color=colors[i], edgecolor='black', linewidth=1.5)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval-0.1, f'{yval:.2f}', ha='center', va='bottom', fontsize=20, color='black')

# 添加标题和标签
# plt.title('Success Rate of Different Methods for Various Difficulty Levels', fontsize=16, fontweight='bold')
plt.xlabel('Difficulty', fontsize=20)
plt.ylabel('Success Rate', fontsize=20)

# 设置刻度和标签
plt.xticks(index + bar_width * (len(methods) - 1) / 2, difficulties, fontsize=18)
plt.yticks(fontsize=18)

# 显示网格
plt.grid(axis='y', linestyle='--', alpha=0.7, color='gray')

# 添加图例，位置为左下角
legend = plt.legend(title='Methods', title_fontsize=20, fontsize=20, 
                   loc='lower left', bbox_to_anchor=(0.02, 0.02),
                   frameon=True, fancybox=True, shadow=True)
legend.get_frame().set_alpha(0.9)

# 美化布局
plt.tight_layout()

# 显示图表
plt.show()
