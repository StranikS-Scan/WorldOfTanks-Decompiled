@echo off

echo.
echo Searching and deleting directories:
echo.

set "source=%~dp0source\res"

for /f "tokens=* delims=" %%d in ('dir /ad/b/ogne "%source%"') do (
    for %%x in (gui vscript) do (
        if exist "%source%\%%d\%%x\" (            

            del "%source%\%%d\%%x\*.*" /s/f/q >nul
            cd "%source%\%%d"
            rd "%source%\%%d\%%x" /s/q >nul
 
            echo     %source%\%%d\%%x\)
        )
    )
)

echo.
pause
