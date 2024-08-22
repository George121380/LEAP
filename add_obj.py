import json

name_set=set()
output_file_path='add.txt'
with open('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/resources/class_name_equivalence.json', 'r') as f:
    name_equivalence = json.load(f)
for name in name_equivalence:
    name_set.add(name)
    for name_ in name_equivalence[name]:
        name_set.add(name_)

with open('plus.txt', 'r') as f:
    for line in f:
        line=line.strip()
        if line in name_set:
            continue
        else:
            name_set.add(line)

content=''
for name in name_set:
    print(name)
    content+=f'feature is_{name}(x:item)\n'




with open(output_file_path, 'w') as f:
    f.write(content)