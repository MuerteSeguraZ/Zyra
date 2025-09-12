@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=Readme upd p.2"

git status

git commit -m "%MSG%"

git push origin main --force

pause
