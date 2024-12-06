import logging
import os
import csv
k = 100  

class CsvFormatter(logging.Formatter):
    def __init__(self):
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
                line = line[k:]  
            adjusted_lines.append(line) 

        return '\n'.join(adjusted_lines) 

class CsvHandler(logging.Handler):
    def __init__(self, folder_path,task_name=None):
        logging.Handler.__init__(self)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        if task_name==None:
            filename = f"epoch.csv"

        else:
            filename = f"test_{task_name}.csv"
        self.filepath = os.path.join(folder_path, filename)

        self.file = open(self.filepath, 'a', newline='', encoding='utf-8')

        self.csv_writer = csv.writer(self.file, quoting=csv.QUOTE_MINIMAL)

        self.csv_writer.writerow(['Task Category', 'Content', 'Executed Actions', 'Info','Success Rate','Task Path'])

    def emit(self, record):
        csv_row = self.format(record)
        self.csv_writer.writerow(csv_row)
        self.file.flush()

    def close(self):
        self.file.close()
        logging.Handler.close(self)

def setup_epoch_logger(folder_path,task_name=None):

    logger_name = f'csv_logger_{task_name}'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = CsvHandler(folder_path,task_name)
    formatter = CsvFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_last_task_path_from_logger(logger_handler):
    """
    Return: The last task path in the logger file.
    """
    file_path = logger_handler.filepath

    if not os.path.exists(file_path):
        print("log file does not exist.")
        return None

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        print("log file is empty.")
        return None

    last_row = rows[-1]
    task_path = last_row[0].replace('cdl_dataset/dataset/', '')
    scene_num = int(last_row[-1].replace('Scene_id: ', ''))
    return task_path, scene_num


def filter_tasks(task_list, last_task_path, scene_num):
    
    for idx, task in enumerate(task_list):
        if task[0] == last_task_path and task[1] == scene_num:
            break
    filtered_tasks = task_list[idx + 1:]

    return filtered_tasks

class TaskLoggerFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        lines = record.msg.split('\n')
        formatted_message = '\n'.join(lines)
        return f"{formatted_message}\n{'#' * 30}\n"

class TaskLoggerHandler(logging.Handler):
    def __init__(self, folder_path, task_name=None):
        logging.Handler.__init__(self)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if task_name is None:
            filename = "task_log.txt"
        else:
            filename = f"{task_name}_task_log.txt"

        self.filepath = os.path.join(folder_path, filename)
        self.file = open(self.filepath, 'a', encoding='utf-8')

    def emit(self, record):
        log_message = self.format(record)
        self.file.write(log_message)
        self.file.flush()

    def close(self):
        self.file.close()
        logging.Handler.close(self)

def setup_task_logger(folder_path, task_name=None):
    logger_name = f'task_logger_{task_name}'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = TaskLoggerHandler(folder_path, task_name)
    formatter = TaskLoggerFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
