import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import threading
import queue
import os
import psutil
import json
import subprocess

CONFIG_FILE = "ps_config.json"

PS_USERCONFIG_PATH = os.path.expanduser("~/Documents/Adobe/Adobe Photoshop/PSUserConfig.txt")

def create_gui(master=None):
    q = queue.Queue()

    config = load_config()
    photoshop_exe = config.get("photoshop_exe", "C:/Program Files/Adobe/Adobe Photoshop 2023/Photoshop.exe")
    button_color = config.get("button_color", "#4CAF50")
    button_icon_path = config.get("button_icon", "icon.png")

    if master is None:
        root = tk.Tk()
    else:
        root = tk.Toplevel(master)

    root.title("Photoshop Script Runner")
    root.geometry("500x500")

    # Menu bar
    menubar = tk.Menu(root)
    pengaturan_menu = tk.Menu(menubar, tearoff=0)
    pengaturan_menu.add_command(label="Ubah Path Photoshop", command=lambda: ubah_path_photoshop())
    pengaturan_menu.add_command(label="Pengaturan Tombol", command=lambda: pengaturan_tombol())
    pengaturan_menu.add_command(label="Matikan Popup Script Photoshop", command=lambda: matikan_popup_script())
    pengaturan_menu.add_command(label="Lihat Lokasi PSUserConfig.txt", command=lambda: lihat_lokasi_userconfig())
    menubar.add_cascade(label="Pengaturan", menu=pengaturan_menu)
    root.config(menu=menubar)

    status_var = tk.StringVar(value="Status: Siap")

    tk.Label(root, text="Folder Scripts:").pack(pady=5)
    script_folder_var = tk.StringVar()
    tk.Entry(root, textvariable=script_folder_var, width=50, state='readonly').pack(padx=5)

    def pilih_folder():
        folder = filedialog.askdirectory()
        if folder:
            script_folder_var.set(folder)
            load_scripts(folder)

    tk.Button(root, text="Pilih Folder Script", command=pilih_folder).pack(pady=5)

    script_frame = tk.Frame(root)
    script_frame.pack(fill='both', expand=True, pady=5)

    status_label = tk.Label(root, textvariable=status_var, fg='blue')
    status_label.pack(pady=5)

    def update_status(text):
        q.put(("status", text))

    def load_scripts(folder):
        for widget in script_frame.winfo_children():
            widget.destroy()
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.js','.jsx'))]
        if not files:
            update_status("Tidak ada file js/jsx ditemukan.")
            return
        update_status(f"{len(files)} script ditemukan.")
        try:
            icon = tk.PhotoImage(file=button_icon_path)
        except:
            icon = None
        for f in files:
            btn = tk.Button(
                script_frame, text=f, image=icon, compound="left",
                bg=button_color, fg="white", relief="raised", border=5,
                command=lambda file=f: jalankan_script(folder, file)
            )
            btn.image = icon
            btn.pack(pady=2, fill='x', padx=10)

    def jalankan_script(folder, filename):
        def task():
            update_status(f"Menjalankan: {filename}")
            script_path = os.path.join(folder, filename)
            try:
                subprocess.run([photoshop_exe, script_path], check=True, shell=False)
                update_status(f"Selesai: {filename}")
            except Exception as e:
                update_status(f"Gagal menjalankan: {filename} - {e}")
        threading.Thread(target=task, daemon=True).start()

    def cek_photoshop():
        def task():
            update_status("Mengecek proses Photoshop...")
            found = any(
                any(name in p.name().lower() for name in ["photoshop.exe", "photoshop 2020.exe"])
                for p in psutil.process_iter()
            )
            if found:
                update_status("✅ Photoshop aktif")
            else:
                update_status("❌ Photoshop tidak aktif")
        threading.Thread(target=task, daemon=True).start()

    def ubah_path_photoshop():
        win = tk.Toplevel(root)
        win.title("Ubah Path Photoshop")
        win.geometry("500x150")
        tk.Label(win, text="Pilih Path Photoshop.exe:").pack(pady=5)
        e = tk.Entry(win, width=60)
        e.insert(0, photoshop_exe)
        e.pack(pady=5)
        def browse():
            file = filedialog.askopenfilename(filetypes=[("Executable","*.exe")])
            if file:
                e.delete(0, tk.END)
                e.insert(0, file)
        tk.Button(win, text="Pilih File", command=browse).pack(pady=5)
        def save():
            nonlocal photoshop_exe
            photoshop_exe = e.get()
            config['photoshop_exe'] = photoshop_exe
            save_config(config)
            win.destroy()
            update_status(f"Path Photoshop diubah: {photoshop_exe}")
        tk.Button(win, text="Simpan", command=save).pack(pady=5)

    def pengaturan_tombol():
        win = tk.Toplevel(root)
        win.title("Pengaturan Tombol Script")
        tk.Label(win, text="Warna Tombol:").pack(pady=5)
        def pilih_warna():
            color = colorchooser.askcolor()[1]
            if color:
                config['button_color'] = color
                save_config(config)
                update_status(f"Warna tombol diubah: {color}")
        tk.Button(win, text="Pilih Warna", command=pilih_warna).pack(pady=5)

        tk.Label(win, text="Icon Tombol (PNG):").pack(pady=5)
        def pilih_icon():
            file = filedialog.askopenfilename(filetypes=[("PNG files","*.png")])
            if file:
                config['button_icon'] = file
                save_config(config)
                update_status(f"Icon tombol diubah.")
        tk.Button(win, text="Pilih Icon", command=pilih_icon).pack(pady=5)

        def refresh():
            nonlocal button_color, button_icon_path
            button_color = config.get("button_color", "#4CAF50")
            button_icon_path = config.get("button_icon", "icon.png")
            save_config(config)
            update_status("Pengaturan diterapkan dan disimpan.")
        tk.Button(win, text="Refresh & Simpan", command=refresh).pack(pady=5)

    def matikan_popup_script():
        try:
            os.makedirs(os.path.dirname(PS_USERCONFIG_PATH), exist_ok=True)
            with open(PS_USERCONFIG_PATH, 'w') as f:
                f.write("WarnRunningScripts 0")
            messagebox.showinfo("Sukses", "Berhasil menambahkan WarnRunningScripts 0. Restart Photoshop untuk menerapkan.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menulis file PSUserConfig.txt: {e}")

    def lihat_lokasi_userconfig():
        messagebox.showinfo("Lokasi PSUserConfig.txt", f"File seharusnya ada di:\n{PS_USERCONFIG_PATH}")

    tk.Button(root, text="Cek Photoshop Aktif", command=cek_photoshop).pack(pady=5)

    def check_queue():
        try:
            while True:
                msg = q.get_nowait()
                if msg[0]=="status":
                    status_var.set(f"Status: {msg[1]}")
        except queue.Empty:
            pass
        root.after(100, check_queue)

    check_queue()

    if master is None:
        root.mainloop()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

if __name__=="__main__":
    create_gui()