@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=Minor bug (i forgot to add * and / hehe)"

git status

git commit -m "%MSG%"

git push origin main

pause
