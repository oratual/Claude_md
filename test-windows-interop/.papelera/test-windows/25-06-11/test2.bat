@echo off
setlocal enabledelayedexpansion

echo === Test 2: BAT con Lógica ===
set counter=0

:loop
set /a counter+=1
echo Iteración: !counter!
if !counter! lss 3 goto loop

echo.
if exist C:\Windows (
    echo [OK] Directorio Windows encontrado
) else (
    echo [ERROR] No se encuentra C:\Windows
)

echo Test finalizado con !counter! iteraciones