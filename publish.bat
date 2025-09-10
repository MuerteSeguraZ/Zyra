@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=oops forgot not mb here ya go :)"

git status

git commit -m "%MSG%"

git push origin main

pause
