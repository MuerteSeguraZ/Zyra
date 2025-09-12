@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=Uint stuff and some dec bugfixes, my cat approves btw"

git status

git commit -m "%MSG%"

git push origin main

pause
