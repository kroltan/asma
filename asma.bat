@echo off
if [%1]==[] goto usage
python %~dp0asma.py %1
goto :eof
:usage
echo asma.bat FILE ^> DESTINATION
exit /B 1
