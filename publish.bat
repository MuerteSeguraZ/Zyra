@echo off

REM a

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=runner (zyra <filename.zy>) so i dont have to do a main.py ever again"

git status

git commit -m "%MSG%"

git push origin main

pause
