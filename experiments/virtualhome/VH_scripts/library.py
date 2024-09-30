import json
class behavior_library:
    def __init__(self):
        self.source_path='experiments/virtualhome/resources/library_data.json'
        self.behavior_data=json.load(open(self.source_path, "r"))
        self.visualization_path='experiments/virtualhome/resources/library_visualization.txt'

    def save_library(self):
        with open(self.source_path, "w") as file:
            json.dump(self.behavior_data, file)
        with open(self.visualization_path, 'w', encoding='utf-8') as txt_file:
            for category, behaviors in self.behavior_data.items():
                txt_file.write(f"{category}:\n")
                for behavior in behaviors:
                    txt_file.write(behavior['cdl'].replace("\\n", "\n"))
                    txt_file.write("\n\n")
    
    def parse_goal_representation(self,goal_representation:str):
        """
        Args:
            goal_representation: A group of behaviors

        Returns:
            definitions: A list of functions
            behaviors: A list of behavior definitions
        """
        definitions = []
        behaviors = []
        current_block = []
        current_type = None
        for line in goal_representation.splitlines():
            stripped_line = line.strip()

            # Detect the start of a new function definition
            if stripped_line.startswith("def"):
                if current_block:
                    if current_type == "def":
                        definitions.append("\n".join(current_block))
                    elif current_type == "behavior":
                        behaviors.append("\n".join(current_block))
                current_block = [line]
                current_type = "def"
            # Detect the start of a new behavior definition
            elif stripped_line.startswith("behavior"):
                if current_block:
                    if current_type == "def":
                        definitions.append("\n".join(current_block))
                    elif current_type == "behavior":
                        behaviors.append("\n".join(current_block))
                current_block = [line]
                current_type = "behavior"
            else:
                current_block.append(line)

        # Add the last block of code
        if current_block:
            if current_type == "def":
                definitions.append("\n".join(current_block))
            elif current_type == "behavior":
                behaviors.append("\n".join(current_block))

        return definitions, behaviors

    def lift(self,task_name:str,source_sub_task:str,behavior_description:str,behavior_cdl:str):
        """
        Args:
            task_name: The task name that the behavior is associated with
            source_sub_task: where the behavior is created
            behavior_description: the description of the behavior
            behavior_cdl: cdl representation for this behavior
        """
        if task_name in self.behavior_data:
            self.behavior_data[task_name].append({'usage_description':behavior_description,'cdl':behavior_cdl,'source_sub_task':source_sub_task})
        else:
            self.behavior_data[task_name]=[{'usage_description':behavior_description,'cdl':behavior_cdl,'source_sub_task':source_sub_task}]
        
        self.save_library()

    def download_behaviors(self):
        pass

    def lift_group(self,task_name:str,source_sub_task:str,goal_representation:str):
        """
        Args:
            task_name: The task name that the behavior is associated with
            source_sub_task: where the behavior is created
            goal_representation: A group of behaviors
        """
        definitions, behaviors = self.parse_goal_representation(goal_representation)
        for behavior in behaviors:
            if not '__goal__'in behavior:
                behavior_description = ''
                self.lift(task_name,source_sub_task,behavior_description,behavior)

    def delete(self,task_name,behavior_description):
        """
        Args:
            task_name: The task name that the behavior is associated with
            behavior_description: the description of the behavior
        """
        for i in range(len(self.behavior_data[task_name])):
            if self.behavior_data[task_name][i]['usage_description']==behavior_description:
                self.behavior_data[task_name].pop(i)
                break
        
        self.save_library()
        