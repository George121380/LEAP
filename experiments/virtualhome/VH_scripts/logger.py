import logging
import os
import csv
from datetime import datetime
k = 100  

class CsvFormatter(logging.Formatter):
    def __init__(self, k):
        super().__init__()
        self.k = k

    def format(self, record):
        formatted_fields = []
        for field in [record.msg, record.args[0], record.args[1], record.args[2], record.args[3], record.args[4]]:
            formatted_field = self.ensure_line_length(str(field), self.k)
            formatted_fields.append(formatted_field)
        return formatted_fields

    def ensure_line_length(self, text, k):
        lines = text.split('\n')
        adjusted_lines = []

        for line in lines:
            while len(line) > k:
                adjusted_lines.append(line[:k])
                line = line[k:]  # 剩下的部分继续处理
            adjusted_lines.append(line)  # 将不足k的部分添加

        return '\n'.join(adjusted_lines)  # 将处理后的内容重新组合为完整的文本

class CsvHandler(logging.Handler):
    def __init__(self, folder_path):
        logging.Handler.__init__(self)

        # 确保文件夹存在
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # 生成唯一的文件名，例如使用时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"log_{timestamp}.csv"
        self.filepath = os.path.join(folder_path, filename)

        # 打开文件并设置写入模式为追加模式
        self.file = open(self.filepath, 'a', newline='', encoding='utf-8')

        # 创建csv写入器，设置引用规则以处理逗号和换行符
        self.csv_writer = csv.writer(self.file, quoting=csv.QUOTE_MINIMAL)

        # 写入表头
        self.csv_writer.writerow(['Goal Representation', 'Debug Result', 'Action', 'Add Info','LLM Answer','Plan'])

    def emit(self, record):
        # 获取当前记录格式化后的行
        csv_row = self.format(record)

        # 直接写入整行
        self.csv_writer.writerow(csv_row)
        self.file.flush()

    def close(self):
        self.file.close()
        logging.Handler.close(self)

def setup_logger(folder_path, k):
    logger = logging.getLogger('csv_logger')
    logger.setLevel(logging.INFO)

    # 设置自定义Csv处理器
    handler = CsvHandler(folder_path)
    formatter = CsvFormatter(k)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# 使用指定文件夹存储日志，并设置k的值
folder_path = 'log/records'
logger = setup_logger(folder_path, k)
