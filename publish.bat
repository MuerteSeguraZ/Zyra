@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=Uhh i think it was break and continue"

git status

git commit -m "%MSG%"

git push origin main

pause
