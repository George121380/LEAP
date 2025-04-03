def estimate_token_count(text):
    """
    Estimate the number of tokens in a given text string based on character count and language.
    
    Args:
        text (str): The text to estimate tokens for
        
    Returns:
        int: Estimated number of tokens
    """
    if not text:
        return 0
        
    token_count = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # Chinese character range
            token_count += 1  # Chinese characters are typically 1 token each
        else:
            token_count += 0.25  # Other characters are typically 0.25 tokens each
            
    return int(token_count)

def calculate_string_length(text):
    """
    Calculate the length of a string while properly handling both Chinese and other characters.
    
    Args:
        text (str): The text to calculate length for
        
    Returns:
        int: The length of the text
    """
    if not text:
        return 0
        
    length = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # Chinese character range
            length += 1
        else:
            length += 1
            
    return length

def calculate_library_data_average_length(library_data):
    """
    Calculate the average length of source_sub_task and actions from a list of dictionaries containing library data.
    
    Args:
        library_data (list): List of dictionaries containing task data
        
    Returns:
        tuple: (average source_sub_task length, average actions length, total number of tasks)
    """
    if not library_data:
        return 0, 0, 0
        
    total_subtask_length = 0
    total_actions_length = 0
    total_tasks = len(library_data)
    
    for task in library_data:
        if 'source_sub_task' in task:
            total_subtask_length += calculate_string_length(task['source_sub_task'])
        if 'actions' in task:
            total_actions_length += calculate_string_length(task['actions'])
            
    avg_subtask_length = total_subtask_length / total_tasks if total_tasks > 0 else 0
    avg_actions_length = total_actions_length / total_tasks if total_tasks > 0 else 0
    
    return avg_subtask_length, avg_actions_length, total_tasks