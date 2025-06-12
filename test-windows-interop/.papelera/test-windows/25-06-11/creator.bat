@echo off
echo Creating files from Windows...
echo Test content > created_from_bat.txt
echo @echo off > created_script.bat
echo echo Hello from created script >> created_script.bat
echo Created files in: %cd%
dir created_*.*