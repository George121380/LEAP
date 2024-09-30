import json

# 读取JSON文件
with open('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/resources/library_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 打开txt文件准备写入
with open('output_file.txt', 'w', encoding='utf-8') as txt_file:
    # 遍历数据并写入每一项
    for category, behaviors in data.items():
        txt_file.write(f"{category}:\n")
        for behavior in behaviors:
            txt_file.write(behavior['cdl'].replace("\\n", "\n"))
            txt_file.write("\n\n")

print("JSON内容已成功转换为TXT文件。")
