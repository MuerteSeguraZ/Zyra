@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=added != because my other cat didnt like there was no not equal"

git status

git commit -m "%MSG%"

git push origin main --force

pause
