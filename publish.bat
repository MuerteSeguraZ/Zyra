@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=char literals added"

git status

git commit -m "%MSG%"

git push origin main

pause
