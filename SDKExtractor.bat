@echo off
cd /d "%~dp0"
set "EXTRACT_DIR=ToExtract"

REM Wypakowywujemy wszystkie zipy z ToExtract, sprawdziwszy wczesniej, czy aby juz nie wypakowane
for %%F in ("%EXTRACT_DIR%\*.zip") do (

    REM Pobiera nazwę katalogu docelowego (bez rozszerzenia .zip)
    if exist "%%~nF" (
        echo "Katalog %%~nF już istnieje. Pomijam rozpakowywanie."
    ) else (
        echo "Rozpakowywanie %%F..."
        powershell -Command "Expand-Archive -Path '%%F' -DestinationPath '.' -Force"
        echo "Rozpakowano %%F do bieżącego katalogu"
    )
)

pause