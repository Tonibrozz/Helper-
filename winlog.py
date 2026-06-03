import tkinter as tk
from tkinter import messagebox
import winreg

WINLOGON_KEY_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

def read_value(name):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, WINLOGON_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except FileNotFoundError:
        return ""
    except PermissionError:
        return "⛔ Нет доступа"

def write_value(name, value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, WINLOGON_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            return True
    except PermissionError:
        return False

def update_values():
    shell_val.set(read_value("Shell"))
    userinit_val.set(read_value("Userinit"))

def save_values():
    s = shell_val.get()
    u = userinit_val.get()

    if not s or not u:
        messagebox.showwarning("Ошибка", "Оба поля должны быть заполнены.")
        return

    shell_result = write_value("Shell", s)
    userinit_result = write_value("Userinit", u)

    if shell_result and userinit_result:
        messagebox.showinfo("Готово", "Параметры успешно обновлены.")
    else:
        messagebox.showerror("Ошибка", "Не удалось сохранить. Запустите от имени администратора.")

# Интерфейс
root = tk.Tk()
root.title("Winlogon автозагрузка")
root.geometry("600x250")

shell_val = tk.StringVar()
userinit_val = tk.StringVar()

tk.Label(root, text="Shell (обычно explorer.exe):").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=shell_val, width=80).pack(padx=10)

tk.Label(root, text="Userinit (обычно userinit.exe,):").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=userinit_val, width=80).pack(padx=10)

tk.Button(root, text="💾 Сохранить изменения", command=save_values).pack(pady=10)
tk.Button(root, text="🔄 Обновить значения", command=update_values).pack()

update_values()
root.mainloop()
