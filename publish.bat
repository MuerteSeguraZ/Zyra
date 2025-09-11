@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=i dont even remember i think it was tuples but the test is big so yeah i like the syntax"

git status

git commit -m "%MSG%"

git push origin main

pause
