@echo off

cd /d "PATH_TO_SERVER_DIRECTORY"

:StartServer
echo Starting Satisfactory Dedicated Server...
FactoryServer.exe

:: Capture the exit code
set "exitCode=%ERRORLEVEL%"

:: If the exit code is 0, it means a regular shutdown
if "%exitCode%" equ "0" (
    echo Server stopped gracefully. Exiting script.
    exit /b 0
)

:: If the exit code is not 0, assume a crash and restart
echo Server crashed with exit code %exitCode%. Restarting in 5 seconds...
timeout /t 5 /nobreak

:: Go back to the StartServer label to restart the server
goto StartServer
