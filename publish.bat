@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=ptrdiff (small upd cuz now im engrossed in lowlevel stuff)"

git status

git commit -m "%MSG%"

git push origin main --force

pause
