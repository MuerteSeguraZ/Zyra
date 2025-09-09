@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=comments (//) and multi-line comments (/* */)!!!!!"

git status

git commit -m "%MSG%"

git push origin main

pause
