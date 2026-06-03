import os
import shutil
import winreg
import tkinter as tk
from tkinter import messagebox, ttk

def get_installed_programs():
    programs = []

    # Путь к разделам с установленными программами
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for root, path in reg_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0] if 'InstallLocation' in [winreg.EnumValue(subkey, j)[0] for j in range(winreg.QueryInfoKey(subkey)[1])] else ""
                            programs.append((name, install_location))
                    except:
                        continue
        except:
            continue

    return sorted(programs, key=lambda x: x[0].lower())

def delete_folder(path):
    if path and os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Ошибка при удалении {path}: {e}")

def uninstall_selected():
    selected = tree.selection()
    if not selected:
        return

    name = tree.item(selected[0])["values"][0]
    path = tree.item(selected[0])["values"][1]

    confirm = messagebox.askyesno("Удаление", f"Удалить {name}?")

    if confirm:
        delete_folder(path)
        deep = messagebox.askyesno("Полное удаление", f"Удалить все остатки {name}?")
        if deep:
            # Попытка удалить данные в пользовательских каталогах
            user_paths = [
                os.path.join(os.environ['APPDATA'], name),
                os.path.join(os.environ['LOCALAPPDATA'], name),
                os.path.join(os.environ['USERPROFILE'], "Documents", name),
                os.path.join(os.environ['PROGRAMDATA'], name)
            ]
            for p in user_paths:
                delete_folder(p)
            messagebox.showinfo("Готово", f"{name} полностью удалена.")
        else:
            messagebox.showinfo("Удалено", f"{name} удалена частично.")

        # Обновление списка
        update_program_list()

def update_program_list():
    tree.delete(*tree.get_children())
    programs = get_installed_programs()
    for name, path in programs:
        tree.insert("", "end", values=(name, path if path else "Не указано"))

# GUI
root = tk.Tk()
root.title("Uninstaller на Python")
root.geometry("800x500")

tree = ttk.Treeview(root, columns=("Программа", "Путь"), show="headings")
tree.heading("Программа", text="Программа")
tree.heading("Путь", text="Путь установки")
tree.pack(fill=tk.BOTH, expand=True)

btn = tk.Button(root, text="Удалить выбранную", command=uninstall_selected)
btn.pack(pady=10)

update_program_list()

root.mainloop()
