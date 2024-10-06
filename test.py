def find_behavior_from_library(goal_representation, behavior_from_library):
    """
    Args:
        goal_representation: The goal representation which may contain behavior definitions and calls.
        behavior_from_library: A dictionary containing behaviors and their metadata:
            - 'content': list of behavior definitions.
            - 'names': list of behavior names.
            - 'function_calls': list of dictionaries with keys 'behavior_name' and 'function_calls' (list of functions called by the behavior).
            - 'behavior_calls': list of dictionaries with keys 'behavior_name' and 'called_behaviors' (list of behaviors called by the behavior).
            - 'function_definitions': dictionary mapping function names to their definitions (if available).
    Returns:
        full_code: A string containing all necessary behavior and function definitions.
    """
    import re

    # Sets to keep track of behaviors and functions to be added
    behaviors_to_add = set()
    processed_behaviors = set()
    functions_to_add = set()
    processed_functions = set()
    
    # Initialize the output strings
    add_behaviors = ''
    add_functions = ''
    
    # Build a mapping from behavior names to their indices for quick lookup
    behavior_name_to_index = {name: idx for idx, name in enumerate(behavior_from_library['names'])}
    
    # First, parse the goal_representation to find behaviors that are already defined
    # Regex pattern to find behavior definitions in goal_representation
    behavior_pattern = r'behavior\s+(\w+)\s*\(.*?\):'
    defined_behaviors = set(re.findall(behavior_pattern, goal_representation))
    
    # Now, find behaviors in the goal_representation that match behaviors in the library
    for behavior_name in behavior_from_library['names']:
        if behavior_name in goal_representation:
            behaviors_to_add.add(behavior_name)
    
    # Remove behaviors that are already defined in goal_representation
    behaviors_to_add -= defined_behaviors
    
    # Function to process behaviors recursively
    def process_behavior(behavior_name):
        if behavior_name in processed_behaviors or behavior_name in defined_behaviors:
            return
        processed_behaviors.add(behavior_name)
        
        idx = behavior_name_to_index.get(behavior_name)
        if idx is None:
            return  # Behavior not found in the library
        
        # Add behavior content
        nonlocal add_behaviors
        add_behaviors += behavior_from_library['content'][idx] + '\n'
        
        # Add functions called by this behavior
        called_functions = behavior_from_library['function_calls'][idx]['function_calls']
        for func_name in called_functions:
            functions_to_add.add(func_name)
        
        # Recursively process behaviors called by this behavior
        called_behaviors = behavior_from_library['behavior_calls'][idx]['called_behaviors']
        for called_behavior in called_behaviors:
            process_behavior(called_behavior)
    
    # Process all behaviors that need to be added
    for behavior_name in behaviors_to_add:
        process_behavior(behavior_name)
    
    # Now process functions
    function_pattern = r'function\s+(\w+)\s*\(.*?\):'
    defined_functions = set(re.findall(function_pattern, goal_representation))
    for func_name in functions_to_add:
        if func_name in processed_functions or func_name in defined_functions:
            continue
        processed_functions.add(func_name)
        # Add function definition from library
        func_definition = behavior_from_library['function_definitions'].get(func_name)
        if func_definition:
            add_functions += func_definition + '\n'
    
    # Combine functions and behaviors
    full_code = add_functions + add_behaviors
    return full_code

if __name__=='__main__':
    goal_representation = """
    behavior FindTableWithFood:
        Find a table with food on it.
    
    behavior PutFoodInStorage:
        Put the food in the appropriate storage locations.
    """
    behavior_from_library = {
        'content': [
            "behavior FindTableWithFood:\n    Find the table with food on it.\n",
            "behavior PutFoodInStorage:\n    Put the food in the right storage locations.\n",
        ],
        'names': ['FindTableWithFood', 'PutFoodInStorage'],
        'function_calls': [
            {'behavior_name': 'FindTableWithFood', 'function_calls': []},
            {'behavior_name': 'PutFoodInStorage', 'function_calls': []},
        ],
        'behavior_calls': [
            {'behavior_name': 'FindTableWithFood', 'called_behaviors': []},
            {'behavior_name': 'PutFoodInStorage', 'called_behaviors': []},
        ],
        'function_definitions': {}
    }
    full_code = find_behavior_from_library(goal_representation, behavior_from_library)
    print(full_code)