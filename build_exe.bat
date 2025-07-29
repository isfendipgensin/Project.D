@echo off
echo -----------------------------
echo Building EXE with PyInstaller
echo -----------------------------

:: Ganti nama file sesuai file kamu
set FILE=dma_app.py

:: Jalankan pyinstaller
py -m PyInstaller --onefile --noconsole --clean --icon=dma.ico "%FILE%"

echo -----------------------------
echo Build selesai!
echo Hasil ada di folder "dist"
echo -----------------------------
pause
