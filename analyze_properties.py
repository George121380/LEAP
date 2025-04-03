import re
from collections import defaultdict

def analyze_properties(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有属性行
    property_lines = re.findall(r'(\w+)\[(.*?)\] = True', content)
    
    # 创建属性到物品种类的映射
    property_to_objects = defaultdict(set)
    
    # 处理每一行
    for prop, obj in property_lines:
        # 提取物品类型（去掉数字后缀）并替换下划线为空格
        obj_type = re.sub(r'\d+$', '', obj)
        obj_type = obj_type.replace('_', ' ').title()  # 将下划线替换为空格并首字母大写
        property_to_objects[prop].add(obj_type)
    
    # 生成LaTeX表格
    latex_table = "\\begin{longtable}{|>{\\raggedright\\arraybackslash}p{0.2\\textwidth}|>{\\raggedright\\arraybackslash}p{0.75\\textwidth}|}\n"
    latex_table += "\\hline\n"
    latex_table += "\\textbf{Property} & \\textbf{Object Types} \\\\\n"
    latex_table += "\\hline\n"
    latex_table += "\\endfirsthead\n\n"
    latex_table += "\\multicolumn{2}{l}{\\textit{Table continued}}\\\\ \\hline\n"
    latex_table += "\\textbf{Property} & \\textbf{Object Types} \\\\\n"
    latex_table += "\\hline\n"
    latex_table += "\\endhead\n\n"
    latex_table += "\\hline\n"
    latex_table += "\\endfoot\n\n"
    latex_table += "\\hline\n"
    latex_table += "\\endlastfoot\n\n"
    
    # 按属性名排序
    for prop in sorted(property_to_objects.keys()):
        # 将属性名也替换下划线为空格并首字母大写
        prop_name = prop.replace('_', ' ').title()
        
        # 将物品种类列表转换为字符串，用逗号分隔
        obj_types = sorted(property_to_objects[prop])
        # 使用 " ," 作为分隔符，确保逗号前后各有一个空格
        obj_list = " ,".join([obj + " " for obj in obj_types]).rstrip()
        
        # 添加行
        latex_table += f"{prop_name} & {obj_list} \\\\\n\\hline\n"
    
    latex_table += "\\caption{Properties and their corresponding object types}\n"
    latex_table += "\\label{tab:properties}\n"
    latex_table += "\\end{longtable}"
    
    # 保存到文件
    with open('properties_table.tex', 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    return property_to_objects

if __name__ == "__main__":
    property_to_objects = analyze_properties('properties.txt')
    print("LaTeX table has been generated in properties_table.tex") 