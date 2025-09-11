@echo off

REM a

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=decimal added (check main.py for example)"

git status

git commit -m "%MSG%"

git push origin main

pause
