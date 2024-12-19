# To-Do:

- [ ] Library testing -> Provide the whole library as context (do not allow calling)/ RAG / Add previous behavior into domain
- [ ] Third scene
- [ ] Give size properties to more objects

# Debug:
- [ ] Name Conflict while planning (obj_name_cdl==instance_name)
- [ ] Annotation for has_water "or"->"+" 





Improve auto debugger:

case1: exist as bind
if exists sink: item : is_sink(sink):
            achieve close_char(char, sink)
refer to: /Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/log/epoch_20241201_215307/records/Clean_the_bathroom_g2_task_log.txt


case2
def can_control_dvd_player(remote_control: item, dvd_player: item):
    # Determine if remote control can control the specified DVD player
    symbol can_control = exists function: item : is_remote_control(remote_control) and close(remote_control, dvd_player)
    return can_control

EXP还有bug
