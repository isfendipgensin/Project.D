@echo off
:: auto_push.bat - Script untuk otomatis add, commit, dan push ke GitHub

set /p MESSAGE="Masukkan pesan commit: "

:: Ganti ke folder projectmu
cd /d E:\PATH\KE\FOLDER\Project.D

:: Tambahkan semua perubahan
git add .

:: Commit dengan pesan yang dimasukkan pengguna
git commit -m "%MESSAGE%"

:: Push ke branch master (ganti main jika perlu)
git push origin master

echo.
echo Selesai! Perubahan sudah di-push ke GitHub.
pause
