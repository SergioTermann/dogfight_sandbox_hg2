@echo off
cd source
start cmd /k "conda activate bh && python main.py --port 57805"
start cmd /k "conda activate bh && python main.py --port 57806"
start cmd /k "conda activate bh && python main.py --port 57807"
start cmd /k "conda activate bh && python main.py --port 57808"
@REM ..\bin\python\python.exe main.py --port 57806
@REM ..\bin\python\python.exe main.py --port 57806
pause