@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=uhh i added operators for uh the set data type"

git status

git commit -m "%MSG%"

git push origin main

pause
