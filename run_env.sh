#!/bin/bash

# 顯示當前 IP 地址，這需要另外找到合適的命令來替代 Windows 批次檔中的 %myip% 變量。
echo "Current IP: $(hostname -I | cut -d' ' -f1) run"

# 切換工作目錄至腳本所在目錄
cd "$(dirname "$0")"

echo "Start waitress"
export FLASK_ENV=development
# export FLASK_APP=main.py

# 執行 Flask 應用
flask run --reload --debugger --host 0.0.0.0 --port 80
