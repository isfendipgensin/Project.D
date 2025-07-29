import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json
import shutil
import threading
import queue
from collections import defaultdict
import re
import difflib
from ttkthemes import ThemedTk
import psutil
import subprocess

CONFIG_FILE = "config.json"
HITUNG_FILE = "hasil_hitung.json"
LOG_FILE = "log_copy.json"

class FileCounterApp:

    def tanya_output_metode(self):
        win = tk.Toplevel(self.root)
        win.title("Pilih Metode Output")
        win.geometry("350x180")
        self.center_window(win, 350, 180)
        self.set_popup_bg(win)
        var = tk.StringVar(value="per_folder")

        ttk.Label(win, text="Bagaimana Anda ingin hasil copy PSD?").pack(pady=10)
        ttk.Radiobutton(win, text="Per folder sesuai isi JPG", variable=var, value="per_folder").pack(anchor='w', padx=20)
        ttk.Radiobutton(win, text="Disatukan semua ke satu folder", variable=var, value="satu_folder").pack(anchor='w', padx=20)
        ttk.Radiobutton(win, text="Pilih Manual PSD (lewati pencocokan otomatis)", variable=var, value="manual_psd").pack(anchor='w', padx=20)

        result = []

        def pilih():
            result.append(var.get())
            win.destroy()

        ttk.Button(win, text="OK", command=pilih).pack(pady=10)

        win.grab_set()
        win.wait_window()
        return result[0] if result else None

    def ask_password(self, callback):
        win = tk.Toplevel(self.root)
        win.title("Masukkan Password")
        win.geometry("300x100")
        self.center_window(win, 300, 100)
        self.set_popup_bg(win)
        ttk.Label(win, text="Password:").pack(pady=5)
        entry = ttk.Entry(win, show="*", width=30)
        entry.pack(pady=5)
        def check():
            if entry.get() == self.config.get("password", "dma"):
                win.destroy()
                callback()
            else:
                messagebox.showerror("Salah", "Password salah!")
        ttk.Button(win, text="OK", command=check).pack(pady=5)

    def ubah_nama_aplikasi(self):
        win = tk.Toplevel(self.root)
        win.title("Ubah Nama Aplikasi")
        win.geometry("300x120")
        self.center_window(win, 300, 120)
        self.set_popup_bg(win)
        ttk.Label(win, text="Nama Baru:").pack(pady=5)
        entry = ttk.Entry(win)
        entry.insert(0, self.config.get("app_title", "DMA App Beta v.0.1"))
        entry.pack(pady=5)
        def save():
            self.config["app_title"] = entry.get()
            self.root.title(entry.get())
            self.save_config()
            win.destroy()
        ttk.Button(win, text="Simpan", command=save).pack(pady=5)

    def ubah_logo_aplikasi(self):
        file_path = filedialog.askopenfilename(title="Pilih Logo", filetypes=[("Image files", "*.png;*.jpg;*.ico")])
        if file_path:
            self.config["app_logo"] = file_path
            self.save_config()
            messagebox.showinfo("Sukses", "Logo aplikasi berhasil diubah!")

    def ubah_note(self):
        win = tk.Toplevel(self.root)
        win.title("Ubah Note")
        win.geometry("300x160")
        self.center_window(win, 300, 160)

        ttk.Label(win, text="Note Baru:").pack(pady=5)
        entry = ttk.Entry(win)
        entry.insert(0, self.config.get("note", ""))
        entry.pack(pady=5)
        ttk.Label(win, text="Warna Note:").pack(pady=5)
        color_entry = ttk.Entry(win)
        color_entry.insert(0, self.config.get("note_color", "green"))
        color_entry.pack(pady=5)
        def save():
            self.config["note"] = entry.get()
            self.config["note_color"] = color_entry.get()
            self.label_note.config(text=f"NOTE: {entry.get()}", foreground=color_entry.get())
            self.save_config()
            win.destroy()
        ttk.Button(win, text="Simpan", command=save).pack(pady=5)

    def ubah_password(self):
        win = tk.Toplevel(self.root)
        win.title("Ubah Password")
        win.geometry("300x120")
        self.center_window(win, 300, 120)
        self.set_popup_bg(win)
        ttk.Label(win, text="Password Baru:").pack(pady=5)
        entry = ttk.Entry(win, show="*")
        entry.pack(pady=5)
        def save():
            self.config["password"] = entry.get()
            self.save_config()
            messagebox.showinfo("Sukses", "Password berhasil diubah!")
            win.destroy()
        ttk.Button(win, text="Simpan", command=save).pack(pady=5)

    def __init__(self, root):
        self.root = root
        self.selected_dir = tk.StringVar()
        self.total_count = tk.IntVar()
        self.msg_queue = queue.Queue()

        self.config = self.load_config()
        self.root.title(self.config.get("app_title", "DMA App Beta v.0.1"))

        # Menu
        menubar = tk.Menu(root)

        # Menu Pengaturan
        setting = tk.Menu(menubar, tearoff=0)
        setting.add_command(label="Ubah Nama Aplikasi", command=lambda: self.ask_password(self.ubah_nama_aplikasi))
        setting.add_command(label="Ubah Logo Aplikasi", command=lambda: self.ask_password(self.ubah_logo_aplikasi))
        setting.add_command(label="Ubah NOTE", command=lambda: self.ask_password(self.ubah_note))
        setting.add_command(label="Ubah Password", command=lambda: self.ask_password(self.ubah_password))
        menubar.add_cascade(label="Pengaturan", menu=setting)

        # Menu Theme (Dropdown)
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="Normal", command=lambda: self.set_theme_switch("plastik"))
        theme_menu.add_command(label="Dark", command=lambda: self.set_theme_switch("equilux"))
        menubar.add_cascade(label="Theme", menu=theme_menu)

        root.config(menu=menubar)

        # UI atas
        ftop = ttk.Frame(root, padding=10)
        ftop.pack(fill='x')
        ttk.Label(ftop, text="Pilih Direktori:").pack(side='left')
        ttk.Entry(ftop, textvariable=self.selected_dir, width=50, state='readonly').pack(side='left', padx=5)
        ttk.Button(ftop, text="Pilih Folder", command=self.choose_directory).pack(side='left')

        # Pilihan Proses
        fbtn = ttk.Frame(root, width=550)
        fbtn.pack(pady=5, fill='x')
        self.proses_var = tk.StringVar(value="start_counting")
        opsi = [
            ("PROFESI", "start_counting"),
            ("WSD / MSK", "hitung_wisuda"),
            ("CUSTOM", "hitung_custom"),
            ("BUAT MASTER", "lanjutkan_copy"),
            ("PHOTOSHOP SCRIPT", "open_photoshop_gui"),
            # ("CROP PAS FOTO", "crop_pas_foto"),  # Hapus baris ini
        ]
        for text, val in opsi:
            ttk.Radiobutton(fbtn, text=text, variable=self.proses_var, value=val).pack(side='left', padx=4, pady=4)
        
        # HAPUS BARIS INI untuk menghilangkan tombol CROP PAS FOTO
        # ttk.Button(fbtn, text="CROP PAS FOTO", command=lambda: threading.Thread(target=self.crop_pas_foto).start()).pack(side='left', padx=10, pady=4)
        # Tombol Proses dan Reset di bawah tengah
        proses_frame = ttk.Frame(root)
        proses_frame.pack(pady=10)
        ttk.Button(proses_frame, text="Proses", command=self.proses_pilihan).pack(side='left', padx=5)
        ttk.Button(proses_frame, text="Reset", command=self.reset_hasil).pack(side='left', padx=5)

        # Progress
        self.progress = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress.pack(pady=5)

        # Table
        columns=('FOLDER','JUMLAH','SINGLE')
        self.tree=ttk.Treeview(root, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=150 if col=='FOLDER' else 80)
        self.tree.pack(padx=10,pady=5, fill='x')

        # Note & total
        note = self.config.get("note","")
        color = self.config.get("note_color","green")
        style = ttk.Style()
        style.configure("Note.TLabel", foreground=color, font=('Arial',10,'bold'))
        self.label_note = ttk.Label(root, text=f"NOTE: {note}", style="Note.TLabel")
        self.label_note.pack(pady=5)

        style.configure("Total.TLabel", font=('Arial',12,'bold'))
        self.label_total=ttk.Label(root, text="TOTAL SEMUA : 0", style="Total.TLabel")
        self.label_total.pack(pady=5)

        ttk.Button(root, text="Edit Value", command=self.edit_value).pack(pady=5)

        self.root.after(100, self.check_queue)
        self.set_theme_switch("plastik")
        self.center_window(self.root, 500, 600)

    # === Functions ===
    def reset_hasil(self):
        self.tree.delete(*self.tree.get_children())
        self.progress['value'] = 0
        self.total_count.set(0)
        self.label_total.config(text="TOTAL SEMUA : 0")
        if os.path.exists(HITUNG_FILE):
            os.remove(HITUNG_FILE)
        messagebox.showinfo("Reset", "Hasil telah direset!")
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"password":"dma", "note_color":"green"}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def choose_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_dir.set(folder)

    def start_counting(self):
        dir_path = self.selected_dir.get()
        if not dir_path:
            messagebox.showwarning("Pilih direktori dulu!", "")
            return

        # --- Filter folder sesuai permintaan ---
        subfolders = [f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        folder_angka = sorted([f for f in subfolders if f.strip()[:1].isdigit()], key=lambda x: int(x.strip().split('.')[0]) if '.' in x else 999)
        folder_acuan = None

        if folder_angka:
            # Jika ada folder angka, ambil hanya folder nomor 1
            for f in folder_angka:
                if f.strip().startswith('1'):
                    folder_acuan = f
                    break
        if not folder_acuan:
            # Jika tidak ada folder angka 1, cari folder dengan kata kunci
            keywords = ['PROFESI', 'OB PROFESI', 'OB', 'WISUDA', 'MANASIK']
            for f in subfolders:
                if any(kw in f.upper() for kw in keywords):
                    folder_acuan = f
                    break

        if folder_acuan:
            # Proses hanya folder acuan
            target_dir = os.path.join(dir_path, folder_acuan)
        else:
            # Jika tidak ditemukan, proses seperti biasa (atau bisa tampilkan warning)
            target_dir = dir_path

        # --- Lanjutkan step berikutnya seperti biasa ---
        self.tree.delete(*self.tree.get_children())
        self.progress['value'] = 0
        label_data, angka_map = self.proses_folder(target_dir)
        total = 0
        hasil = []
        for label, counts in sorted(label_data.items()):
            jumlah = counts['group']
            single = counts['single']
            total += jumlah + single
            self.tree.insert('', 'end', values=(label, jumlah, single))
            hasil.append({"label": label, "jumlah": jumlah, "single": single, "angka": angka_map.get(label, [])})
        self.total_count.set(total)
        self.label_total.config(text=f"TOTAL SEMUA : {total}")
        self.progress['value'] = 100
        with open(HITUNG_FILE, "w") as f:
            json.dump(hasil, f)

    def hitung_wisuda(self):
        dir_path = self.selected_dir.get()
        if not dir_path:
            messagebox.showwarning("Pilih direktori dulu!", "")
            return

        # Cari folder nomor 1 yang mengandung WISUDA atau MANASIK
        subfolders = [f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        folder_1 = None
        for f in subfolders:
            nama = f.strip().upper()
            if nama.startswith('1') and ('WISUDA' in nama or 'MANASIK' in nama):
                folder_1 = f
                break

        if not folder_1:
            messagebox.showwarning("Tidak ditemukan", "Folder nomor 1 yang mengandung WISUDA atau MANASIK tidak ditemukan!")
            return

        # Proses hanya folder tersebut
        target_dir = os.path.join(dir_path, folder_1)
        self.tree.delete(*self.tree.get_children())
        self.progress['value'] = 0
        label_data, angka_map = self.proses_folder(target_dir)
        total = 0
        hasil = []
        # Nama label hasil mengikuti nama folder (tanpa angka depan)
        label_folder = folder_1
        for label, counts in sorted(label_data.items()):
            jumlah = counts['group']
            single = counts['single']
            total += jumlah + single
            # Label hasil = "WISUDA" atau "MANASIK" sesuai nama folder
            if 'WISUDA' in label_folder.upper():
                label_hasil = "WISUDA"
            elif 'MANASIK' in label_folder.upper():
                label_hasil = "MANASIK"
            else:
                label_hasil = label_folder
            self.tree.insert('', 'end', values=(label_hasil, jumlah, single))
            hasil.append({"label": label_hasil, "jumlah": jumlah, "single": single, "angka": angka_map.get(label, [])})
        self.total_count.set(total)
        self.label_total.config(text=f"TOTAL SEMUA : {total}")
        self.progress['value'] = 100
        with open(HITUNG_FILE, "w") as f:
            json.dump(hasil, f)

    def lanjutkan_copy(self, data=None, missing_labels=None):
        # --- Pilihan mode ---
        win = tk.Toplevel(self.root)
        win.title("Pilih Mode Lanjut")
        win.geometry("350x150")
        self.center_window(win, 350, 150)
        self.set_popup_bg(win)
        var = tk.StringVar(value="profesi")
        ttk.Label(win, text="Pilih jenis proses:").pack(pady=10)
        ttk.Radiobutton(win, text="WISUDA / MANASIK / PAS FOTO", variable=var, value="wisuda").pack(anchor='w', padx=20)
        ttk.Radiobutton(win, text="PROFESI", variable=var, value="profesi").pack(anchor='w', padx=20)
        result = []
        def pilih():
            result.append(var.get())
            win.destroy()
        ttk.Button(win, text="OK", command=pilih).pack(pady=10)
        win.grab_set()
        win.wait_window()
        if not result:
            return
        mode = result[0]

        if not os.path.exists(HITUNG_FILE):
            self.msg_queue.put(("status","Belum ada hasil hitung!"))
            return

        if data is None:
            with open(HITUNG_FILE,"r") as f:
                data=json.load(f)

        if missing_labels is not None:
            # Filter hanya label yang gagal sebelumnya
            data = [item for item in data if item["label"] in missing_labels]

        if mode == "wisuda":
            # --- PILIH MANUAL PSD UNTUK SETIAP LABEL ---
            manual_map = {}
            for item in data:
                label = item["label"]
                file_path = filedialog.askopenfilename(
                    title=f"Pilih file PSD untuk label '{label}'",
                    filetypes=[("PSD files", "*.psd")])
                if file_path:
                    manual_map[label] = file_path

            # Setelah semua file dipilih, baru pilih folder tujuan
            dst = filedialog.askdirectory(title="Pilih Folder Tujuan")
            if not dst: return

            # Proses copy manual
            copied = 0
            for item in data:
                label = item["label"]
                if label in manual_map:
                    angka_list = item.get("angka", [])
                    n_copy = item["jumlah"] + item["single"]
                    dst_folder = os.path.join(dst, label) if label != "Tanpa Keterangan" else dst
                    os.makedirs(dst_folder, exist_ok=True)
                    for i, angka in enumerate(angka_list):
                        if i >= n_copy: break
                        new_name = f"{angka}.psd"
                        target_path = os.path.join(dst_folder, new_name)
                        if not os.path.exists(target_path):
                            shutil.copy2(manual_map[label], target_path)
                            copied += 1
                            self.msg_queue.put(("progress", copied))
            messagebox.showinfo("Selesai", "Copy manual selesai!")
            self.progress['value'] = 0
            return

        # --- MODE PROFESI (otomatis, seperti sebelumnya) ---
        try:
            import ps
        except Exception as e:
            messagebox.showerror("Error", f"Gagal import ps.py: {e}")
            return

        if not os.path.exists(HITUNG_FILE):
            self.msg_queue.put(("status","Belum ada hasil hitung!"))
            return

        if data is None:
            with open(HITUNG_FILE,"r") as f:
                data=json.load(f)

        if missing_labels is not None:
            # Filter hanya label yang gagal sebelumnya
            data = [item for item in data if item["label"] in missing_labels]

        src=filedialog.askdirectory(title="Pilih Folder Master (PSD)")
        if not src: return
        dst=filedialog.askdirectory(title="Pilih Folder Tujuan")
        if not dst: return

        pilihan = self.tanya_output_metode()
        if not pilihan: return

        per_folder = (pilihan == "per_folder")

        total_files=sum( item["jumlah"]+item["single"] for item in data )
        if total_files==0:
            self.msg_queue.put(("status","Tidak ada file untuk dicopy!"))
            return

        copied=0
        success_log=[]
        missing_log=[]
        missing_labels_new = []
        self.msg_queue.put(("progress",0))
        self.msg_queue.put(("status","Mulai copy file..."))

        for item in data:
            label = item["label"]
            angka_list = item.get("angka", [])
            n_copy = item["jumlah"] + item["single"]
            master = None

            # Cari semua file PSD di folder master
            psd_files = [f for f in os.listdir(src) if f.lower().endswith(".psd")]
            # Fuzzy matching: cari nama file yang paling mirip dengan label
            matches = difflib.get_close_matches(label.lower(), [os.path.splitext(f)[0].lower() for f in psd_files], n=1, cutoff=0.7)
            if matches:
                # Ambil file yang paling mirip
                idx = [os.path.splitext(f)[0].lower() for f in psd_files].index(matches[0])
                master = psd_files[idx]
            else:
                # Langsung masukkan ke daftar gagal, tanpa popup input manual
                missing_log.append(f"Master PSD tidak ditemukan: '{label}'")
                missing_labels_new.append(label)
                continue

            if per_folder and label != "Tanpa Keterangan":
                folder_dst = os.path.join(dst, label)
                os.makedirs(folder_dst, exist_ok=True)
            else:
                folder_dst = dst

            for i, angka in enumerate(angka_list):
                if i >= n_copy: break
                new_name = f"{angka}.psd"
                target_path = os.path.join(folder_dst, new_name)
                if not os.path.exists(target_path):  # Hanya copy jika belum ada
                    shutil.copy2(os.path.join(src, master), target_path)
                    copied += 1
                    self.msg_queue.put(("progress", copied))

            success_log.append(f"Master PSD '{label}' : {n_copy}")

        text="\n".join(success_log+[""]+missing_log)
        self.msg_queue.put(("show_log_popup", text))
        self.msg_queue.put(("status","Copy selesai!"))

        if missing_labels_new:
            # Tampilkan pilihan untuk mengulang, pilih manual, atau selesai
            def ulang():
                popup.destroy()
                threading.Thread(target=lambda: self.lanjutkan_copy(data=None, missing_labels=missing_labels_new)).start()

            def manual():
                popup.destroy()
                manual_map = {}
                for label in missing_labels_new:
                    file_path = filedialog.askopenfilename(
                        title=f"Pilih file PSD untuk label '{label}'",
                        filetypes=[("PSD files", "*.psd")])
                    if file_path:
                        manual_map[label] = file_path
                if manual_map:
                    # Proses copy hanya untuk label yang dipilih manual
                    for item in data:
                        label = item["label"]
                        if label in manual_map:
                            angka_list = item.get("angka", [])
                            n_copy = item["jumlah"] + item["single"]
                            dst_folder = os.path.join(dst, label) if per_folder and label != "Tanpa Keterangan" else dst
                            os.makedirs(dst_folder, exist_ok=True)
                            for i, angka in enumerate(angka_list):
                                if i >= n_copy: break
                                new_name = f"{angka}.psd"
                                target_path = os.path.join(dst_folder, new_name)
                                if not os.path.exists(target_path):
                                    shutil.copy2(manual_map[label], target_path)
                    messagebox.showinfo("Selesai", "Copy manual selesai!")
                self.progress['value'] = 0  # Reset progress bar

            def selesai():
                popup.destroy()
                messagebox.showinfo("Selesai", f"Copy selesai dengan beberapa master tidak ditemukan.")
                self.progress['value'] = 0  # Reset progress bar

            popup = tk.Toplevel(self.root)
            popup.title("Master Tidak Ditemukan")
            popup.geometry("400x150")
            self.center_window(popup, 400, 150)
            self.set_popup_bg(popup)  # <-- Tambahkan baris ini
            ttk.Label(
                popup,
                text="Beberapa master PSD tidak ditemukan.\nIngin pilih folder master lagi, pilih manual PSD, atau selesai?"
            ).pack(padx=20, pady=10)
            ttk.Button(popup, text="Pilih Folder Master Lagi", command=ulang).pack(side='left', padx=10, pady=10)
            ttk.Button(popup, text="Pilih Manual PSD", command=manual).pack(side='left', padx=10, pady=10)
            ttk.Button(popup, text="Selesai", command=selesai).pack(side='right', padx=10, pady=10)
        else:
            messagebox.showinfo("Selesai", f"Copy selesai!")
            self.progress['value'] = 0  # Reset progress bar

    def open_photoshop_gui(self):
        try:
            import ps
            threading.Thread(target=lambda: ps.create_gui(master=self.root), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka Photoshop Script:\n{e}")

    def check_queue(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                if msg[0]=="status":
                    self.label_note.config(text=f"NOTE: {msg[1]}")
                elif msg[0]=="progress":
                    self.progress['value']=msg[1]
                elif msg[0]=="show_log_popup":
                    self.show_log_popup(msg[1])
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def show_log_popup(self, text):
        win = tk.Toplevel(self.root)
        win.title("Log Hasil Copy")
        win.geometry("500x300")
        self.center_window(win, 500, 300)
        self.set_popup_bg(win)
        txt = tk.Text(win, wrap='word')
        txt.insert('1.0', text)
        txt.config(state='disabled')
        # Set warna sesuai theme
        theme = self.root.get_theme() if hasattr(self.root, "get_theme") else "plastik"
        if theme == "equilux":
            txt.configure(bg="#222", fg="#eee", insertbackground="#eee")
        else:
            txt.configure(bg="#f0f0f0", fg="#000", insertbackground="#000")
        txt.pack(expand=True, fill='both', padx=10, pady=10)
        ttk.Button(win, text="Tutup", command=win.destroy).pack(pady=5)

    def proses_folder(self, folder_root):
        label_data=defaultdict(lambda:{'group':0,'single':0})
        angka_map=defaultdict(list)
        for root,_,files in os.walk(folder_root):
            rel=os.path.relpath(root, folder_root)
            is_root=(rel==".")
            folder="Tanpa Keterangan" if is_root else os.path.basename(root).upper()
            grup=defaultdict(set)
            for f in files:
                if f.lower().endswith(".jpg"):
                    m=re.match(r"(\d+)\s*\((\d+)\)(?:\s+(.*?))?\.(jpg|jpeg)", f,re.I)
                    if m:
                        angka,num,label=m.group(1),m.group(2),m.group(3)
                        lbl=label.strip().upper() if label else ("TANPA LABEL" if is_root else folder)
                        key=f"{angka}_{lbl}"
                        grup[key].add(num)
            for key,s in grup.items():
                angka,label_final=key.split("_",1)
                angka_map[label_final].append(angka)
                if '1'in s and '2'in s:
                    label_data[label_final]['group']+=1
                else:
                    label_data[label_final]['single']+=len(s)
        return label_data, angka_map

    def edit_value(self):
        sel=self.tree.selection()
        if not sel: 
            messagebox.showwarning("Pilih baris!","")
            return
        v=self.tree.item(sel)['values']
        win = tk.Toplevel(self.root)
        win.title(f"Edit - {v[0]}")
        win.geometry("300x200")
        self.center_window(win, 300, 200)
        self.set_popup_bg(win)
        ttk.Label(win,text=f"Folder: {v[0]}").pack(pady=5)
        ttk.Label(win,text="Jumlah Grup:").pack()
        e1=ttk.Entry(win); e1.insert(0,str(v[1])); e1.pack()
        ttk.Label(win,text="Jumlah Single:").pack()
        e2=ttk.Entry(win); e2.insert(0,str(v[2])); e2.pack()
        def save():
            try:
                new_j=int(e1.get())
                new_s=int(e2.get())
                self.tree.item(sel, values=(v[0],new_j,new_s))
                self.update_total()
                win.destroy()
            except: 
                messagebox.showerror("Error","Angka tidak valid")
        ttk.Button(win,text="Simpan",command=save).pack(pady=5)

    def update_total(self):
        t=0
        for i in self.tree.get_children():
            v=self.tree.item(i)['values']
            t+=int(v[1])+int(v[2])
        self.total_count.set(t)
        self.label_total.config(text=f"TOTAL SEMUA : {t}")

    def set_theme(self, theme_name):
        self.root.set_theme(theme_name)

    def apply_dark_mode(self):
        bg = "#222"
        fg = "#eee"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def apply_light_mode(self):
        bg = "#f0f0f0"
        fg = "#000"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def set_theme_switch(self, theme_name):
        self.root.set_theme(theme_name)
        if theme_name == "equilux":
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def center_window(self, win, width=None, height=None):
        win.update_idletasks()
        if width is None or height is None:
            width = win.winfo_width()
            height = win.winfo_height()
        x = win.winfo_screenwidth() // 2 - width // 2
        y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def set_popup_bg(self, win):
        theme = self.root.get_theme() if hasattr(self.root, "get_theme") else "plastik"
        if theme == "equilux":
            win.configure(bg="#222")
        else:
            win.configure(bg="#f0f0f0")

    # Tambahkan ask_password, ubah_nama_aplikasi, ubah_logo_aplikasi, ubah_note, ubah_password
    # ... (copy dari versi sebelumnya)

    def hitung_custom(self):
        folder = filedialog.askdirectory(title="Pilih Folder Untuk Hitung JPG")
        if not folder:
            return

        # Hitung semua file jpg (rekursif)
        count_jpg = 0
        for root, _, files in os.walk(folder):
            count_jpg += sum(1 for f in files if f.lower().endswith('.jpg'))

        self.tree.delete(*self.tree.get_children())
        self.progress['value'] = 0
        self.tree.insert('', 'end', values=(os.path.basename(folder), count_jpg, 0))
        hasil = [{"label": os.path.basename(folder), "jumlah": count_jpg, "single": 0, "angka": []}]
        self.total_count.set(count_jpg)
        self.label_total.config(text=f"TOTAL SEMUA : {count_jpg}")
        self.progress['value'] = 100
        with open(HITUNG_FILE, "w") as f:
            json.dump(hasil, f)

    def proses_pilihan(self):
        pilihan = self.proses_var.get()
        if pilihan == "start_counting":
            self.start_counting()
        elif pilihan == "hitung_wisuda":
            self.hitung_wisuda()
        elif pilihan == "lanjutkan_copy":
            threading.Thread(target=self.lanjutkan_copy).start()
        elif pilihan == "open_photoshop_gui":
            self.open_photoshop_gui()
        elif pilihan == "hitung_custom":
            self.hitung_custom()
        elif pilihan == "crop_pas_foto":
            threading.Thread(target=self.crop_pas_foto).start()

if __name__=="__main__":
    root = ThemedTk(theme="plastik")  # default normal
    app = FileCounterApp(root)
    # print(root.get_themes())  # Uncomment jika ingin melihat daftar theme
    root.mainloop()

# Contoh menampilkan semua theme:
print(root.get_themes())  # ['arc', 'black', 'blue', 'clearlooks', ...]
