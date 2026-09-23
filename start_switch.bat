@echo off

timeout /t 7 /nobreak >nul

cd /d E:\switch-ai-assistance

call .venv\Scripts\activate

python main.py