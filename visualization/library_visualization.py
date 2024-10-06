import json
source_path='experiments/virtualhome/resources/library_backup.json'
visualization_path='visualization/library_visualization.txt'

behavior_data=json.load(open(source_path))

with open(visualization_path, 'w', encoding='utf-8') as txt_file:
    for category, behaviors in behavior_data.items():
        txt_file.write(f"{category}:\n")
        for behavior in behaviors:
            txt_file.write(behavior['cdl'].replace("\\n", "\n"))
            txt_file.write("\n\n")