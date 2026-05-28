@echo off
setlocal enabledelayedexpansion

:: ==========================================
:: Configuración
:: ==========================================
set DB_FILE=db.sqlite3
set BACKUP_ROOT=C:\backups\petcare_sqlite
set LOG_FILE=%BACKUP_ROOT%\backup_log.txt

:: ==========================================
:: Crear carpeta con fecha
:: ==========================================
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set DATE_DIR=%datetime:~0,8%
set BACKUP_PATH=%BACKUP_ROOT%\%DATE_DIR%
if not exist "%BACKUP_PATH%" mkdir "%BACKUP_PATH%"

:: ==========================================
:: Nombre del archivo de backup
:: ==========================================
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set BACKUP_FILE=%BACKUP_PATH%\backup_%DB_NAME%_%TIMESTAMP%.sqlite3

:: ==========================================
:: Log inicio
:: ==========================================
echo %date% %time% - Iniciando backup >> %LOG_FILE%

:: ==========================================
:: Copiar el archivo de la base de datos
:: ==========================================
copy "%DB_FILE%" "%BACKUP_FILE%" 2>> %LOG_FILE%

if %errorlevel% neq 0 (
    echo %date% %time% - ERROR en copia >> %LOG_FILE%
    exit /b 1
)

:: ==========================================
:: Eliminar backups de más de 30 días
:: ==========================================
forfiles /p "%BACKUP_ROOT%" /m *.sqlite3 /d -30 /c "cmd /c del @path" 2>nul

echo %date% %time% - Backup completado: %BACKUP_FILE% >> %LOG_FILE%
echo Backup guardado en %BACKUP_FILE%
exit /b 0