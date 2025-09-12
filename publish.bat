@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=isize/usize because my dog likes messing with memory"

git status

git commit -m "%MSG%"

git push origin main --force

pause
