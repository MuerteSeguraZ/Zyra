@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=added spaceship operator <=> because my third cat wanted to sort things out faster (he's lazy)"

git status

git commit -m "%MSG%"

git push origin main --force

pause
