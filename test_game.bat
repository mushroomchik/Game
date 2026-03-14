@echo off
chcp 65001 >nul
cd /d C:\Users\USER\PycharmProjects\Game
python run_tests.py
type test_output.txt
