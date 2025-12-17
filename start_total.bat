@echo off
cd source
start cmd /k "conda activate bh && python main.py --port 57805"
start cmd /k "conda activate bh && python main.py --port 57806"
pause