@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=MASSIVE UPGRADE like giant mushroom typa shit"

git status

git commit -m "%MSG%"

git push origin main --force

pause
