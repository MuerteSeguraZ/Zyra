@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=stdlib"

git status

git commit -m "%MSG%"

git push origin main --force

pause
