@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=printf added and null datatype because i didnt know what to add tbh"

git status

git commit -m "%MSG%"

git push origin main

pause
