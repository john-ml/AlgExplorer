@echo off
:top
set /p input=Input file (drag and drop into this window, then press enter): 
set trained=trained.txt
set /p subs=Consider substitutions (y/n)? 
set /p peek=Print top X algs per movecount level (y/n)? 
if "%peek%" EQU "y" (set /p peek=X = ) else (set peek=)
set /p output=Write output to file (y/n)? 
if "%output%" EQU "y" (set /p output=Output filename: ) else (set output=)
set /p batten=Use Chad Batten's evaluation scheme (y/n)? 
set /p aufs=Ignore AUFs (y/n)? 

set s=python algexplorer.py %input% trained.txt
if "%subs%" EQU "y" (set s=%s% -s)
if "%peek%" NEQ "" (set s=%s% -p %peek%)
if "%output%" NEQ "" (set s=%s% -o "%output%")
if "%batten%" EQU "y" (set s=%s% -b)
if "%aufs%" EQU "y" (set s=%s% -tl U -tr U)
echo.
%s%
echo.
set /p another=Analyze another (y/n)? 
set input=
set trained=
set subs=
set peek=
set output=
set batten=
if "%another%" EQU "y" (goto :top)