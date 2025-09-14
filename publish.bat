@echo off

git add --all

set "MSG=%~1"
if "%MSG%"=="" set "MSG=uint128 and int128 because i dont like them missing"

git status

git commit -m "%MSG%"

git push origin main --force

pause
