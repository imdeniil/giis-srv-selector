@echo off
chcp 65001 >nul
echo ============================================
echo   Сборка GIIS Server Selector в EXE
echo ============================================
echo.

echo [1/2] Компиляция с PyInstaller...
.venv\Scripts\pyinstaller.exe --onefile --windowed --name "GIIS_ServerSelector" --uac-admin giis_srv_selector.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ОШИБКА: Не удалось скомпилировать!
    echo ============================================
    pause
    exit /b 1
)

echo.
echo [2/2] Готово!
echo.
echo ============================================
echo Исполняемый файл создан:
echo dist\GIIS_ServerSelector.exe
echo ============================================
echo.
pause
