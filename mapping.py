import os
import hashlib
import json

# 计算文件的哈希值，使用SHA256
def get_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        # 以二进制模式读取文件并计算哈希
        while chunk := file.read(8192):  # 分块读取文件，避免内存溢出
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# 获取指定文件夹中所有的txt文件路径及其内容的哈希值
def get_txt_files_with_hash(folder_path):
    txt_files = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                relative_path = os.path.relpath(root, folder_path)
                file_path = os.path.join(relative_path, file)
                file_hash = get_file_hash(os.path.join(root, file))  # 获取文件内容的哈希值
                txt_files[file_hash] = file_path  # 将哈希值作为字典的键
    return txt_files

# 生成mapping.json
def generate_mapping_json(original_folder, current_folder, output_json_path):
    # 获取原始路径和当前路径下所有txt文件的哈希映射
    original_files = get_txt_files_with_hash(original_folder)
    current_files = get_txt_files_with_hash(current_folder)
    
    # 创建一个字典来存储映射关系
    mapping = {}
    
    for current_hash, current_path in current_files.items():
        # 检查原本路径下是否有相同哈希值的文件
        if current_hash in original_files:
            original_path = original_files[current_hash]
            # 保存映射关系
            mapping[os.path.join(current_folder, current_path)] = os.path.join(original_folder, original_path)
    
    # 将映射关系保存到JSON文件
    with open(output_json_path, 'w') as json_file:
        json.dump(mapping, json_file, indent=4)
        



if __name__ == '__main__':
    original_folder = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset'  # 原本文件夹路径
    current_folder = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/cooking'  # 当前文件夹路径
    output_json_path = 'mapping.json'  # 输出的JSON文件路径

    # 生成映射关系并保存到mapping.json
    generate_mapping_json(original_folder, current_folder, output_json_path)