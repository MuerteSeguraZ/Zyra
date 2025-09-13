@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=test and readme upd"

git status

git commit -m "%MSG%"

git push origin main --force

pause
