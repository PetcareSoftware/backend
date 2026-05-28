@echo off
echo === RESTAURACIÓN DE BASE DE DATOS SQLite PetCare ===
echo.

set /p BACKUP_FILE="Ruta completa del archivo .sqlite3 a restaurar: "
if not exist "%BACKUP_FILE%" (
    echo Archivo no encontrado.
    exit /b 1
)

set /p CONFIRM="¿Restaurar? Esto sobrescribirá la base de datos actual (s/N): "
if /i not "%CONFIRM%"=="s" (
    echo Cancelado.
    exit /b 0
)

:: Detener el servidor si está corriendo 
echo Asegúrate de que el servidor Django no esté corriendo.
pause

:: Copiar backup a db.sqlite3
copy "%BACKUP_FILE%" "db.sqlite3" /Y

if %errorlevel% eq 0 (
    echo Restauración exitosa.
) else (
    echo Error en restauración.
)
pause