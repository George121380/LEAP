# task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    task_dict_dir = "/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/resources/task_state_LTL_formula_accurate.json"
    helm_prompt_path = "/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/evaluation/action_sequence/prompts/helm_prompts.json"
    scene_id = f"scene_{scenegraph_id}"
    task_dict = json.load(open(task_dict_dir, "r"))
    task_dict = task_dict[scene_id]
        
    exploration_content = ""
    for task_name, task_dicts in task_dict.items():
        print(f"CURRENT TASK IS {task_name}!")
        for file_id, task_goal_dict in task_dicts.items():
            if file_id!='27_2':
                continue
            dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"
            init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph_id, file_id))
            