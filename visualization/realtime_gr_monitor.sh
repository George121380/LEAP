#!/bin/bash

# 设置要监控的 Python 文件路径
PYTHON_FILE="visualization/realtime_gr_monitor.py"

# 检查 Python 文件是否存在
if [[ ! -f "$PYTHON_FILE" ]]; then
  echo "Error: Python script '$PYTHON_FILE' not found!"
  exit 1
fi

# 运行 Python 脚本
echo "Starting to monitor the goal representation..."
python3 "$PYTHON_FILE"

# 如果要使用 Python 2，替换为 python "$PYTHON_FILE"
