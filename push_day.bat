@echo off
REM Push one day of the physical design notes to GitHub.
cd /d "%~dp0"
if not exist .git (
  git init -b main
  git remote add origin https://github.com/Pavitinder-1516/Physical-Design-Notes.git
)
set /p N=Which day do you want to push (01-30)? 
set DAY=
for /d %%D in (Day-%N%-*) do set DAY=%%D
if "%DAY%"=="" (
  echo No folder found for day %N%.
  pause
  exit /b 1
)
if "%N%"=="01" git add README.md PUSH_PLAN.md diagrams tools
git add "%DAY%"
git commit -m "%DAY%"
git push -u origin main
pause
