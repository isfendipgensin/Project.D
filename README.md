# 📦 Project.D - Cara Update & Upload ke GitHub

Berikut langkah-langkah **update versi aplikasi dan upload ke GitHub** agar updater bisa mendeteksi update baru.

---

## ✅ 1) Edit kode di lokal
- Buka project di komputermu
- Edit file Python sesuai kebutuhan
- Jangan lupa update `version.txt` → misalnya:
```
1.0.2
```

---

## ⚙️ 2) Buka terminal / Git Bash & pindah ke folder project
```bash
cd "E:/PATH/KE/FOLDER/Project.D"
```

---

## 📌 3) Tambahkan file yang berubah
```bash
git add .
```

---

## 📝 4) Commit perubahan
```bash
git commit -m "Update fitur baru, versi 1.0.2"
```

---

## 🚀 5) Push ke GitHub
Jika branch kamu bernama `master`:
```bash
git push origin master
```

Jika branch bernama `main`:
```bash
git push origin main
```

---

✅ Selesai! Versi baru sudah ada di GitHub.
Updater Python akan otomatis mendeteksi versi lebih baru & download ZIP update.

📌 *Tips:* file `version.txt` cukup berisi angka versi, misalnya:
```
1.0.2
```

🚀 **Selamat mengembangkan!**
