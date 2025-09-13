@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=u didn't have enough with uints? well here's ints from 8 to 64"

git status

git commit -m "%MSG%"

git push origin main --force

pause
