@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=dicts and indexing added"

git status

git commit -m "%MSG%"

git push origin main

pause
