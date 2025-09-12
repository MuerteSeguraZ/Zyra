@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=readme upd 3"

git status

git commit -m "%MSG%"

git push origin main --force

pause
