#!/usr/bin/env python3
"""
Script to organize task information from txt files into a structured JSON format.
This script reads all task files from the dataset directory and extracts:
- Task name
- Goal
- Guidance
- Category (from Category.json)
"""

import os
import json
import re
from pathlib import Path

def parse_task_file(file_path):
    """
    Parse a single task file and extract Task name, Goal, and Guidance.
    
    Args:
        file_path (str): Path to the task file
        
    Returns:
        dict: Dictionary containing task information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Task name
        task_name_match = re.search(r'Task name:\s*(.+)', content)
        task_name = task_name_match.group(1).strip() if task_name_match else ""
        
        # Extract Goal
        goal_match = re.search(r'Goal:\s*(.+)', content)
        goal = goal_match.group(1).strip() if goal_match else ""
        
        # Extract Guidance
        guidance_match = re.search(r'Guidance:\s*(.+)', content)
        guidance = guidance_match.group(1).strip() if guidance_match else ""
        
        return {
            "task_name": task_name,
            "goal": goal,
            "guidance": guidance
        }
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def load_category_mapping(category_file):
    """
    Load category mapping from Category.json file.
    
    Args:
        category_file (str): Path to Category.json file
        
    Returns:
        dict: Mapping from file path to category
    """
    try:
        with open(category_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        # Create reverse mapping: file_path -> category
        file_to_category = {}
        for category, file_list in categories.items():
            for file_path in file_list:
                file_to_category[file_path] = category
        
        return file_to_category
    except Exception as e:
        print(f"Error loading category file {category_file}: {e}")
        return {}

def organize_tasks():
    """
    Main function to organize all tasks into a structured JSON format.
    """
    # Define paths - 使用绝对路径
    script_dir = Path(__file__).parent.resolve()  # scripts目录
    cdl_dataset_dir = script_dir.parent  # cdl_dataset目录
    dataset_dir = cdl_dataset_dir / "dataset"  # dataset目录
    category_file = cdl_dataset_dir.parent / "Category.json"  # Category.json文件
    output_file = script_dir / "organized_tasks.json"
    
    print(f"Script directory: {script_dir}")
    print(f"CDL dataset directory: {cdl_dataset_dir}")
    print(f"Dataset directory: {dataset_dir}")
    print(f"Category file: {category_file}")
    print(f"Output file: {output_file}")
    
    # 检查路径是否存在
    if not dataset_dir.exists():
        print(f"Error: Dataset directory does not exist: {dataset_dir}")
        return
    
    if not category_file.exists():
        print(f"Error: Category file does not exist: {category_file}")
        return
    
    # Load category mapping
    file_to_category = load_category_mapping(category_file)
    
    # Initialize result structure
    organized_tasks = {
        "tasks": [],
        "summary": {
            "total_tasks": 0,
            "categories": {}
        }
    }
    
    # Process each task directory
    for task_dir in sorted(dataset_dir.iterdir()):
        if not task_dir.is_dir():
            continue
            
        print(f"Processing directory: {task_dir.name}")
        
        # Process each txt file in the task directory
        for txt_file in sorted(task_dir.glob("*.txt")):
            print(f"  Processing file: {txt_file.name}")
            
            # Parse task information
            task_info = parse_task_file(txt_file)
            if not task_info:
                continue
            
            # Determine category
            relative_path = f"cdl_dataset/dataset/{task_dir.name}/{txt_file.name}"
            category = file_to_category.get(relative_path, "unknown")
            
            # Create task entry
            task_entry = {
                "file_path": str(txt_file.relative_to(dataset_dir)),
                "task_name": task_info["task_name"],
                "goal": task_info["goal"],
                "guidance": task_info["guidance"],
                "category": category
            }
            
            organized_tasks["tasks"].append(task_entry)
            organized_tasks["summary"]["total_tasks"] += 1
            
            # Update category count
            if category not in organized_tasks["summary"]["categories"]:
                organized_tasks["summary"]["categories"][category] = 0
            organized_tasks["summary"]["categories"][category] += 1
    
    # Save organized tasks to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organized_tasks, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully saved organized tasks to: {output_file}")
        print(f"Total tasks processed: {organized_tasks['summary']['total_tasks']}")
        print("Category distribution:")
        for category, count in organized_tasks["summary"]["categories"].items():
            print(f"  {category}: {count}")
    except Exception as e:
        print(f"Error saving output file: {e}")

if __name__ == "__main__":
    organize_tasks() 