import json
from token_counter import calculate_library_data_average_length

def main():
    # Read the library data
    with open('main_results/openai_new/round7/overall/Action_libraryWG/library_data.json', 'r', encoding='utf-8') as f:
        library_data = json.load(f)
    
    # Calculate average lengths
    avg_subtask_length, avg_actions_length, total_tasks = calculate_library_data_average_length(library_data)
    
    # Print results
    print(f"Total number of tasks: {total_tasks}")
    print(f"Average source_sub_task length: {avg_subtask_length:.2f} characters")
    print(f"Average actions length: {avg_actions_length:.2f} characters")
    print(f"Average total length per task: {(avg_subtask_length + avg_actions_length):.2f} characters")

if __name__ == "__main__":
    main() 