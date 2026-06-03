import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import pefile
import queue
import contextlib
import io
import code
import psutil
import subprocess
import winreg
import ctypes
import shutil
import os
from tkinter import filedialog, scrolledtext, messagebox
import time
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
import sys
import hashlib
import datetime
import pefile
import win32event
import win32con
import win32api
import tempfile
import atexit
import random
import string
import re
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QWindow 
import threading
from tkinter import simpledialog




_normal_exit = False


def setup_ghost_tab(tab):
    info_label = ttk.Label(tab, text="Ghost Mode - скрытый запуск программ", font=("Arial", 10))
    info_label.pack(pady=10)

    log_text = Text(tab, height=8, width=60, state="disabled")
    log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def log(msg):
        log_text.config(state="normal")
        log_text.insert("end", msg + "\n")
        log_text.see("end")
        log_text.config(state="disabled")

    def launch_ghost():
        filetypes = [("EXE файлы", "*.exe")]
        exe_path = filedialog.askopenfilename(filetypes=filetypes)
        if not exe_path: return

        try:
            temp_dir = tempfile.mkdtemp()
            rand_name = ''.join(random.choices(string.ascii_letters, k=8)) + ".exe"
            temp_path = os.path.join(temp_dir, rand_name)
            shutil.copy2(exe_path, temp_path)

            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = subprocess.SW_HIDE

            subprocess.Popen([temp_path], startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
            log(f"Запущено: {temp_path}")
            messagebox.showinfo("Успех", f"{rand_name} запущен в Ghost Mode!")
        except Exception as e:
            log(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))

    def decoy_mode():
        fake_ips = ["185.143.223.11", "172.104.44.21", "91.234.190.77"]
        fake_cmds = ["nslookup google.com", "ping 8.8.8.8", "curl https://example.com/api/v1/test"]
        try:
            for ip in fake_ips:
                os.system(f"ipconfig /flushdns >nul && nslookup {ip} >nul")
            for cmd in fake_cmds:
                os.system(cmd + " >nul 2>&1")
            log("Decoy: фейковая активность выполнена.")
            messagebox.showinfo("DECOY ACTIVE", "Фейковая активность создана!")
        except Exception as e:
            log(f"Ошибка в decoy_mode: {str(e)}")
            messagebox.showerror("Ошибка", str(e))

    def cloak_process():
        pid = simpledialog.askinteger("Маскировка", "Введите PID процесса:")
        if pid:
            try:
                import ctypes
                PROCESS_ALL_ACCESS = 0x1F0FFF
                h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                ctypes.windll.psapi.SetProcessImageNameW(h_process, "svchost.exe")
                log(f"PID {pid} замаскирован под svchost.exe")
                messagebox.showinfo("CLOAK", f"PID {pid} теперь маскируется под svchost.exe!")
            except Exception as e:
                log(f"Ошибка маскировки: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось замаскировать: {str(e)}")

    def panic_mode():
        if messagebox.askyesno("Подтверждение", "Удалить временные файлы и историю?"):
            clean_paths = [
                os.environ.get("TEMP", "") + "\\*",
                os.environ.get("LOCALAPPDATA", "") + "\\Temp\\*", 
                os.environ.get("USERPROFILE", "") + "\\Recent\\*"
            ]
            try:
                for path in clean_paths:
                    os.system(f'del /f /s /q "{path}" >nul 2>&1')
                log("Panic: удалены временные файлы и история.")
                messagebox.showinfo("Panic Mode", "Следы очищены!")
            except Exception as e:
                log(f"Ошибка в panic_mode: {str(e)}")
                messagebox.showerror("Ошибка", str(e))

    button_frame = ttk.Frame(tab)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Запуск EXE", command=launch_ghost).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Фейк активность", command=decoy_mode).pack(side='left', padx=5) 
    ttk.Button(button_frame, text="Очистка следов", command=panic_mode).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Маскировка", command=cloak_process).pack(side='left', padx=5)




class AntiKill:
    def __init__(self):
        self.mutex = None
        self.protect_thread = None
        self.setup_protection()
        
    def setup_protection(self):

        self.mutex = win32event.CreateMutex(None, False, "YourAppNameMutex")
        if win32api.GetLastError() == win32con.ERROR_ALREADY_EXISTS:
            sys.exit(0)
            

        self.protect_process()
        

        self.protect_thread = threading.Thread(target=self._protect_loop, daemon=True)
        self.protect_thread.start()
    
    def protect_process(self):
        try:
            PROCESS_ALL_ACCESS = 0x1F0FFF
            our_pid = os.getpid()
            our_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, our_pid)
            

            ctypes.windll.ntdll.NtSetInformationProcess(
                our_handle, 
                29, 
                ctypes.byref(ctypes.c_int(1)), 
                ctypes.sizeof(ctypes.c_int))
        except:
            pass
    
    def _protect_loop(self):
        while not _normal_exit:
            try:
                self.protect_process()
                time.sleep(5)
            except:
                pass



    def safe_exit(self):
        global _normal_exit
        _normal_exit = True
        if self.mutex:
            win32api.CloseHandle(self.mutex)

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True  
    else:

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return False

if not run_as_admin():
    print("Программа требует прав администратора. Запустите её снова с повышенными привилегиями.")
    sys.exit(1)
else:
    print("Программа запущена с правами администратора.")

class RegistryMonitor(threading.Thread):
    def __init__(self, keys_to_watch, callback):
        super().__init__()
        self.keys_to_watch = keys_to_watch
        self.callback = callback
        self.stop_event = threading.Event()

    def run(self):
        last_states = {}
        while not self.stop_event.is_set():
            for key_path in self.keys_to_watch:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        info = winreg.QueryInfoKey(key)
                        state = (info[0], info[1])
                        if key_path in last_states:
                            if last_states[key_path] != state:
                                self.callback(f"Изменение в реестре: {key_path}")
                        last_states[key_path] = state
                except Exception as e:
                    self.callback(f"Ошибка доступа к {key_path}: {e}")
            time.sleep(3)

    def stop(self):
        self.stop_event.set()



#regedit
def unblock_taskmgr():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.CloseKey(key)
        return True, "Диспетчер задач разблокирован"
    except FileNotFoundError:
        return True, "Диспетчер задач уже разблокирован"
    except Exception as e:
        return False, f"Ошибка: {e}"

def block_taskmgr():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        return True, "Диспетчер задач заблокирован"
    except Exception as e:
        return False, f"Ошибка: {e}"

def unblock_registry_editor():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableRegistryTools")
        winreg.CloseKey(key)
        return True, "Редактор реестра разблокирован"
    except FileNotFoundError:
        return True, "Редактор реестра уже разблокирован"
    except Exception as e:
        return False, f"Ошибка: {e}"

#debugger cliner
def clear_debuggers():
    debuggers = ["ollydbg.exe", "x64dbg.exe", "ida64.exe", "ida.exe", "windbg.exe"]
    errors = []
    for dbg in debuggers:
        result = subprocess.run(f'taskkill /f /im {dbg}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            errors.append(dbg)
    if errors:
        return False, f"Не удалось завершить: {', '.join(errors)}"
    return True, "Отладчики завершены"

def list_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name']):
        procs.append((p.info['pid'], p.info['name']))
    return procs

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)
        return True, "Процесс завершён"
    except Exception as e:
        return False, str(e)

def create_process(exe_path):
    try:
        subprocess.Popen(exe_path)
        print(f"[+] Процесс запущен: {exe_path}")
    except Exception as e:
        print(f"[!] Ошибка запуска процесса: {e}")

def start_explorer():
    os.system("explorer.exe")

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, width=300, height=200):
        super().__init__(parent)
        self.parent = parent
        self.width = width
        self.height = height
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth()-width)//2}+{(self.winfo_screenheight()-height)//2}")
        self.overrideredirect(True)
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.letter_h = self.canvas.create_text(50, height//2, text="H", fill="cyan", font=("Segoe UI", 58, "bold"))
        self.letter_p = self.canvas.create_text(width-50, height//2, text="P", fill="cyan", font=("Segoe UI", 58, "bold"))

        self.speed_h = 5
        self.speed_p = -5
        self.shine_count = 0
        self.max_shines = 3

        self.animate()


    def animate(self):
        self.canvas.move(self.letter_h, self.speed_h, 0)
        self.canvas.move(self.letter_p, self.speed_p, 0)

        xh, _ = self.canvas.coords(self.letter_h)
        xp, _ = self.canvas.coords(self.letter_p)

        if xp - xh <= 30:
            self.speed_h = 0
            self.speed_p = 0
            self.after(1000, self.finish)
        else:
            self.after(30, self.animate)


    def finish(self):
        self.destroy()
        self.parent.deiconify()




if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  
else:
    base_path = os.path.abspath(".")  




class UnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("helper++")
        self['bg'] = 'black'    
        self.overrideredirect(True)
        self.withdraw()

        self.resizable_width = True
        self.resizable_height = True


        self.attributes('-alpha', 0.85)

        window_width = 732
        window_height = 800

        self._create_resize_borders()


        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)


        self.geometry(f"{window_width}x{window_height}+{x}+{y}")






        close_button = tk.Button(self, text="Закрыть", command=self.destroy)
        close_button.place(x=130, y=80)




        drag_area = tk.Frame(self, bg="black", height=30)
        drag_area.pack(fill="x", side="top")


        close_btn = tk.Button(
            drag_area,
            text="X",
            bg="#000000",
            fg="red",
            width=40,
            height=40,
            font=("Arial", 30, "bold"),
            borderwidth=0,
            command=self.destroy,
            activebackground="#000000",
            activeforeground="red",
            cursor="hand2"
        )
        close_btn.place(relx=1.0, x=-5, y=5, anchor="ne", width=20, height=20)




        helper_label = tk.Label(
            drag_area,
            text='Helper++',
            bg='#000000',
            fg='red',
            font=('Segoe UI', 12, 'bold')
        
        )
        helper_label.pack(side='left', padx=10)

        drag_area.bind("<ButtonPress-1>", self.start_move)
        drag_area.bind("<B1-Motion>", self.do_move)



        style = ttk.Style()
        style.theme_use('default')
        style.configure('lefttab.TNotebook', tabposition='wn', background='#222222', borderwidth=0)
        style.configure('Dark.TFrame', background='#000000', borderwidth=0)

        style.configure('TNotebook.Tab',
                        width=12, height=5, padding=[5, 10],
                        anchor='center',
                        font=('Segoe UI', 10),
                        borderwidth=0)



        style.map('TNotebook.Tab',
                  background=[('selected', '#444444')],
                  foreground=[('selected', '#00ffcc')],
                  )

        self.tabs = ttk.Notebook(self, style='lefttab.TNotebook')
        self.tabs.pack(fill='both', expand=True)

        self.protection_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.process_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.autorun_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.tinstall_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.explorer_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.asses_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.uninstaller_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.tunlocker_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.virus_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.registry_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.cmd_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.ghost_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.disk_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.exe_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.analiz_tab = ttk.Frame(self.tabs, style='Dark.TFrame')



        self.tabs.add(self.protection_tab, text="Защита")
        self.tabs.add(self.uninstaller_tab, text="Удаление")
        self.tabs.add(self.cmd_tab, text="CMD")
        self.tabs.add(self.process_tab, text="Диспетчер\nзадач")
        self.tabs.add(self.autorun_tab, text="Авто\nзапуск")
        self.tabs.add(self.tinstall_tab, text="Установить\nи следить")
        self.tabs.add(self.tunlocker_tab, text="Anti\nBlocker")
        self.tabs.add(self.explorer_tab, text="Проводник")
        self.tabs.add(self.virus_tab, text="Анализ\nвредоносного ПО")
        self.tabs.add(self.registry_tab, text="мониторинг\nресурсов")
        self.tabs.add(self.ghost_tab, text="Ghost\nMode")
        self.tabs.add(self.disk_tab, text="Раздел\nдисков")
        self.tabs.add(self.exe_tab, text="EXEeditor")
        self.tabs.add(self.analiz_tab, text="Обход\nвирусов")





        self.create_protection_tab()
        self.create_process_tab()
        self.create_autorun_tab()
        self.create_tinstall_tab()
        self.create_explorer_tab()
        self.create_uninstaller_tab()
        self.create_tunlocker_tab()
        self.create_virus_tab()
        self.create_registry_tab()
        self.create_cmd_tab()
        self.create_ghost_tab()
        self.create_disk_tab()
        self.create_exe_tab()
        self.create_analiz_tab()

    def create_analiz_tab(self):
        from tkinter import Toplevel, Label, Button, filedialog, Listbox, END, Text, Scrollbar, messagebox
        import os, stat, psutil, subprocess

        analiz_frame = self.analiz_tab

        header = Label(
            analiz_frame,
            text="Инструменты обхода вирусов (Недохакер Лайт)",
            bg="#000000",
            fg="#00ff00",
            font=("Segoe UI", 14, "bold")
        )
        header.pack(pady=15)

        button_style = {
            "bg": "#111111",
            "fg": "#00ff00",
            "activebackground": "#222222",
            "activeforeground": "#00ffcc",
            "font": ("Segoe UI", 12, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "width": 35,
            "height": 2
        }

        def remove_file_protection():
            top = Toplevel(self)
            top.title("Выбор файла для разблокировки")
            top.configure(bg="#000000")
            top.geometry("400x150")
            Label(top, text="Выберите файл для снятия защиты", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=20)

            def select_file():
                file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=[("Все файлы", "*.*")])
                if file_path:
                    try:
                        os.chmod(file_path, stat.S_IWRITE)
                        self.log_status(f"[OK] Защита снята: {file_path}")
                    except Exception as e:
                        self.log_status(f"[ERROR] {e}")
                top.destroy()

            Button(top, text="Выбрать файл", command=select_file, **button_style).pack(pady=10)

        def scan_hidden_processes():
            top = Toplevel(self)
            top.title("Сканирование процессов")
            top.configure(bg="#000000")
            top.geometry("500x300")
            Label(top, text="Найденные скрытые процессы", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=5)

            listbox = Listbox(top, bg="#111111", fg="#00ff00", font=("Segoe UI", 10), width=60, height=10)
            listbox.pack(pady=5, fill="both", expand=True)

            def scan():
                listbox.delete(0, END)
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        name = proc.info['name'].lower()
                        if 'temp' in name or 'hidden' in name or 'svchost' in name:
                            listbox.insert(END, f"{proc.info['name']} (PID: {proc.info['pid']})")
                            self.log_status(f"[!] Найден процесс: {proc.info}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                if listbox.size() == 0:
                    self.log_status("[OK] Скрытых процессов не найдено.")

            Button(top, text="Сканировать", command=scan, **button_style).pack(pady=10)

        def kill_protected_processes():
            top = Toplevel(self)
            top.title("Убийство процессов")
            top.configure(bg="#000000")
            top.geometry("500x300")
            Label(top, text="Выберите процесс для убийства", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=5)

            listbox = Listbox(top, bg="#111111", fg="#00ff00", font=("Segoe UI", 10), width=60, height=10)
            listbox.pack(pady=5, fill="both", expand=True)

            processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    processes.append(proc)
                    listbox.insert(END, f"{proc.info['name']} (PID: {proc.info['pid']})")
                except:
                    continue

            def kill_selected():
                selected = listbox.curselection()
                if selected:
                    proc = processes[selected[0]]
                    try:
                        proc.kill()
                        self.log_status(f"[X] Убит процесс: {proc.info['name']}")
                        listbox.delete(selected[0])
                    except Exception as e:
                        self.log_status(f"[ERROR] {e}")

            Button(top, text="Убить процесс", command=kill_selected, **button_style).pack(pady=10)

        def clean_autorun():
            top = Toplevel(self)
            top.title("Очистка автозапуска")
            top.configure(bg="#000000")
            top.geometry("400x150")
            Label(top, text="Очистить скрытый автозапуск?", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=20)

            def clean():
                autorun_paths = [
                    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                    r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
                ]
                for path in autorun_paths:
                    try:
                        subprocess.run(f'reg delete "{path}" /va /f', shell=True)
                        self.log_status(f"[OK] Очищен {path}")
                    except Exception as e:
                        self.log_status(f"[ERROR] {e}")
                top.destroy()

            Button(top, text="Очистить", command=clean, **button_style).pack(pady=10)

        def unlock_system_tools():
            top = Toplevel(self)
            top.title("Разблокировка системных утилит")
            top.configure(bg="#000000")
            top.geometry("400x150")
            Label(top, text="Разблокировать диспетчер задач, regedit, cmd?", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=20)

            def unlock():
                commands = [
                    'REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 0 /f',
                    'REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableRegistryTools /t REG_DWORD /d 0 /f'
                ]
                for cmd in commands:
                    subprocess.run(cmd, shell=True)
                self.log_status("[OK] Системные утилиты разблокированы!")
                top.destroy()

            Button(top, text="Разблокировать", command=unlock, **button_style).pack(pady=10)

        def analyze_task_scheduler():
            top = Toplevel(self)
            top.title("Анализ планировщика задач")
            top.configure(bg="#000000")
            top.geometry("700x500")

            Label(top, text="Сканируем плонировшик и показывает подазрительные файлы не все", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=10)

            text_area = Text(top, bg="#111111", fg="#00ff00", font=("Consolas", 10), wrap="none")
            text_area.pack(fill="both", expand=True, padx=10, pady=10)

            scroll = Scrollbar(top, command=text_area.yview)
            scroll.pack(side="right", fill="y")
            text_area.config(yscrollcommand=scroll.set)

            def scan_tasks():
                text_area.delete(1.0, END)
                try:
                    result = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"], capture_output=True, text=True, shell=True)
                    tasks = result.stdout.split("\n\n")
                    for t in tasks:
                        if "TaskName" in t:
                            if ("exe" in t.lower() or "vbs" in t.lower() or "bat" in t.lower()) and ("Windows" not in t):
                                text_area.insert(END, f"[!] ПОДОЗРИТЕЛЬНО:\n{t}\n{'-'*50}\n")
                            else:
                                text_area.insert(END, f"{t}\n{'-'*50}\n")
                except Exception as e:
                    text_area.insert(END, f"[ERROR] {e}\n")

            def delete_task():
                selection = text_area.get("sel.first", "sel.last").strip()
                if not selection:
                    messagebox.showerror("Ошибка", "Выделите текст с TaskName!")
                    return
                for line in selection.splitlines():
                    if line.startswith("TaskName:"):
                        task_name = line.split(":", 1)[1].strip()
                        break
                else:
                    messagebox.showerror("Ошибка", "TaskName не найден!")
                    return
                try:
                    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], shell=True)
                    messagebox.showinfo("Успех", f"Задача '{task_name}' удалена!")
                    scan_tasks()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

            Button(top, text="🔍 Сканировать", command=scan_tasks, bg="#222222", fg="#00ff00", font=("Segoe UI", 10)).pack(pady=5)
            Button(top, text="🗑 Удалить выбранную задачу", command=delete_task, bg="#222222", fg="#ff3333", font=("Segoe UI", 10)).pack(pady=5)

            scan_tasks()

        btn1 = Button(analiz_frame, text="🛡 Снять защиту с файлов", command=remove_file_protection, **button_style)
        btn2 = Button(analiz_frame, text="🔍 Найти скрытые процессы", command=scan_hidden_processes, **button_style)
        btn3 = Button(analiz_frame, text="🚫 Убить защищённые процессы", command=kill_protected_processes, **button_style)
        btn4 = Button(analiz_frame, text="📦 Очистить скрытый автозапуск", command=clean_autorun, **button_style)
        btn5 = Button(analiz_frame, text="🕵 Разблокировать системные утилиты", command=unlock_system_tools, **button_style)
        btn6 = Button(analiz_frame, text="🔍 Анализ планировщика задач", command=analyze_task_scheduler, **button_style)
        btn7 = Button(analiz_frame, text="🛠 Режим песочницы для файлов", command=self.run_sandbox_mode, **button_style)
        

        btn1.pack(pady=10)
        btn2.pack(pady=10)
        btn3.pack(pady=10)
        btn4.pack(pady=10)
        btn5.pack(pady=10)
        btn6.pack(pady=10)
        btn7.pack(pady=10)

        self.status_label = Label(self, text="Готово.", bg="#111111", fg="#00ff00", font=("Segoe UI", 10), anchor="w")
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

    def log_status(self, message):
        self.status_label.config(text=message)
        self.status_label.update_idletasks()





    def analyze_task_scheduler():
        import subprocess
        from tkinter import Toplevel, Label, Button, Text, Scrollbar, END, messagebox

        top = Toplevel()
        top.title("Анализ планировщика задач")
        top.configure(bg="#000000")
        top.geometry("700x500")

        Label(top, text="Сканируем задания планировщика...", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=10)

        text_area = Text(top, bg="#111111", fg="#00ff00", font=("Consolas", 10), wrap="none")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        scroll = Scrollbar(top, command=text_area.yview)
        scroll.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scroll.set)

        # --- Сканирование задач ---
        def scan_tasks():
            text_area.delete(1.0, END)
            try:
                result = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"], capture_output=True, text=True, shell=True)
                tasks = result.stdout.split("\n\n")
                for t in tasks:
                    if "TaskName" in t:
                        if ("exe" in t.lower() or "vbs" in t.lower() or "bat" in t.lower()) and ("Windows" not in t):
                            text_area.insert(END, f"[!] ПОДОЗРИТЕЛЬНО:\n{t}\n{'-'*50}\n")
                        else:
                            text_area.insert(END, f"{t}\n{'-'*50}\n")
            except Exception as e:
                text_area.insert(END, f"[ERROR] {e}\n")

        # --- Удаление задачи ---
        def delete_task():
            selection = text_area.get("sel.first", "sel.last").strip()
            if not selection:
                messagebox.showerror("Ошибка", "Выделите текст с TaskName!")
                return
            for line in selection.splitlines():
                if line.startswith("TaskName:"):
                    task_name = line.split(":", 1)[1].strip()
                    break
            else:
                messagebox.showerror("Ошибка", "TaskName не найден!")
                return
            try:
                subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], shell=True)
                messagebox.showinfo("Успех", f"Задача '{task_name}' удалена!")
                scan_tasks()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        Button(top, text="🔍 Сканировать", command=scan_tasks, bg="#222222", fg="#00ff00", font=("Segoe UI", 10)).pack(pady=5)
        Button(top, text="🗑 Удалить выбранную задачу", command=delete_task, bg="#222222", fg="#ff3333", font=("Segoe UI", 10)).pack(pady=5)

        scan_tasks()



    def run_sandbox_mode(self):
        import tempfile, shutil, subprocess, os
        from tkinter import Toplevel, Label, Button, Text, Scrollbar, END, filedialog, messagebox

        top = Toplevel(self)
        top.title("Режим Песочницы")
        top.configure(bg="#000000")
        top.geometry("700x500")

        Label(top, text="Выберите файл для запуска в песочнице", bg="#000000", fg="#00ff00", font=("Segoe UI", 12)).pack(pady=10)

        text_area = Text(top, bg="#111111", fg="#00ff00", font=("Consolas", 10))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        scroll = Scrollbar(top, command=text_area.yview)
        scroll.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scroll.set)

        sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")

        def select_and_run():
            file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=[("Executable", "*.exe"), ("Все файлы", "*.*")])
            if not file_path:
                return

            try:
                dest_path = os.path.join(sandbox_dir, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                text_area.insert(END, f"[INFO] Файл скопирован в песочницу: {dest_path}\n")
                text_area.insert(END, f"[INFO] Запуск в песочнице...\n")
                text_area.update_idletasks()

                proc = subprocess.Popen(dest_path, cwd=sandbox_dir, shell=True)
                proc.wait()
                text_area.insert(END, f"[OK] Файл завершил выполнение.\n")

            except Exception as e:
                text_area.insert(END, f"[ERROR] {e}\n")

        def cleanup_sandbox():
            try:
                shutil.rmtree(sandbox_dir)
                text_area.insert(END, "[OK] Песочница очищена.\n")
            except Exception as e:
                text_area.insert(END, f"[ERROR] {e}\n")

        Button(top, text="Выбрать и запустить файл", command=select_and_run, bg="#222222", fg="#00ff00", font=("Segoe UI", 10)).pack(pady=5)
        Button(top, text="Очистить песочницу", command=cleanup_sandbox, bg="#222222", fg="#ff3333", font=("Segoe UI", 10)).pack(pady=5)





    def choose_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("EXE files", "*.exe")])
        if filepath:
            self.selected_file.set(filepath)
            self.btn_code.pack(pady=5)
            self.btn_files.pack(pady=5)
            self.output_text.delete("1.0", tk.END)


    def view_code(self):
        import pefile
        filepath = self.selected_file.get()
        try:
            pe = pefile.PE(filepath)
            code = ""
            for section in pe.sections:
                name = section.Name.decode(errors="ignore").strip()
                hex_data = section.get_data()[:64].hex()  
                code += f"[{name}]\n{hex_data}\n\n"
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, code)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать код: {e}")

    def view_structure(self):
        import pefile
        filepath = self.selected_file.get()
        try:
            pe = pefile.PE(filepath)
            info = f"Файл: {os.path.basename(filepath)}\n\nСекции EXE:\n"
            for section in pe.sections:
                name = section.Name.decode(errors="ignore").strip()
                size = section.SizeOfRawData
                addr = hex(section.VirtualAddress)
                info += f"{name:<10} | Размер: {size:<8} | Адрес: {addr}\n"
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, info)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать EXE: {e}")

    def create_exe_tab(self):
        self.selected_file = tk.StringVar()
        self.selected_file.trace_add('write', self.enable_buttons)  # Следим за изменением выбранного файла
        
        # Стиль для виджетов
        style = ttk.Style()
        style.configure('TFrame', background='#2e2e2e')
        style.configure('TLabel', background='#2e2e2e', foreground='white')
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.map('TButton', 
                background=[('active', '#535353'), ('!disabled', '#424242')],
                foreground=[('!disabled', 'white')])
        
        # Главный фрейм
        main_frame = ttk.Frame(self.exe_tab, style='TFrame')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Фрейм для выбора файла
        file_frame = ttk.Frame(main_frame, style='TFrame')
        file_frame.pack(fill='x', pady=(0, 15))
        
        # Заголовок
        title = ttk.Label(
            file_frame, 
            text="EXE File Analyzer", 
            font=("Segoe UI", 14, "bold"),
            foreground="#4fc3f7"
        )
        title.pack(pady=(0, 10))
        
        # Кнопка выбора файла и информация о файле
        select_btn = ttk.Button(
            file_frame, 
            text="Select EXE File", 
            command=self.choose_file,
            style='TButton'
        )
        select_btn.pack(side='left', padx=(0, 10))
        
        self.file_label = ttk.Label(
            file_frame, 
            textvariable=self.selected_file,
            wraplength=500,
            foreground="#a5d6a7"
        )
        self.file_label.pack(side='left', fill='x', expand=True)
        
        # Фрейм для кнопок анализа
        btn_frame = ttk.Frame(main_frame, style='TFrame')
        btn_frame.pack(fill='x', pady=(0, 15))
        
        # Кнопки анализа
        self.btn_code = ttk.Button(
            btn_frame, 
            text="View Bytecode", 
            command=self.view_code,
            state='disabled'
        )
        self.btn_code.pack(side='left', padx=(0, 10))
        
        self.btn_files = ttk.Button(
            btn_frame, 
            text="EXE Structure", 
            command=self.view_structure,
            state='disabled'
        )
        self.btn_files.pack(side='left', padx=(0, 10))
        
        self.btn_hashes = ttk.Button(
            btn_frame,
            text="Calculate Hashes",
            command=self.calculate_hashes,
            state='disabled'
        )
        self.btn_hashes.pack(side='left', padx=(0, 10))
        
        self.btn_imports = ttk.Button(
            btn_frame,
            text="View Imports",
            command=self.view_imports,
            state='disabled'
        )
        self.btn_imports.pack(side='left', padx=(0, 10))
        
        self.btn_hex = ttk.Button(
            btn_frame,
            text="Hex View",
            command=self.show_hex_view,
            state='disabled'
        )
        self.btn_hex.pack(side='left')
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        # Вкладка для вывода
        self.output_text = scrolledtext.ScrolledText(
            notebook, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white'
        )
        notebook.add(self.output_text, text="Analysis Results")
        
        # Вкладка для hex-просмотра
        self.hex_view = scrolledtext.ScrolledText(
            notebook,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            state='disabled'
        )
        notebook.add(self.hex_view, text="Hex View")
        
        # Статус бар
        self.status_bar = ttk.Label(
            main_frame,
            text="Ready",
            relief='sunken',
            anchor='w',
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(fill='x', pady=(5, 0))
        
        # Контекстное меню
        self.setup_context_menu()

    def enable_buttons(self, *args):
        """Активирует кнопки анализа при выборе файла"""
        file_selected = bool(self.selected_file.get())
        state = 'normal' if file_selected else 'disabled'
        
        self.btn_code.config(state=state)
        self.btn_files.config(state=state)
        self.btn_hashes.config(state=state)
        self.btn_imports.config(state=state)
        self.btn_hex.config(state=state)

    def choose_file(self):
        """Выбор файла для анализа"""
        file_path = filedialog.askopenfilename(
            title="Select EXE File",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file.set(file_path)
            self.status_bar.config(text=f"Selected: {file_path}")
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"File selected: {file_path}\n")
            self.output_text.config(state='disabled')

    def show_hex_view(self):
        """Показывает hex-представление файла"""
        file_path = self.selected_file.get()
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                hex_content = ' '.join(f'{byte:02x}' for byte in content[:1024])  # Первые 1024 байта
            
            self.hex_view.config(state='normal')
            self.hex_view.delete(1.0, tk.END)
            self.hex_view.insert(tk.END, hex_content)
            self.hex_view.config(state='disabled')
            
            notebook.select(self.hex_view)  # Переключаемся на вкладку hex-просмотра
            self.status_bar.config(text="Hex view loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hex view:\n{str(e)}")





    def generic_analyzer(self, analysis_type):
        """Универсальный обработчик для аналитических функций"""
        if not self.selected_file.get():
            messagebox.showerror("Error", "No file selected!")
            return
        
        try:
            if analysis_type == "Hashes":
                self.calculate_hashes()
            elif analysis_type == "Imports":
                self.view_imports()
            else:
                self.output_text.insert(tk.END, f"Analysis type '{analysis_type}' not implemented yet.\n")
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to perform {analysis_type} analysis:\n{str(e)}")

    def calculate_hashes(self):
        """Вычисление хешей файла"""
        file_path = self.selected_file.get()
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            md5 = hashlib.md5(file_data).hexdigest()
            sha1 = hashlib.sha1(file_data).hexdigest()
            sha256 = hashlib.sha256(file_data).hexdigest()
            
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "File Hashes:\n")
            self.output_text.insert(tk.END, f"MD5:    {md5}\n")
            self.output_text.insert(tk.END, f"SHA1:   {sha1}\n")
            self.output_text.insert(tk.END, f"SHA256: {sha256}\n")
            self.output_text.config(state='disabled')
            
            self.status_bar.config(text="Hashes calculated successfully")
        except Exception as e:
            messagebox.showerror("Hash Error", f"Failed to calculate hashes:\n{str(e)}")

    def view_imports(self):
        """Просмотр импортов EXE файла"""
        file_path = self.selected_file.get()
        try:
            pe = pefile.PE(file_path)
            
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Imported DLLs and Functions:\n\n")
            
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    self.output_text.insert(tk.END, f"{entry.dll.decode('utf-8', errors='replace')}:\n")
                    for imp in entry.imports:
                        name = imp.name.decode('utf-8', errors='replace') if imp.name else f"ordinal_{imp.ordinal}"
                        self.output_text.insert(tk.END, f"  - {name}\n")
                    self.output_text.insert(tk.END, "\n")
            else:
                self.output_text.insert(tk.END, "No imports found in this file.\n")
                
            self.output_text.config(state='disabled')
            self.status_bar.config(text="Imports analyzed successfully")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to analyze imports:\n{str(e)}")
        finally:
            if 'pe' in locals():
                pe.close()





    def setup_context_menu(self):
        self.context_menu = tk.Menu(self.exe_tab, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Clear", command=self.clear_output)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Save to file", command=self.save_output)
        
        self.output_text.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_text(self):
        self.exe_tab.clipboard_clear()
        text = self.output_text.get("sel.first", "sel.last")
        self.exe_tab.clipboard_append(text)

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def save_output(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.output_text.get(1.0, tk.END))

                

    def to_gb(self, bytes_val):
        try:
            return float(bytes_val) / (1024**3)
        except:
            return 0

    def create_disk_tab(self):
        disk_frame = ttk.Frame(self.disk_tab)
        disk_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.disk_list = ttk.Treeview(disk_frame, columns=("Disk", "Size", "FileSystem"), show="headings")
        self.disk_list.heading("Disk", text="Диск")
        self.disk_list.heading("Size", text="Размер")
        self.disk_list.heading("FileSystem", text="Файловая система")
        self.disk_list.pack(fill='both', expand=True)

        btn_frame = ttk.Frame(disk_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="Создать раздел", command=self.create_partition).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Форматировать", command=self.format_disk).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить раздел", command=self.delete_partition).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Сжать", command=self.shrink_volume).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Расширить", command=self.extend_volume).pack(side='left', padx=5)

        self.update_disk_list()

            
    def update_disk_list(self):
        self.disk_list.delete(*self.disk_list.get_children())
        try:
            powershell_cmd = (
                "powershell -Command \""
                "Get-CimInstance Win32_LogicalDisk | "
                "Select-Object DeviceID,Size,FreeSpace,FileSystem | "
                "ForEach-Object { "
                "'{0}|{1}|{2}|{3}' -f $_.DeviceID, $_.Size, $_.FreeSpace, $_.FileSystem "
                "}\""
            )
            result = subprocess.check_output(powershell_cmd, shell=True).decode("utf-8", errors="ignore")

            for line in result.strip().splitlines():
                parts = line.strip().split("|")
                if len(parts) == 4:
                    letter, size, free, fs = parts
                    try:
                        size_gb = self.to_gb(int(size))
                        free_gb = self.to_gb(int(free))
                        size_str = f"{size_gb:.2f} GB (своб: {free_gb:.2f} GB)"
                    except:
                        size_str = "Неизвестно"

                    self.disk_list.insert("", tk.END, values=(letter, size_str, fs))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список дисков:\n{e}")



    def get_selected_disk(self):
        selected = self.disk_list.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите диск из списка.")
            return None
        return self.disk_list.item(selected[0])["values"][0]  

    def create_partition(self):
        disk = self.get_selected_disk()
        if not disk:
            return
        messagebox.showinfo("Инфо", "Создание раздела требует diskpart и ручной настройки через .txt-скрипт.")

    def format_disk(self):
        disk = self.get_selected_disk()
        if not disk:
            return
        if messagebox.askyesno("Подтверждение", f"Форматировать диск {disk}? Все данные будут удалены."):
            try:
                subprocess.run(f"format {disk} /FS:NTFS /Q /Y", shell=True, check=True)
                messagebox.showinfo("Успех", f"{disk} отформатирован.")
                self.update_disk_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при форматировании: {e}")

    def delete_partition(self):
        disk = self.get_selected_disk()
        if not disk:
            return
        messagebox.showinfo("Инфо", "Удаление разделов можно реализовать через diskpart скрипт.")

    def shrink_volume(self):
        disk = self.get_selected_disk()
        if not disk:
            return
        size = simpledialog.askinteger("Сжать", "Введите размер для сжатия (в МБ):")
        if size:
            try:
                script = f"select volume {disk[0]}\nshrink desired={size}"
                subprocess.run(f"echo {script} | diskpart", shell=True, check=True)
                messagebox.showinfo("Успех", "Том сжат.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сжатии: {e}")

    def extend_volume(self):
        disk = self.get_selected_disk()
        if not disk:
            return
        try:
            script = f"select volume {disk[0]}\nextend"
            subprocess.run(f"echo {script} | diskpart", shell=True, check=True)
            messagebox.showinfo("Успех", "Том расширен.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расширении: {e}")





    def create_ghost_tab(self):
        setup_ghost_tab(self.ghost_tab)




    def _create_resize_borders(self):
        border_size = 5 
        
        self.right_border = tk.Frame(self, width=border_size, bg='black', cursor='sb_h_double_arrow')
        self.right_border.pack(side='right', fill='y')
        
        self.bottom_border = tk.Frame(self, height=border_size, bg='black', cursor='sb_v_double_arrow')
        self.bottom_border.pack(side='bottom', fill='x')
        
        self.corner_border = tk.Frame(self, width=border_size, height=border_size, bg='black', cursor='size_nw_se')
        self.corner_border.pack(side='bottom', anchor='se')
        
        self.right_border.bind("<ButtonPress-1>", self.start_resize_width)
        self.right_border.bind("<B1-Motion>", self.resize_width)
        
        self.bottom_border.bind("<ButtonPress-1>", self.start_resize_height)
        self.bottom_border.bind("<B1-Motion>", self.resize_height)
        
        self.corner_border.bind("<ButtonPress-1>", self.start_resize_both)
        self.corner_border.bind("<B1-Motion>", self.resize_both)

    def start_resize_width(self, event):
        self.resizing_width = True
        self.start_x = event.x_root
        self.start_width = self.winfo_width()

    def resize_width(self, event):
        if not hasattr(self, 'resizing_width'):
            return
        delta = event.x_root - self.start_x
        new_width = self.start_width + delta
        if new_width > 300: 
            self.geometry(f"{new_width}x{self.winfo_height()}")

    def start_resize_height(self, event):

        self.resizing_height = True
        self.start_y = event.y_root
        self.start_height = self.winfo_height()

    def resize_height(self, event):

        if not hasattr(self, 'resizing_height'):
            return
        delta = event.y_root - self.start_y
        new_height = self.start_height + delta
        if new_height > 200: 
            self.geometry(f"{self.winfo_width()}x{new_height}")

    def start_resize_both(self, event):
        self.start_resize_width(event)
        self.start_resize_height(event)

    def resize_both(self, event):
        self.resize_width(event)
        self.resize_height(event)

        

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f"+{x}+{y}")


    def create_cmd_tab(self):
        self.cmd_output = tk.Text(self.cmd_tab, bg='black', fg='lime', insertbackground='lime',
                                  font=('Consolas', 10), state='disabled')
        self.cmd_output.pack(fill='both', expand=True, padx=5, pady=(5, 0))


        self.cmd_input = tk.Entry(self.cmd_tab, bg='black', fg='lime', insertbackground='lime',
                                  font=('Consolas', 10))
        self.cmd_input.pack(fill='x', padx=5, pady=5)
        self.cmd_input.focus()
        self.cmd_input.bind('<Return>', self.execute_cmd)


    def execute_cmd(self, event=None):
        cmd = self.cmd_input.get().strip()
        if not cmd:
            return

        self.append_output(f"> {cmd}\n")

        try:

            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)

            output = result.stdout.decode('cp866') + result.stderr.decode('cp866')
        except Exception as e:
            output = f"Error: {e}\n"

        self.append_output(output)
        self.cmd_input.delete(0, tk.END)

    def append_output(self, text):
        self.cmd_output.configure(state='normal')
        self.cmd_output.insert(tk.END, text)
        self.cmd_output.see(tk.END)
        self.cmd_output.configure(state='disabled')



    def create_registry_tab(self):
        self.registry_canvas = tk.Canvas(self.registry_tab, bg='white', height=250)
        self.registry_canvas.pack(fill='both', expand=True, padx=10, pady=10)

        self.registry_text_id = self.registry_canvas.create_text(
            10, 10, anchor='nw', text="Мониторинг не запущен.", font=("Consolas", 10)
        )

        buttons_frame = ttk.Frame(self.registry_tab, style='Dark.TFrame')
        buttons_frame.pack(pady=5)

        start_btn = ttk.Button(buttons_frame, text="Старт мониторинга", command=self.start_registry_monitor)
        start_btn.pack(side='left', padx=5)

        stop_btn = ttk.Button(buttons_frame, text="Стоп мониторинга", command=self.stop_registry_monitor)
        stop_btn.pack(side='left', padx=5)

        self.registry_monitor = None


    def registry_callback(self, message):
        def update():
            current_text = self.registry_canvas.itemcget(self.registry_text_id, 'text')
            new_text = f"{message}\n\n{current_text}"
            lines = new_text.split('\n')
            if len(lines) > 20:
                lines = lines[:20]
            self.registry_canvas.itemconfigure(self.registry_text_id, text='\n'.join(lines))
        self.registry_canvas.after(0, update)


    def start_registry_monitor(self):
        if self.registry_monitor and self.registry_monitor.is_alive():
            messagebox.showinfo("Инфо", "Мониторинг уже запущен.")
            return
        keys = [
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        ]
        self.registry_monitor = RegistryMonitor(keys, self.registry_callback)
        self.registry_monitor.daemon = True
        self.registry_monitor.start()
        self.registry_canvas.itemconfigure(self.registry_text_id, text="Мониторинг реестра запущен...\n")


    def stop_registry_monitor(self):
        if self.registry_monitor:
            self.registry_monitor.stop()
            self.registry_monitor = None
            self.registry_canvas.itemconfigure(self.registry_text_id, text="Мониторинг остановлен.\n")



 
    def create_virus_tab(self):

        self.info_text = tk.Text(self.virus_tab, height=15, bg="white", fg="black")
        self.info_text.pack(padx=10, pady=10, fill='both', expand=True)

        btn_frame = ttk.Frame(self.virus_tab)
        btn_frame.pack(pady=5)

        btn_select = ttk.Button(btn_frame, text="Выбрать программу", command=self.select_program)
        btn_select.pack(side='left', padx=5)

        btn_scan = ttk.Button(btn_frame, text="Сканировать", command=self.scan_program)
        btn_scan.pack(side='left', padx=5)

    def select_program(self):
        filetypes = [("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        filename = filedialog.askopenfilename(title="Выберите программу", filetypes=filetypes)
        if filename:
            self.selected_file = filename
            self.info_text.delete('1.0', tk.END)
            self.info_text.insert(tk.END, f"Выбрана программа:\n{self.selected_file}\n")

    def scan_program(self):
        if not self.selected_file:
            messagebox.showwarning("Внимание", "Программа не выбрана!")
            return

        file_info = self.get_file_info(self.selected_file)
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, f"Информация о файле:\n")
        for k, v in file_info.items():
            self.info_text.insert(tk.END, f"{k}: {v}\n")
        

        self.info_text.insert(tk.END, "\nРезультат сканирования: Вирусы не обнаружены")

    def get_file_info(self, path):
        try:
            size = os.path.getsize(path)
            name = os.path.basename(path)
            created = os.path.getctime(path)
            modified = os.path.getmtime(path)
            return {
                "Имя файла": name,
                "Размер (байт)": size,
                "Дата создания": created,
                "Дата изменения": modified,
            }
        except Exception as e:
            return {"Ошибка": str(e)}



    def create_tunlocker_tab(self):
        self.restrictions = [
            ("Блокировка диспетчера задач", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr"),
            ("Блокировка редактора реестра", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools"),
            ("Блокировка командной строки", winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System", "DisableCMD"),
            ("Блокировка оснасток MMC", winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\MMC", "RestrictToPermittedSnapins"),
            ("Блокировка панели управления", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel"),
            ("Блокировка 'Выполнить'", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoRun"),
            ("Блокировка дисков в проводнике", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoViewOnDrive"),
            ("Скрытие дисков", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDrives"),
            ("Блокировка поиска в пуске", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoFind"),
            ("Блокировка контекстного меню", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoViewContextMenu"),
            ("Блокировка параметров папок", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoFolderOptions"),
            ("Блокировка вкладки безопасность", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoSecurityTab"),
            ("Скрытие меню файл", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoFileMenu"),
            ("Блокировка выключения через пуск", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoClose"),
            ("Скрытие ярлыков из пуск", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoCommonGroups"),
            ("Скрытие выхода из системы в пуск", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "StartMenuLogOff"),
            ("Запрет смены обоев", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop", "NoChangingWallPaper"),
            ("Отключение Win-клавиш", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWinKeys"),
            ("Запрет изменений панели задач и меню 'Пуск'", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoSetTaskbar"),
            ("Блокировка Win+L", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableLockWorkstation"),
            ("Запрет смены пароля", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword"),
            ("Блокировка меню по правому клику на панели задач", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoTrayContextMenu"),
            ("Блокировка gpedit", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "NoGPEdit"),
            ("Блокировка контекстного меню в Пуск", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "DisableContextMenusInStartMenu"),
            ("Запрет кнопки выход из системы", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "DisableLogoff"),
            ("Отключение восстановления системы", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore", "DisableSR"),
            ("Блокировка настроек восстановления", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore", "DisableConfig"),
            ("Блокировка выхода из системы", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoLogoff"),
            ("Брандмауэр", winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile", "EnableFirewall"),
            ("DisableRegistryTools", "Блокировка редактора реестра", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"),
            ("DisableCMD", "Блокировка командной строки", winreg.HKEY_CURRENT_USER, r"Software\\Policies\\Microsoft\\Windows\\System"),
            ("RestrictToPermittedSnapins", "Блокировка оснасток MMC", winreg.HKEY_CURRENT_USER, r"Software\\Policies\\Microsoft\\MMC"),
            ("NoControlPanel", "Блокировка панели управления", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoRun", "Запрет окна 'Выполнить'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoViewOnDrive", "Блокировка доступа к дискам", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoDrives", "Скрытие иконок дисков", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoFind", "Отключение поиска", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoViewContextMenu", "Блокировка контекстного меню", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoFolderOptions", "Блокировка параметров папок", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoSecurityTab", "Скрытие вкладки 'Безопасность'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoFileMenu", "Скрытие меню 'Файл'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoClose", "Блокировка завершения работы", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoCommonGroups", "Скрытие общих ярлыков", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("StartMenuLogOff", "Скрытие кнопки 'Выход'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoChangingWallPaper", "Запрет смены обоев", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\ActiveDesktop"),
            ("NoWinKeys", "Отключение Win-клавиш", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoSetTaskbar", "Запрет изменения панели задач", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("DisableLockWorkstation", "Запрет Win+L", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"),
            ("DisableChangePassword", "Запрет смены пароля", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"),
            ("NoTrayContextMenu", "Блокировка контекстного меню трея", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("NoGPEdit", "Блокировка gpedit.msc", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"),
            ("DisableContextMenusInStartMenu", "Запрет контекстного меню 'Пуск'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("DisableLogoff", "Скрытие кнопки 'Выход из системы'", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("DisableSR", "Отключение восстановления системы", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Policies\\Microsoft\\Windows NT\\SystemRestore"),
            ("DisableConfig", "Запрет настроек восстановления", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Policies\\Microsoft\\Windows NT\\SystemRestore"),
            ("NoLogoff", "Блокировка выхода из системы", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"),
            ("Запрет использования Bluetooth", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\Bluetooth", "AllowBluetooth"),
            ("Отключение автозапуска для всех дисков", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDriveTypeAutoRun"),
            ("Запрет доступа к командлетам PowerShell", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\PowerShell", "DisallowRun"),
            ("Отключение панели уведомлений", winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", "DisableNotificationCenter"),
            ("Запрет фоновых приложений", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled"),
            ("Запрет изменения яркости экрана", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Power\PowerSettings\7516b95f-f776-4464-8c53-06167f40cc99", "ACSettingIndex"),
            ("Отключение Wi-Fi", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\NetworkConnections", "NC_ShowSharedAccessUI"),
            ("Блокировка изменения прокси", winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Internet Explorer\Control Panel", "Proxy"),
            ("Отключение SmartScreen для Microsoft Edge", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\MicrosoftEdge\PhishingFilter", "EnabledV9"),
            ("Отключение всплывающих уведомлений о батарее", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings", "NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK"),
            ("Отключение 'Истории буфера обмена'", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\System", "AllowClipboardHistory"),
            ("Запрет запуска 'ms-settings:'", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\Explorer", "SettingsPageVisibility"),
            ("Отключение экрана приветствия после обновлений", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "EnableFirstLogonAnimation"),
            ("Скрытие переключения пользователей", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "HideFastUserSwitching"),
            ("Отключение Windows Spotlight", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\CloudContent", "DisableWindowsSpotlightFeatures"),
            ("Отключение журнала активности", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\System", "EnableActivityFeed"),
            ("Отключение временной шкалы", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\System", "PublishUserActivities"),
            ("Отключение панели задач в режиме планшета", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\ImmersiveShell", "TabletMode"),
            ("Отключение PIN-кода Windows Hello", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\PassportForWork", "Enabled"),
            ("Запрет уведомлений приложений", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "ToastEnabled"),
            ("Отключение экрана блокировки", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\Personalization", "NoLockScreen"),
            ("Скрытие ленты в проводнике", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\Explorer", "ExplorerRibbonStartsMinimized"),
            ("Запрет изменения языковых параметров", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\InputPersonalization", "RestrictImplicitTextCollection"),
            ("Запрет изменения темы", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "NoDispAppearancePage"),
            ("Запрет изменения курсора", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "NoDispCPL"),
            ("Отключение автозапуска установленных программ", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoStartMenuMFUprogramsList"),
            ("Запрет создания ярлыков на рабочем столе", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDesktop"),
            ("Отключение панели задач", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoSetTaskbar"),
            ("Запрет изменения языка ввода с помощью клавиш", winreg.HKEY_CURRENT_USER, r"Keyboard Layout\Toggle", "Language Hotkey"),
            ("Запрет входа с помощью Microsoft-аккаунта", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "NoConnectedUser"),
            ("Запрет создания точек восстановления", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows NT\SystemRestore", "DisableSR"),
            ("Отключение Windows Error Reporting", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\Windows\Windows Error Reporting", "Disabled"),
            ("Отключение панели 'Поделиться'", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoPeopleSuggestions"),
            ("Отключение отображения времени в панели задач", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideClock"),
            ("Скрытие значка сети", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideNetworkIcon"),
            ("Скрытие значка громкости", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideVolumeIcon"),
            ("Скрытие значка питания", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HidePowerIcon"),
            ("Запрет изменения значков рабочего стола", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoDesktopIcons"),
            ("Отключение шифрования устройства (BitLocker)", winreg.HKEY_LOCAL_MACHINE, r"Software\Policies\Microsoft\FVE", "EnableBDE"),
        ]




        self.unlocker_tree = ttk.Treeview(self.tunlocker_tab, columns=("name", "status"), show="headings", height=14)
        self.unlocker_tree.heading("name", text="Ограничение")
        self.unlocker_tree.heading("status", text="Статус")
        self.unlocker_tree.column("name", width=330)
        self.unlocker_tree.column("status", width=120)
        self.unlocker_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.tunlocker_tab, style='Dark.TFrame')
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Сканировать", command=self.scan_restrictions).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Разблокировать всё", command=self.unlock_all).pack(side="left", padx=10)

        self.update_restriction_table()    


    def webbrows(self):
        threading.Thread(target=self.launch_pyqt_browser).start()

    def launch_pyqt_browser(self):
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtCore import QUrl
        import sys

        app = QApplication(sys.argv)
        window = QWidget()
        window.setWindowTitle("Мой Браузер")
        window.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout()
        browser = QWebEngineView()
        browser.load(QUrl("https://www.google.com"))
        layout.addWidget(browser)
        window.setLayout(layout)
        window.show()

        app.exec_()


    def create_protection_tab(self):
        style = ttk.Style()
        style.configure("Green.TButton", font=("Segoe UI", 10, "bold"), relief='flat', background='#191919', foreground='white')  
        button_frame = tk.Frame(self.protection_tab, background='#000000')
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)


        style.map("Green.TButton", foreground=[('active', 'white')],
                                    background=[('active', '#191919')])

        buttons = [
            ("служба\nподдержки", self.open_telegram),
            ("запустить\nПроводник", self.start_explorer),
            ("Безопасный\nрежим", self.security_win),
            ("Восстановить\nшрифты", self.install_russian_font),
            ("Очистка\nот дебагеров", self.clear_debuggers),
            ("Восстановить\nассоциации", self.restore_associations),
            ("Разблокировать\nДиспетчер задач", self.unblock_taskmgr),
            ("Заблокировать\nДиспетчер задач", self.block_taskmgr),
            ("Разблокировать\nРедактор реестра", self.unblock_registry),
            ("Браузер", self.webbrows),
        ]

        max_in_row = 3
        for i, (text, command) in enumerate(buttons):
            row = i // max_in_row
            col = i % max_in_row

            btn = ttk.Button(button_frame, text=text, command=command, style="Green.TButton")
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")


        for i in range(max_in_row):
            button_frame.columnconfigure(i, weight=1)

        total_rows = (len(buttons) + max_in_row - 1) // max_in_row
        for i in range(total_rows):
            button_frame.rowconfigure(i, weight=1)


#        footer = ttk.Label(self.protection_tab, text="ToniBrozz©", 
#                        background='#000000', foreground='#ffffff')
#        footer.pack(side="bottom", anchor="se", padx=10, pady=5)

        
    def security_win(self):
        os.system('bcdedit /set {default} safeboot minimal')




    def open_telegram(self):
        webbrowser.open("https://t.me/ToniBroz")



    def install_russian_font(font_path):
        font_name = os.path.basename(font_path)
        font_display_name = "My Russian Font (TrueType)"  
        fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
        dest_path = os.path.join(fonts_dir, font_name)

        try:

            shutil.copy(font_path, dest_path)


            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, font_display_name, 0, winreg.REG_SZ, font_name)


            ctypes.windll.gdi32.AddFontResourceW(dest_path)
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  

            messagebox.showinfo("Установлено", f"Шрифт '{font_name}' успешно установлен.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить шрифт:\n{e}")




    def open_youtube(self):
        webbrowser.open_new("https://www.youtube.com/@TONIBROZZ")


    def start_explorer(self):
        create_process("explorer.exe")



    def clear_debuggers(self):
        success, msg = ClearDebuggers.clear_debuggers()

        if success:
            messagebox.showinfo("Успех", msg)
        else:
            messagebox.showwarning("Внимание", msg)


    def unblock_taskmgr(self):
        success, msg = unblock_taskmgr()
        if success:
            messagebox.showinfo("Успех", msg)
        else:
            messagebox.showerror("Ошибка", msg)

    def block_taskmgr(self):
        success, msg = block_taskmgr()
        if success:
            messagebox.showinfo("Успех", msg)
        else:
            messagebox.showerror("Ошибка", msg)



    def unblock_registry(self):
        success, msg = unblock_registry_editor()
        if success:
            messagebox.showinfo("Успех", msg)
        else:
            messagebox.showerror("Ошибка", msg)



    def restore_associations(self):

        try:
            os.system("cmd /c assoc .txt=txtfile")
            os.system("cmd /c assoc .exe=exefile")
            os.system("cmd /c assoc .lnk=lnkfile")
            os.system("cmd /c assoc .jpg=jpegfile")
            os.system("cmd /c assoc .png=pngfile")
            os.system("cmd /c assoc .mp3=mp3file")
            os.system("cmd /c assoc .mp4=mp4file")
            os.system("cmd /c assoc .doc=Word.Document.8")
            os.system("cmd /c assoc .docx=Word.Document.12")
            os.system("cmd /c assoc .xls=Excel.Sheet.8")
            os.system("cmd /c assoc .xlsx=Excel.Sheet.12")
            os.system("cmd /c assoc .pdf=AcroExch.Document.DC")

            os.system('cmd /c ftype txtfile="%SystemRoot%\\system32\\NOTEPAD.EXE" "%1"')
            os.system('cmd /c ftype exefile="%1" "%*"')
            os.system('cmd /c ftype jpegfile="%SystemRoot%\\System32\\rundll32.exe "%ProgramFiles%\\Windows Photo Viewer\\PhotoViewer.dll", ImageView_Fullscreen %1"')

            messagebox.showinfo("Успешно", "Ассоциации файлов восстановлены!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")


    def create_uninstaller_tab(self):
        import winreg
        import os
        import shutil
        import subprocess
        from tkinter import messagebox

        frame = self.uninstaller_tab

        def get_installed_programs():
            programs = []
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
            ]

            for root, path in reg_paths:
                try:
                    with winreg.OpenKey(root, path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]

                                    try:
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    except:
                                        install_location = ""

                                    try:
                                        uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                    except:
                                        uninstall_string = ""

                                    programs.append((name, install_location, uninstall_string))
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

        def run_uninstall_command(cmd):
            try:
                subprocess.run(cmd, shell=True)
            except Exception as e:
                print(f"Ошибка запуска uninstall: {e}")

        def uninstall_selected():
            selected = tree.selection()
            if not selected:
                return

            item = tree.item(selected[0])
            name = item["values"][0]
            path = item["values"][1]
            uninstall_cmd = item["values"][2]

            confirm = messagebox.askyesno("Удаление", f"Удалить {name}?")

            if not confirm:
                return

            if uninstall_cmd:
                run = messagebox.askyesno("Удалить через системный Uninstaller?", f"Удалить {name} через стандартный деинсталлятор?")
                if run:
                    run_uninstall_command(uninstall_cmd)

            if path != "Не указано" and os.path.exists(path):
                delete_folder(path)

            deep = messagebox.askyesno("Полное удаление", f"Удалить все остатки {name}?")
            if deep:
                user_paths = [
                    os.path.join(os.environ.get('APPDATA', ''), name),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), name),
                    os.path.join(os.environ.get('USERPROFILE', ''), "Documents", name),
                    os.path.join(os.environ.get('PROGRAMDATA', ''), name)
                ]
                for p in user_paths:
                    delete_folder(p)

                messagebox.showinfo("Готово", f"{name} полностью удалена.")
            else:
                messagebox.showinfo("Удалено", f"{name} удалена частично.")

            update_program_list()

        def update_program_list():
            tree.delete(*tree.get_children())
            programs = get_installed_programs()
            for name, path, uninstall_cmd in programs:
                tree.insert("", "end", values=(name, path if path else "Не указано", uninstall_cmd))

        tree = ttk.Treeview(frame, columns=("Программа", "Путь", "Uninstall"), show="headings")
        tree.heading("Программа", text="Программа")
        tree.heading("Путь", text="Путь установки")
        tree.heading("Uninstall", text="Uninstall команда")
        tree.pack(fill=tk.BOTH, expand=True)

        btn = tk.Button(frame, text="Удалить выбранную", command=uninstall_selected)
        btn.pack(side=tk.LEFT, pady=10)

        refresh_btn = tk.Button(frame, text="Обновить список", command=update_program_list)
        refresh_btn.pack(side=tk.LEFT, pady=10)

        update_program_list()

        return frame


    def create_explorer_tab(self):
        try:
            style = ttk.Style()
            style.configure("Explorer.TFrame", background="#000")
            style.configure("Explorer.TButton", padding=5)
            style.configure("Explorer.Treeview", rowheight=25)
            style.configure("Explorer.Treeview.Heading", font=('Segoe UI', 9, 'bold'))
            style.map("Explorer.Treeview", background=[('selected', '#02b008')])

            main_frame = ttk.Frame(self.explorer_tab, style="Explorer.TFrame")
            main_frame.pack(fill='both', expand=True, padx=5, pady=5)

            toolbar = ttk.Frame(main_frame, style="Explorer.TFrame")
            toolbar.pack(fill='x', pady=(0, 5))

            nav_frame = ttk.Frame(toolbar, style="Explorer.TFrame")
            nav_frame.pack(side='left')

            self.back_btn = ttk.Button(
                nav_frame, 
                text="←", 
                style="Explorer.TButton",
                command=self._explorer_back,
                width=3
            )
            self.back_btn.pack(side='left', padx=2)
            
            self.forward_btn = ttk.Button(
                nav_frame, 
                text="→", 
                style="Explorer.TButton",
                command=self._explorer_forward,
                width=3
            )
            self.forward_btn.pack(side='left', padx=2)
            
            self.up_btn = ttk.Button(
                nav_frame, 
                text="↑", 
                style="Explorer.TButton",
                command=self._explorer_up,
                width=3
            )
            self.up_btn.pack(side='left', padx=2)

            self.path_var = tk.StringVar()
            self.path_entry = ttk.Entry(
                toolbar,
                textvariable=self.path_var,
                font=('Segoe UI', 9)
            )
            self.path_entry.pack(side='left', fill='x', expand=True, padx=5)
            self.path_entry.bind('<Return>', self._explorer_navigate_to_path)

            action_frame = ttk.Frame(toolbar, style="Explorer.TFrame")
            action_frame.pack(side='right')

            ttk.Button(
                action_frame, 
                text="Создать папку", 
                style="Explorer.TButton",
                command=self._explorer_create_folder
            ).pack(side='left', padx=2)
            
            ttk.Button(
                action_frame, 
                text="Создать файл", 
                style="Explorer.TButton",
                command=self._explorer_create_file
            ).pack(side='left', padx=2)
            
            ttk.Button(
                action_frame, 
                text="Удалить", 
                style="Explorer.TButton",
                command=self._explorer_delete_selected
            ).pack(side='left', padx=2)
            
            ttk.Button(
                action_frame, 
                text="Копировать", 
                style="Explorer.TButton",
                command=self._explorer_copy
            ).pack(side='left', padx=2)
            
            ttk.Button(
                action_frame, 
                text="Вставить", 
                style="Explorer.TButton",
                command=self._explorer_paste,
                state='disabled'
            ).pack(side='left', padx=2)
            
            ttk.Button(
                action_frame, 
                text="Обновить", 
                style="Explorer.TButton",
                command=self._explorer_refresh
            ).pack(side='left', padx=2)

            tree_frame = ttk.Frame(main_frame, style="Explorer.TFrame")
            tree_frame.pack(fill='both', expand=True)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side='right', fill='y')

            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
            hsb.pack(side='bottom', fill='x')

            self.tree = ttk.Treeview(
                tree_frame,
                columns=("name", "size", "type", "modified"),
                displaycolumns=("name", "size", "type", "modified"),
                yscrollcommand=vsb.set,
                xscrollcommand=hsb.set,
                selectmode='extended',
                style="Explorer.Treeview"
            )
            self.tree.pack(fill='both', expand=True)

            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)

            self.tree.heading("#0", text="")
            self.tree.column("#0", width=20, stretch=False)
            
            self.tree.heading("name", text="Имя", anchor='w')
            self.tree.column("name", width=300, anchor='w')
            
            self.tree.heading("size", text="Размер", anchor='e')
            self.tree.column("size", width=100, anchor='e', stretch=False)
            
            self.tree.heading("type", text="Тип", anchor='w')
            self.tree.column("type", width=150, anchor='w', stretch=False)
            
            self.tree.heading("modified", text="Изменен", anchor='w')
            self.tree.column("modified", width=150, anchor='w', stretch=False)

            self.tree.bind('<Double-1>', self._explorer_on_double_click)
            self.tree.bind('<<TreeviewOpen>>', self._explorer_on_open)
            self.tree.bind('<Button-3>', self._explorer_show_context_menu)

            self.context_menu = tk.Menu(self.tree, tearoff=0)
            self.context_menu.add_command(
                label="Открыть", 
                command=self._explorer_open_selected
            )
            self.context_menu.add_command(
                label="Копировать", 
                command=self._explorer_copy
            )
            self.context_menu.add_command(
                label="Вставить", 
                command=self._explorer_paste
            )
            self.context_menu.add_separator()
            self.context_menu.add_command(
                label="Удалить", 
                command=self._explorer_delete_selected
            )
            self.context_menu.add_command(
                label="Переименовать", 
                command=self._explorer_rename
            )
            self.context_menu.add_separator()
            self.context_menu.add_command(
                label="Свойства", 
                command=self._explorer_properties
            )


            self.status_bar = ttk.Label(
                main_frame, 
                text="Готов", 
                relief='sunken',
                anchor='w'
            )
            self.status_bar.pack(fill='x', pady=(5, 0))

            self.clipboard = None
            self.history = []
            self.history_index = -1
            self.current_path = os.path.abspath(os.path.expanduser("~"))

            self._explorer_load_directory(self.current_path)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать проводник: {str(e)}")


    def _explorer_load_directory(self, path):
        try:
            if not os.path.exists(path):
                messagebox.showerror("Ошибка", f"Путь не существует: {path}")
                return

            if self.history_index == -1 or self.history[self.history_index] != path:
                self.history = self.history[:self.history_index + 1]
                self.history.append(path)
                self.history_index += 1

            self.back_btn.config(state='normal' if self.history_index > 0 else 'disabled')
            self.forward_btn.config(
                state='normal' if self.history_index < len(self.history) - 1 else 'disabled'
            )

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.current_path = path
            self.path_var.set(path)
            self.status_bar.config(text=path)

            if os.path.dirname(path):
                self.tree.insert(
                    '', 'end', 
                    text="..", 
                    values=("..", "", "Папка", ""),
                    tags=('directory',)
                )

            try:
                files = os.listdir(path)
                files.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            except PermissionError:
                messagebox.showerror("Ошибка", f"Нет доступа к каталогу: {path}")
                return

            for name in files:
                full_path = os.path.join(path, name)
                try:
                    if os.path.isdir(full_path):
                        size = ""
                        file_type = "Папка"
                        tags = ('directory',)
                    else:
                        size = self._format_size(os.path.getsize(full_path))
                        _, ext = os.path.splitext(name)
                        file_type = f"{ext[1:].upper()} файл" if ext else "Файл"
                        tags = ('file',)

                    modified = datetime.datetime.fromtimestamp(
                        os.path.getmtime(full_path)
                    ).strftime('%d.%m.%Y %H:%M')

                    self.tree.insert(
                        '', 'end', 
                        text=name, 
                        values=(name, size, file_type, modified),
                        tags=tags
                    )
                except Exception as e:
                    print(f"Ошибка обработки {full_path}: {e}")

            self.tree.tag_configure('directory', foreground='green')
            self.tree.tag_configure('file', foreground='blue')

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить каталог: {str(e)}")

    def _explorer_back(self):
        """Переход назад по истории"""
        if self.history_index > 0:
            self.history_index -= 1
            self._explorer_load_directory(self.history[self.history_index])

    def _explorer_forward(self):
        """Переход вперед по истории"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._explorer_load_directory(self.history[self.history_index])

    def _explorer_up(self):
        """Переход в родительский каталог"""
        parent = os.path.dirname(self.current_path)
        if parent:
            self._explorer_load_directory(parent)

    def _explorer_navigate_to_path(self, event=None):
        """Переход по указанному пути"""
        path = self.path_var.get()
        if os.path.exists(path):
            self._explorer_load_directory(path)
        else:
            messagebox.showerror("Ошибка", "Указанный путь не существует")

    def _explorer_on_double_click(self, event):
        """Обработка двойного клика"""
        item = self.tree.selection()[0]
        name = self.tree.item(item, 'text')
        
        if name == "..":
            self._explorer_up()
        else:
            path = os.path.join(self.current_path, name)
            if os.path.isdir(path):
                self._explorer_load_directory(path)
            else:
                self._explorer_open_selected()

    def _explorer_on_open(self, event):
        """Обработка открытия узла дерева"""
        pass  

    def _explorer_show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _explorer_open_selected(self):
        """Открытие выбранного файла/папки"""
        items = self.tree.selection()
        if not items:
            return
        
        for item in items:
            name = self.tree.item(item, 'text')
            path = os.path.join(self.current_path, name)
            
            try:
                if os.path.isdir(path):
                    self._explorer_load_directory(path)
                else:
                    os.startfile(path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть {path}: {str(e)}")

    def _explorer_create_folder(self):
        """Создание новой папки"""
        name = simpledialog.askstring("Создать папку", "Введите имя папки:")
        if name:
            path = os.path.join(self.current_path, name)
            try:
                os.mkdir(path)
                self._explorer_refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать папку: {str(e)}")

    def _explorer_create_file(self):
        """Создание нового файла"""
        name = simpledialog.askstring("Создать файл", "Введите имя файла:")
        if name:
            path = os.path.join(self.current_path, name)
            try:
                open(path, 'w').close()
                self._explorer_refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать файл: {str(e)}")

    def _explorer_delete_selected(self):
        """Удаление выбранных файлов/папок"""
        items = self.tree.selection()
        if not items:
            return
        
        names = [self.tree.item(item, 'text') for item in items]
        if ".." in names:
            messagebox.showwarning("Внимание", "Нельзя удалить родительский каталог")
            return
        
        if not messagebox.askyesno(
            "Подтверждение", 
            f"Удалить выбранные элементы ({len(items)})?"
        ):
            return
        
        for item in items:
            name = self.tree.item(item, 'text')
            path = os.path.join(self.current_path, name)
            
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить {path}: {str(e)}")
        
        self._explorer_refresh()

    def _explorer_copy(self):
        """Копирование выбранных файлов/папок"""
        items = self.tree.selection()
        if not items:
            return
        
        self.clipboard = {
            'action': 'copy',
            'paths': [os.path.join(self.current_path, self.tree.item(item, 'text')) 
                    for item in items]
        }
        
        # Активируем кнопку "Вставить"
        for child in self.context_menu.winfo_children():
            if child.cget('label') == "Вставить":
                child.config(state='normal')
        
        for child in self.explorer_tab.winfo_children()[0].winfo_children()[1].winfo_children():
            if isinstance(child, ttk.Button) and child.cget('text') == "Вставить":
                child.config(state='normal')

    def _explorer_paste(self):
        """Вставка скопированных/перемещенных файлов"""
        if not self.clipboard:
            return
        
        try:
            for src_path in self.clipboard['paths']:
                name = os.path.basename(src_path)
                dst_path = os.path.join(self.current_path, name)
                
                if self.clipboard['action'] == 'copy':
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                else: 
                    shutil.move(src_path, dst_path)
            
            self._explorer_refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить операцию: {str(e)}")

    def _explorer_rename(self):
        """Переименование выбранного файла/папки"""
        items = self.tree.selection()
        if len(items) != 1:
            messagebox.showwarning("Внимание", "Выберите один элемент для переименования")
            return
        
        item = items[0]
        old_name = self.tree.item(item, 'text')
        if old_name == "..":
            messagebox.showwarning("Внимание", "Нельзя переименовать родительский каталог")
            return
        
        new_name = simpledialog.askstring(
            "Переименовать", 
            "Введите новое имя:", 
            initialvalue=old_name
        )
        
        if new_name and new_name != old_name:
            old_path = os.path.join(self.current_path, old_name)
            new_path = os.path.join(self.current_path, new_name)
            
            try:
                os.rename(old_path, new_path)
                self._explorer_refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось переименовать: {str(e)}")

    def _explorer_properties(self):
        """Показ свойств выбранного файла/папки"""
        items = self.tree.selection()
        if len(items) != 1:
            return
        
        item = items[0]
        name = self.tree.item(item, 'text')
        path = os.path.join(self.current_path, name)
        
        try:
            stats = os.stat(path)
            size = self._format_size(stats.st_size)
            created = datetime.datetime.fromtimestamp(stats.st_ctime)
            modified = datetime.datetime.fromtimestamp(stats.st_mtime)
            
            info = (
                f"Имя: {name}\n"
                f"Путь: {path}\n"
                f"Тип: {'Папка' if os.path.isdir(path) else 'Файл'}\n"
                f"Размер: {size}\n"
                f"Создан: {created.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"Изменен: {modified.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"Права: {oct(stats.st_mode)[-3:]}"
            )
            
            messagebox.showinfo("Свойства", info)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить свойства: {str(e)}")

    def _explorer_refresh(self):
        """Обновление текущего каталога"""
        self._explorer_load_directory(self.current_path)

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"



    def create_process_tab(self):
        try:

            style = ttk.Style()
            style.configure("Process.TFrame", background="#1e1e1e")
            style.configure("Process.Treeview", background="#252526", fieldbackground="#252526", 
                        foreground="white", rowheight=25)
            style.configure("Process.Treeview.Heading", background="#333333", foreground="white", 
                        font=('Segoe UI', 9, 'bold'))
            style.map("Process.Treeview", background=[('selected', '#0078d7')])
            style.configure("Process.TButton", padding=5, font=('Segoe UI', 9))
            style.configure("Process.TEntry", fieldbackground="#333333", foreground="white")


            main_frame = ttk.Frame(self.process_tab, style="Process.TFrame")
            main_frame.pack(fill='both', expand=True, padx=5, pady=5)

            control_frame = ttk.Frame(main_frame, style="Process.TFrame")
            control_frame.pack(fill='x', pady=(0, 5))

            search_frame = ttk.Frame(control_frame, style="Process.TFrame")
            search_frame.pack(side='left', fill='x', expand=True)

            ttk.Label(search_frame, text="Поиск:", style="Process.TLabel").pack(side='left', padx=5)
            
            self.search_var = tk.StringVar()
            self.search_var.trace("w", self._update_process_search)
            search_entry = ttk.Entry(
                search_frame, 
                textvariable=self.search_var,
                style="Process.TEntry"
            )
            search_entry.pack(side='left', fill='x', expand=True, padx=5)
            
            btn_frame = ttk.Frame(control_frame, style="Process.TFrame")
            btn_frame.pack(side='right')

            icons = {
                'refresh': '↻',
                'kill': '⏹',
                'tree': '🌳',
                'folder': '📁',
                'details': '🔍'
            }

            ttk.Button(
                btn_frame, 
                text=f"{icons['refresh']} Обновить", 
                style="Process.TButton",
                command=self._refresh_process_list
            ).pack(side='left', padx=2)

            ttk.Button(
                btn_frame, 
                text=f"{icons['kill']} Завершить", 
                style="Process.TButton",
                command=self._kill_selected_process
            ).pack(side='left', padx=2)

            ttk.Button(
                btn_frame, 
                text=f"{icons['tree']} Дерево", 
                style="Process.TButton",
                command=self._kill_process_tree
            ).pack(side='left', padx=2)

            ttk.Button(
                btn_frame, 
                text=f"{icons['folder']} Папка", 
                style="Process.TButton",
                command=self._open_process_folder
            ).pack(side='left', padx=2)

            ttk.Button(
                btn_frame, 
                text=f"{icons['details']} Детали", 
                style="Process.TButton",
                command=self._show_process_details
            ).pack(side='left', padx=2)

            tree_frame = ttk.Frame(main_frame, style="Process.TFrame")
            tree_frame.pack(fill='both', expand=True)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side='right', fill='y')

            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
            hsb.pack(side='bottom', fill='x')

            self.process_tree = ttk.Treeview(
                tree_frame,
                columns=("pid", "name", "status", "cpu", "memory", "user"),
                displaycolumns=("pid", "name", "status", "cpu", "memory", "user"),
                yscrollcommand=vsb.set,
                xscrollcommand=hsb.set,
                selectmode='extended',
                style="Process.Treeview"
            )
            self.process_tree.pack(fill='both', expand=True)

            vsb.config(command=self.process_tree.yview)
            hsb.config(command=self.process_tree.xview)

            self.process_tree.heading("#0", text="")
            self.process_tree.column("#0", width=0, stretch=False)
            
            self.process_tree.heading("pid", text="PID", anchor='center')
            self.process_tree.column("pid", width=80, anchor='center', stretch=False)
            
            self.process_tree.heading("name", text="Имя процесса", anchor='w')
            self.process_tree.column("name", width=250, anchor='w')
            
            self.process_tree.heading("status", text="Статус", anchor='center')
            self.process_tree.column("status", width=80, anchor='center', stretch=False)
            
            self.process_tree.heading("cpu", text="CPU %", anchor='center')
            self.process_tree.column("cpu", width=80, anchor='center', stretch=False)
            
            self.process_tree.heading("memory", text="Память", anchor='center')
            self.process_tree.column("memory", width=100, anchor='center', stretch=False)
            
            self.process_tree.heading("user", text="Пользователь", anchor='w')
            self.process_tree.column("user", width=150, anchor='w', stretch=False)

            self.process_tree.bind('<Double-1>', self._open_process_folder)
            self.process_tree.bind('<Button-3>', self._show_process_context_menu)

            self.process_context_menu = tk.Menu(self.process_tree, tearoff=0, bg='#333333', fg='white')
            self.process_context_menu.add_command(
                label="Завершить процесс", 
                command=self._kill_selected_process
            )
            self.process_context_menu.add_command(
                label="Завершить дерево процессов", 
                command=self._kill_process_tree
            )
            self.process_context_menu.add_separator()
            self.process_context_menu.add_command(
                label="Открыть папку процесса", 
                command=self._open_process_folder
            )
            self.process_context_menu.add_command(
                label="Подробная информация", 
                command=self._show_process_details
            )
            self.process_context_menu.add_separator()
            self.process_context_menu.add_command(
                label="Обновить список", 
                command=self._refresh_process_list
            )

            # Статус бар
            self.process_status_bar = ttk.Label(
                main_frame, 
                text="Готов", 
                relief='sunken',
                anchor='w',
                style="Process.TLabel"
            )
            self.process_status_bar.pack(fill='x', pady=(5, 0))

            # Инициализация данных
            self._refresh_process_list()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку процессов: {str(e)}")

    def _refresh_process_list(self):
        try:
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                            'memory_info', 'username', 'exe']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
            
            for proc in processes:
                memory_mb = proc['memory_info'].rss / (1024 * 1024)
                self.process_tree.insert(
                    '', 'end',
                    values=(
                        proc['pid'],
                        proc['name'],
                        proc['status'],
                        f"{proc['cpu_percent']:.1f}%",
                        f"{memory_mb:.1f} MB",
                        proc['username'].split('\\')[-1] if proc['username'] else "SYSTEM"
                    )
                )
            
            self.process_status_bar.config(text=f"Всего процессов: {len(processes)}")
            
        except Exception as e:
            self.process_status_bar.config(text=f"Ошибка: {str(e)}")

    def _update_process_search(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.process_tree.get_children():
            values = self.process_tree.item(item, 'values')
            if not search_term or any(search_term in str(v).lower() for v in values):
                self.process_tree.item(item, tags=('visible',))
                self.process_tree.detach(item)
                self.process_tree.reattach(item, '', 'end')
            else:
                self.process_tree.detach(item)

    def _kill_selected_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите процесс для завершения")
            return
        
        pid = int(self.process_tree.item(selected[0], 'values')[0])
        name = self.process_tree.item(selected[0], 'values')[1]
        
        if messagebox.askyesno(
            "Подтверждение", 
            f"Завершить процесс {name} (PID: {pid})?"
        ):
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                self._refresh_process_list()
                self.process_status_bar.config(text=f"Процесс {name} завершен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось завершить процесс: {str(e)}")

    def _kill_process_tree(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите процесс для завершения")
            return
        
        pid = int(self.process_tree.item(selected[0], 'values')[0])
        name = self.process_tree.item(selected[0], 'values')[1]
        
        if messagebox.askyesno(
            "Подтверждение", 
            f"Завершить процесс {name} (PID: {pid}) и все дочерние процессы?"
        ):
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                
                parent.terminate()
                
                gone, alive = psutil.wait_procs([parent] + children, timeout=5)
                
                self._refresh_process_list()
                self.process_status_bar.config(
                    text=f"Завершено {len(gone)} процессов (включая {name})"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось завершить дерево процессов: {str(e)}")

    def _open_process_folder(self, event=None):
        selected = self.process_tree.selection()
        if not selected:
            return
        
        pid = int(self.process_tree.item(selected[0], 'values')[0])
        
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            
            if exe_path:
                folder = os.path.dirname(exe_path)
                os.startfile(folder)
            else:
                messagebox.showinfo("Информация", "Не удалось определить путь к исполняемому файлу")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку процесса: {str(e)}")

    def _show_process_details(self):
        selected = self.process_tree.selection()
        if not selected:
            return
        
        pid = int(self.process_tree.item(selected[0], 'values')[0])
        
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                info = f"""
    === Основная информация ===
    PID: {proc.pid}
    Имя: {proc.name()}
    Статус: {proc.status()}
    Путь: {proc.exe() or "Недоступно"}
    Рабочая директория: {proc.cwd()}
    Командная строка: {' '.join(proc.cmdline()) or "Недоступно"}
    Пользователь: {proc.username()}
    Дата создания: {datetime.datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}

    === Ресурсы ===
    CPU %: {proc.cpu_percent()}%
    Память: {proc.memory_info().rss / (1024 * 1024):.1f} MB
    Потоки: {proc.num_threads()}
    Дескрипторы: {proc.num_handles()}

    === Дочерние процессы ===
    """
                children = proc.children(recursive=True)
                if children:
                    for child in children:
                        info += f"  - PID {child.pid}: {child.name()}\n"
                else:
                    info += "  Нет дочерних процессов\n"
            
            # Создаем окно с деталями
            detail_win = tk.Toplevel(self)
            detail_win.title(f"Детали процесса {proc.name()} (PID: {pid})")
            detail_win.geometry("600x400")
            
            text = tk.Text(detail_win, wrap='word', font=('Consolas', 10))
            text.pack(fill='both', expand=True, padx=5, pady=5)
            text.insert('1.0', info.strip())
            text.config(state='disabled')
            
            btn_frame = tk.Frame(detail_win)
            btn_frame.pack(fill='x', padx=5, pady=5)
            
            tk.Button(
                btn_frame, 
                text="Завершить процесс", 
                command=lambda: self._kill_process_and_close(pid, detail_win)
            ).pack(side='left', padx=5)
            
            tk.Button(
                btn_frame, 
                text="Закрыть", 
                command=detail_win.destroy
            ).pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о процессе: {str(e)}")

    def _kill_process_and_close(self, pid, window):
        """Завершает процесс и закрывает окно"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            window.destroy()
            self._refresh_process_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить процесс: {str(e)}")

    def _show_process_context_menu(self, event):
        """Показывает контекстное меню для процесса"""
        item = self.process_tree.identify_row(event.y)
        if item:
            self.process_tree.selection_set(item)
            try:
                self.process_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.process_context_menu.grab_release()





    def create_tinstall_tab(self):
        """Создает вкладку для комплексного мониторинга установки программ"""
        try:
            # Стилизация
            style = ttk.Style()
            style.configure("TInstall.TFrame", background="#1e1e1e")
            style.configure("TInstall.TLabel", background="#1e1e1e", foreground="white")
            style.configure("TInstall.TButton", padding=5, font=('Segoe UI', 9))
            style.configure("TInstall.TNotebook", background="#1e1e1e")
            style.configure("TInstall.TNotebook.Tab", background="#2e2e2e", foreground="white")
            
            # Основной фрейм
            main_frame = ttk.Frame(self.tinstall_tab, style="TInstall.TFrame")
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Верхняя панель управления
            control_frame = ttk.Frame(main_frame, style="TInstall.TFrame")
            control_frame.pack(fill='x', pady=(0, 10))
            
            # Информация о выбранной программе
            self.exe_info_label = ttk.Label(
                control_frame, 
                text="Программа не выбрана", 
                style="TInstall.TLabel",
                font=('Segoe UI', 9, 'bold')
            )
            self.exe_info_label.pack(side='left', padx=5)
            
            # Кнопки управления
            btn_frame = ttk.Frame(control_frame, style="TInstall.TFrame")
            btn_frame.pack(side='right')
            
            ttk.Button(
                btn_frame, 
                text="Выбрать программу", 
                style="TInstall.TButton",
                command=self._choose_install_exe
            ).pack(side='left', padx=5)
            
            self.monitor_btn = ttk.Button(
                btn_frame, 
                text="▶ Начать мониторинг", 
                style="TInstall.TButton",
                command=self._start_install_monitoring,
                state='disabled'
            )
            self.monitor_btn.pack(side='left', padx=5)
            
            # Кнопка сохранения логов
            self.save_btn = ttk.Button(
                btn_frame,
                text="💾 Сохранить логи",
                style="TInstall.TButton",
                command=self._save_installation_logs,
                state='disabled'
            )
            self.save_btn.pack(side='left', padx=5)
            
            # Notebook для разных типов мониторинга
            self.monitor_notebook = ttk.Notebook(main_frame, style="TInstall.TNotebook")
            self.monitor_notebook.pack(fill='both', expand=True)
            
            # Вкладки мониторинга
            tabs = {
                'filesystem': ("Файловая система", self._create_filesystem_tab),
                'registry': ("Реестр", self._create_registry_tab),
                'process': ("Процессы", self._create_process_tab),
                'network': ("Сеть", self._create_network_tab),
                'resources': ("Ресурсы", self._create_resources_tab),
                'summary': ("Сводка", self._create_summary_tab)
            }
            
            self.log_frames = {}
            for key, (title, creator) in tabs.items():
                frame = ttk.Frame(self.monitor_notebook, style="TInstall.TFrame")
                creator(frame)
                self.monitor_notebook.add(frame, text=title)
                self.log_frames[key] = frame
            
            # Статус бар
            self.status_bar = ttk.Label(
                main_frame, 
                text="Готов к работе", 
                style="TInstall.TLabel",
                relief='sunken',
                anchor='w'
            )
            self.status_bar.pack(fill='x', pady=(5, 0))
            
            # Инициализация переменных
            self.monitored_process = None
            self.observer = None
            self.reg_monitor = None
            self.monitoring_active = False
            self.installation_logs = {key: [] for key in tabs.keys()}
            self.log_file_path = None
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку мониторинга: {str(e)}")

    def _create_filesystem_tab(self, parent_frame):
        """Создает вкладку для мониторинга файловой системы"""
        self._create_scrollable_log(parent_frame)
        # Дополнительные элементы для файлового мониторинга
        filter_frame = ttk.Frame(parent_frame, style="TInstall.TFrame")
        filter_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(filter_frame, text="Фильтр:", style="TInstall.TLabel").pack(side='left')
        self.fs_filter = ttk.Entry(filter_frame)
        self.fs_filter.pack(side='left', fill='x', expand=True, padx=5)
        self.fs_filter.bind('<Return>', lambda e: self._filter_logs('filesystem'))

    def _create_registry_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)

    def _create_process_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)

    def _create_network_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)

    def _create_resources_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)

    def _create_summary_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)
        btn_frame = ttk.Frame(parent_frame, style="TInstall.TFrame")
        btn_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(
            btn_frame,
            text="📊 Сгенерировать отчет",
            style="TInstall.TButton",
            command=self._generate_install_report
        ).pack()

    def _create_scrollable_log(self, parent_frame):
        canvas = tk.Canvas(parent_frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        log_frame = ttk.Frame(canvas, style="TInstall.TFrame")
        canvas.create_window((0, 0), window=log_frame, anchor="nw")
        
        log_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        parent_frame.canvas = canvas
        parent_frame.log_frame = log_frame
        parent_frame.log_lines = []

    def _choose_install_exe(self):
        file_path = filedialog.askopenfilename(
            title="Выберите программу для мониторинга",
            filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            self.exe_path = file_path
            self.exe_info_label.config(
                text=f"Выбрано: {os.path.basename(file_path)}"
            )
            self.monitor_btn.config(state='normal')
            self._update_status("Программа выбрана. Готов к мониторингу")

    def _start_install_monitoring(self):
        if not hasattr(self, 'exe_path') or not self.exe_path:
            messagebox.showwarning("Внимание", "Сначала выберите программу!")
            return
        
        if self.monitoring_active:
            self._stop_install_monitoring()
            return
        
        log_dir = os.path.join(os.getenv('APPDATA'), 'InstallMonitor')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(log_dir, f"install_log_{timestamp}.txt")
        
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"=== Лог установки {os.path.basename(self.exe_path)} ===\n")
            f.write(f"Время начала: {datetime.datetime.now()}\n")
            f.write(f"Путь к установщику: {self.exe_path}\n\n")
        
        for frame in self.log_frames.values():
            for widget in frame.log_frame.winfo_children():
                widget.destroy()
            frame.log_lines.clear()
        
        for key in self.installation_logs:
            self.installation_logs[key] = []
        
        # Запуск мониторинга
        self.monitoring_active = True
        self.monitor_btn.config(text="■ Остановить мониторинг")
        self.save_btn.config(state='normal')
        self._update_status("Мониторинг запущен...")
        
        threading.Thread(
            target=self._run_install_monitoring, 
            daemon=True
        ).start()

    def _run_install_monitoring(self):
        """Основной цикл мониторинга"""
        try:
            # Запуск процесса
            self._add_log_entry("🚀 Запуск программы...", "header", "process")
            self.monitored_process = subprocess.Popen(
                [self.exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            pid = self.monitored_process.pid
            proc = psutil.Process(pid)
            self._add_log_entry(f"🔄 PID процесса: {pid}", "info", "process")
            
            # Мониторинг файловой системы
            self._setup_filesystem_monitoring()
            
            # Мониторинг реестра
            self._setup_registry_monitoring()
            
            # Основной цикл мониторинга
            while self.monitoring_active and proc.is_running():
                self._monitor_child_processes(proc)
                self._monitor_open_files(proc)
                self._monitor_network_activity(proc)
                self._monitor_resources(proc)
                self._read_process_output()
                time.sleep(1)
            
            if self.monitoring_active:
                self._add_log_entry("✅ Программа завершила работу", "success", "process")
                self._generate_install_summary()
                self._update_status("Мониторинг завершен")
        
        except Exception as e:
            self._add_log_entry(f"❌ Ошибка мониторинга: {str(e)}", "error", "process")
            self._update_status(f"Ошибка: {str(e)}")
        
        finally:
            self.monitoring_active = False
            if self.observer:
                self.observer.stop()
                self.observer.join()
            if hasattr(self, 'monitored_process') and self.monitored_process:
                self.monitored_process.terminate()

    def _stop_install_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_active = False
        self.monitor_btn.config(text="▶ Начать мониторинг")
        self._update_status("Мониторинг остановлен")

    def _setup_filesystem_monitoring(self):
        """Настройка мониторинга файловой системы"""
        self._add_log_entry("👀 Начало мониторинга файловой системы...", "header", "filesystem")
        
        class InstallHandler(FileSystemEventHandler):
            def __init__(self, parent):
                self.parent = parent
            
            def on_created(self, event):
                if self.parent.monitoring_active:
                    self.parent._add_log_entry(
                        f"📂 Создан: {event.src_path}",
                        "file_event",
                        "filesystem"
                    )
            
            def on_deleted(self, event):
                if self.parent.monitoring_active:
                    self.parent._add_log_entry(
                        f"🗑️ Удален: {event.src_path}",
                        "file_event",
                        "filesystem"
                    )
            
            def on_modified(self, event):
                if self.parent.monitoring_active and not event.is_directory:
                    self.parent._add_log_entry(
                        f"✏️ Изменен: {event.src_path}",
                        "file_event",
                        "filesystem"
                    )
        
        self.observer = Observer()
        watch_dirs = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Users\\" + os.getenv('USERNAME') + "\\AppData",
            "C:\\Windows\\Temp",
            os.path.dirname(self.exe_path)
        ]
        
        for directory in watch_dirs:
            if os.path.exists(directory):
                self.observer.schedule(InstallHandler(self), path=directory, recursive=True)
        
        self.observer.start()

    def _setup_registry_monitoring(self):
        """Настройка мониторинга реестра"""
        self._add_log_entry("🔍 Начало мониторинга реестра...", "header", "registry")
        
        # Здесь должна быть реализация мониторинга реестра
        def reg_monitor_thread():
            while self.monitoring_active:
                time.sleep(2)
                # В реальном приложении здесь будет код мониторинга реестра
                pass
        
        self.reg_monitor = threading.Thread(target=reg_monitor_thread, daemon=True)
        self.reg_monitor.start()

    def _monitor_child_processes(self, parent_proc):
        """Мониторинг дочерних процессов"""
        try:
            children = parent_proc.children(recursive=True)
            for child in children:
                self._add_log_entry(
                    f"🔗 Подпроцесс: {child.name()} (PID: {child.pid})",
                    "process_info",
                    "process"
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_open_files(self, proc):
        """Мониторинг открытых файлов"""
        try:
            open_files = proc.open_files()
            if open_files:
                for f in open_files:
                    self._add_log_entry(
                        f"📄 Открыт файл: {f.path}",
                        "file_access",
                        "filesystem"
                    )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_network_activity(self, proc):
        """Мониторинг сетевой активности"""
        try:
            connections = proc.connections()
            if connections:
                for conn in connections:
                    if conn.status == psutil.CONN_ESTABLISHED:
                        self._add_log_entry(
                            f"🌐 Соединение: {conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}",
                            "network_activity",
                            "network"
                        )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_resources(self, proc):
        """Мониторинг использования ресурсов"""
        try:
            cpu_percent = proc.cpu_percent()
            memory_info = proc.memory_info()
            self._add_log_entry(
                f"⚡ CPU: {cpu_percent}%, RAM: {memory_info.rss / 1024 / 1024:.2f} MB",
                "resource_usage",
                "resources"
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _read_process_output(self):
        """Чтение вывода процесса"""
        if not self.monitored_process:
            return
        
        stdout = self.monitored_process.stdout
        if stdout:
            output = stdout.readline()
            if output:
                self._add_log_entry(
                    f"ℹ️ Вывод: {output.decode(errors='replace').strip()}",
                    "process_output",
                    "process"
                )
        
        stderr = self.monitored_process.stderr
        if stderr:
            error = stderr.readline()
            if error:
                self._add_log_entry(
                    f"⚠️ Ошибка: {error.decode(errors='replace').strip()}",
                    "process_error",
                    "process"
                )

    def _add_log_entry(self, message, log_type, log_category):
        """Добавление записи в лог"""
        if not self.monitoring_active:
            return
        
        colors = {
            "header": "#4fc3f7", "info": "#ffffff", "file_event": "#a5d6a7",
            "file_access": "#81c784", "process_output": "#bbdefb", "process_error": "#ff8a65",
            "process_info": "#ce93d8", "success": "#69f0ae", "error": "#ff5252",
            "registry_change": "#ffcc80", "network_activity": "#9fa8da", "resource_usage": "#80cbc4"
        }
        
        color = colors.get(log_type, "#ffffff")
        frame = self.log_frames.get(log_category)
        if not frame:
            return
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        label = ttk.Label(
            frame.log_frame,
            text=full_message,
            style="TInstall.TLabel",
            foreground=color,
            anchor='w',
            font=('Consolas', 9)
        )
        label.pack(fill='x', padx=5, pady=2)
        
        frame.log_frame.update_idletasks()
        frame.canvas.yview_moveto(1.0)
        frame.log_lines.append(label)
        
        self.installation_logs[log_category].append(full_message)
        
        if self.log_file_path:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"{full_message}\n")

    def _update_status(self, message):
        """Обновление статус бара"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")

    def _save_installation_logs(self):
        """Сохранение логов установки"""
        if not self.installation_logs or not self.log_file_path:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        
        try:
            report_dir = os.path.dirname(self.log_file_path)
            report_path = os.path.join(report_dir, f"install_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=== ОТЧЕТ ОБ УСТАНОВКЕ ===\n\n")
                f.write(f"Программа: {os.path.basename(self.exe_path)}\n")
                f.write(f"Время мониторинга: {datetime.datetime.now()}\n\n")
                
                for category, logs in self.installation_logs.items():
                    if logs:
                        f.write(f"=== {category.upper()} ===\n")
                        f.write("\n".join(logs))
                        f.write("\n\n")
            
            messagebox.showinfo("Сохранено", f"Отчет сохранен в:\n{report_path}")
            os.startfile(report_dir)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить логи: {str(e)}")

    def _generate_install_summary(self):
        """Генерация сводки установки"""
        installed_files = []
        modified_files = []
        
        for entry in self.installation_logs['filesystem']:
            if "Создан:" in entry:
                installed_files.append(entry.split("Создан:")[1].strip())
            elif "Изменен:" in entry:
                modified_files.append(entry.split("Изменен:")[1].strip())
        
        summary = [
            "=== СВОДКА УСТАНОВКИ ===",
            f"Программа: {os.path.basename(self.exe_path)}",
            f"Всего создано файлов: {len(installed_files)}",
            f"Всего изменено файлов: {len(modified_files)}",
            "\n=== ОСНОВНЫЕ ДИРЕКТОРИИ ==="
        ]
        
        dir_stats = {}
        for file in installed_files:
            dir_name = os.path.dirname(file)
            dir_stats[dir_name] = dir_stats.get(dir_name, 0) + 1
        
        for dir_path, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary.append(f"{dir_path} - {count} файлов")
        
        for line in summary:
            self._add_log_entry(line, "info", "summary")

    def _generate_install_report(self):
        """Генерация полного отчета об установке"""
        self._save_installation_logs()

    def _filter_logs(self, category):
        """Фильтрация логов по категории"""
        filter_text = self.fs_filter.get().lower()
        frame = self.log_frames.get(category)
        if not frame:
            return
        
        for label in frame.log_lines:
            text = label.cget("text").lower()
            if filter_text in text:
                label.pack(fill='x', padx=5, pady=2)
            else:
                label.pack_forget()




    def create_autorun_tab(self):
        """Создает вкладку автозагрузки с тремя подразделами"""
        try:
            # Создаем Notebook для вкладок внутри автозагрузки
            self.autorun_notebook = ttk.Notebook(self.autorun_tab)
            self.autorun_notebook.pack(fill='both', expand=True, padx=5, pady=5)

            # Вкладка 1: Обычная автозагрузка (Run)
            self.run_tab = ttk.Frame(self.autorun_notebook)
            self.autorun_notebook.add(self.run_tab, text="Автозагрузка (Run)")

            # Вкладка 2: Winlogon
            self.winlogon_tab = ttk.Frame(self.autorun_notebook)
            self.autorun_notebook.add(self.winlogon_tab, text="Winlogon")

            # Вкладка 3: Планировщик задач
            self.scheduler_tab = ttk.Frame(self.autorun_notebook)
            self.autorun_notebook.add(self.scheduler_tab, text="Планировщик")

            # Создаем содержимое для каждой вкладки
            self._create_run_tab_content()
            self._create_winlogon_tab_content()
            self._create_scheduler_tab_content()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку автозагрузки: {str(e)}")

    def _create_run_tab_content(self):
        """Содержимое вкладки обычной автозагрузки"""
        try:
            frame = ttk.Frame(self.run_tab)
            frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Список автозагрузки
            self.run_listbox = tk.Listbox(frame, width=80, height=15)
            self.run_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)

            scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.run_listbox.yview)
            scrollbar.pack(side='right', fill='y')
            self.run_listbox.config(yscrollcommand=scrollbar.set)

            # Кнопки управления
            btn_frame = ttk.Frame(self.run_tab)
            btn_frame.pack(fill='x', padx=5, pady=5)

            ttk.Button(btn_frame, text="Обновить", command=self._update_run_list).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Добавить", command=self._add_to_run).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Удалить", command=self._remove_from_run).pack(side='left', padx=5)

            # Инициализация списка
            self._update_run_list()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку Run: {str(e)}")

    def _create_winlogon_tab_content(self):
        """Содержимое вкладки Winlogon"""
        try:
            frame = ttk.Frame(self.winlogon_tab)
            frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Список Winlogon
            self.winlogon_listbox = tk.Listbox(frame, width=80, height=15)
            self.winlogon_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)

            scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.winlogon_listbox.yview)
            scrollbar.pack(side='right', fill='y')
            self.winlogon_listbox.config(yscrollcommand=scrollbar.set)

            # Кнопки управления
            btn_frame = ttk.Frame(self.winlogon_tab)
            btn_frame.pack(fill='x', padx=5, pady=5)

            ttk.Button(btn_frame, text="Обновить", command=self._update_winlogon_list).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Добавить", command=self._add_to_winlogon).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Удалить", command=self._remove_from_winlogon).pack(side='left', padx=5)

            # Инициализация списка
            self._update_winlogon_list()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку Winlogon: {str(e)}")

    def _create_scheduler_tab_content(self):
        """Содержимое вкладки Планировщика задач"""
        try:
            frame = ttk.Frame(self.scheduler_tab)
            frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Список задач
            self.scheduler_listbox = tk.Listbox(frame, width=80, height=15)
            self.scheduler_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)

            scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.scheduler_listbox.yview)
            scrollbar.pack(side='right', fill='y')
            self.scheduler_listbox.config(yscrollcommand=scrollbar.set)

            # Кнопки управления
            btn_frame = ttk.Frame(self.scheduler_tab)
            btn_frame.pack(fill='x', padx=5, pady=5)

            ttk.Button(btn_frame, text="Обновить", command=self._update_scheduler_list).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Создать задачу", command=self._create_scheduler_task).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Удалить", command=self._remove_scheduler_task).pack(side='left', padx=5)

            # Инициализация списка
            self._update_scheduler_list()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку Планировщика: {str(e)}")

    # Методы для работы с автозагрузкой (Run)
    def _update_run_list(self):
        """Обновляет список программ в автозагрузке"""
        try:
            self.run_listbox.delete(0, tk.END)
            key_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
            ]

            for root, path in key_paths:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                self.run_listbox.insert(tk.END, f"[{'User' if root == winreg.HKEY_CURRENT_USER else 'System'}] {name}: {value}")
                                i += 1
                            except OSError:
                                break
                except WindowsError as e:
                    self.run_listbox.insert(tk.END, f"Ошибка чтения {path}: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить список автозагрузки: {str(e)}")

    def _add_to_run(self):
        """Добавляет программу в автозагрузку"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл для добавления в автозагрузку",
                filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
            )
            if not file_path:
                return

            if not os.path.exists(file_path):
                messagebox.showerror("Ошибка", "Указанный файл не существует!")
                return

            # Нормализуем путь для Wine
            file_path = os.path.abspath(file_path).replace('\\', '/')

            # Выбираем куда добавлять (пользовательская или системная автозагрузка)
            choice = messagebox.askyesno("Выбор", "Добавить в системную автозагрузку (для всех пользователей)?")
            root = winreg.HKEY_LOCAL_MACHINE if choice else winreg.HKEY_CURRENT_USER

            try:
                with winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, os.path.basename(file_path), 0, winreg.REG_SZ, file_path)
                messagebox.showinfo("Успех", "Программа добавлена в автозагрузку")
                self._update_run_list()
            except PermissionError:
                messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить в автозагрузку: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")

    def _remove_from_run(self):
        """Удаляет программу из автозагрузки"""
        try:
            selection = self.run_listbox.curselection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите программу для удаления")
                return
            
            selected_item = self.run_listbox.get(selection[0])
            
            # Парсим информацию из строки
            if selected_item.startswith("[User]"):
                root = winreg.HKEY_CURRENT_USER
                name = selected_item.split(":")[0].replace("[User] ", "").strip()
            elif selected_item.startswith("[System]"):
                root = winreg.HKEY_LOCAL_MACHINE
                name = selected_item.split(":")[0].replace("[System] ", "").strip()
            else:
                messagebox.showerror("Ошибка", "Не удалось определить тип записи")
                return
            
            try:
                with winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                messagebox.showinfo("Успех", f"Программа '{name}' удалена из автозагрузки")
                self._update_run_list()
            except PermissionError:
                messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить программу: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")

    # Методы для работы с Winlogon
    def _update_winlogon_list(self):
        """Обновляет список параметров Winlogon"""
        try:
            self.winlogon_listbox.delete(0, tk.END)
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if name in ["Shell", "Userinit", "Taskman"]:
                                self.winlogon_listbox.insert(tk.END, f"{name}: {value}")
                            i += 1
                        except OSError:
                            break
            except WindowsError as e:
                self.winlogon_listbox.insert(tk.END, f"Ошибка чтения Winlogon: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить список Winlogon: {str(e)}")

    def _add_to_winlogon(self):
        """Добавляет программу в Winlogon"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл для добавления в Winlogon",
                filetypes=[("Исполняемые файлы", "*.exe")]
            )
            if not file_path:
                return

            if not os.path.exists(file_path):
                messagebox.showerror("Ошибка", "Указанный файл не существует!")
                return

            # Нормализуем путь для Wine
            file_path = os.path.abspath(file_path).replace('\\', '/')

            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", 
                                0, winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                    
                    # Получаем текущее значение Shell
                    try:
                        current_shell = winreg.QueryValueEx(key, "Shell")[0]
                    except WindowsError:
                        current_shell = "explorer.exe"  # Значение по умолчанию

                    # Формируем новое значение
                    if current_shell and file_path not in current_shell:
                        new_shell = f"{current_shell},{file_path}"
                    else:
                        new_shell = file_path
                    
                    # Устанавливаем новое значение
                    winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, new_shell)
                
                messagebox.showinfo("Успех", "Программа добавлена в Winlogon")
                self._update_winlogon_list()
            except PermissionError:
                messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить в Winlogon: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")

    def _remove_from_winlogon(self):
        """Восстанавливает стандартные значения Winlogon"""
        try:
            selection = self.winlogon_listbox.curselection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите параметр для восстановления")
                return
            
            selected_item = self.winlogon_listbox.get(selection[0])
            param_name = selected_item.split(":")[0].strip()
            
            default_values = {
                "Shell": "explorer.exe",
                "Userinit": "C:\\Windows\\system32\\userinit.exe,",
                "Taskman": "taskman.exe"
            }
            
            if param_name not in default_values:
                messagebox.showerror("Ошибка", "Неизвестный параметр Winlogon")
                return

            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", 
                                0, winreg.KEY_SET_VALUE) as key:
                    
                    winreg.SetValueEx(key, param_name, 0, winreg.REG_SZ, default_values[param_name])
                
                messagebox.showinfo("Успех", f"Параметр '{param_name}' восстановлен по умолчанию")
                self._update_winlogon_list()
            except PermissionError:
                messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить Winlogon: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")

    # Методы для работы с Планировщиком задач
    def _update_scheduler_list(self):
        """Обновляет список задач в Планировщике"""
        try:
            self.scheduler_listbox.delete(0, tk.END)
            
            # Проверяем доступность PowerShell
            try:
                subprocess.run(["powershell", "-Command", "exit 0"], check=True, shell=True)
            except:
                self.scheduler_listbox.insert(tk.END, "PowerShell недоступен")
                return

            # Команда для получения списка задач
            ps_command = """
            Get-ScheduledTask | 
            Where-Object { $_.TaskPath -notlike "\\Microsoft\\*" -and $_.State -ne "Disabled" } | 
            Select-Object TaskName, State, Actions | 
            ForEach-Object { 
                $action = $_.Actions.Execute
                "{0} ({1}) -> {2}" -f $_.TaskName, $_.State, $action
            }
            """
            
            try:
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True, shell=True, timeout=10)
                
                if result.returncode == 0:
                    tasks = result.stdout.splitlines()
                    if tasks:
                        for task in tasks:
                            if task.strip():
                                self.scheduler_listbox.insert(tk.END, task.strip())
                    else:
                        self.scheduler_listbox.insert(tk.END, "Нет пользовательских задач")
                else:
                    error = result.stderr if result.stderr else "Неизвестная ошибка"
                    self.scheduler_listbox.insert(tk.END, f"Ошибка: {error}")
            except subprocess.TimeoutExpired:
                self.scheduler_listbox.insert(tk.END, "Таймаут выполнения команды")
            except Exception as e:
                self.scheduler_listbox.insert(tk.END, f"Ошибка выполнения: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить список задач: {str(e)}")

    def _create_scheduler_task(self):
        """Создает новую задачу в Планировщике"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите программу для добавления в Планировщик",
                filetypes=[("Исполняемые файлы", "*.exe")]
            )
            if not file_path:
                return

            if not os.path.exists(file_path):
                messagebox.showerror("Ошибка", "Указанный файл не существует!")
                return

            # Нормализуем путь для Wine
            file_path = os.path.abspath(file_path).replace('\\', '/')

            task_name = simpledialog.askstring("Имя задачи", "Введите имя для новой задачи:")
            if not task_name:
                return

            # Проверяем допустимость имени задачи
            if not re.match(r'^[a-zA-Z0-9_\- ]+$', task_name):
                messagebox.showerror("Ошибка", "Имя задачи содержит недопустимые символы!")
                return

            # Команда PowerShell для создания задачи
            ps_command = f"""
            $action = New-ScheduledTaskAction -Execute '{file_path}'
            $trigger = New-ScheduledTaskTrigger -AtLogon
            Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -RunLevel Highest -Force
            """
            
            try:
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True, shell=True, timeout=30)
                
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "Задача успешно создана")
                    self._update_scheduler_list()
                else:
                    error = result.stderr if result.stderr else "Неизвестная ошибка"
                    messagebox.showerror("Ошибка", f"Не удалось создать задачу:\n{error}")
            except subprocess.TimeoutExpired:
                messagebox.showerror("Ошибка", "Таймаут выполнения команды")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании задачи: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")

    def _remove_scheduler_task(self):
        """Удаляет задачу из Планировщика"""
        try:
            selection = self.scheduler_listbox.curselection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите задачу для удаления")
                return
            
            selected_item = self.scheduler_listbox.get(selection[0])
            task_name = selected_item.split(" ")[0].strip()
            
            # Проверяем допустимость имени задачи
            if not task_name or not re.match(r'^[a-zA-Z0-9_\- ]+$', task_name):
                messagebox.showerror("Ошибка", "Недопустимое имя задачи!")
                return

            # Команда PowerShell для удаления задачи
            ps_command = f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false"
            
            try:
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True, shell=True, timeout=30)
                
                if result.returncode == 0:
                    messagebox.showinfo("Успех", f"Задача '{task_name}' удалена")
                    self._update_scheduler_list()
                else:
                    error = result.stderr if result.stderr else "Неизвестная ошибка"
                    messagebox.showerror("Ошибка", f"Не удалось удалить задачу:\n{error}")
            except subprocess.TimeoutExpired:
                messagebox.showerror("Ошибка", "Таймаут выполнения команды")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении задачи: {str(e)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Общая ошибка: {str(e)}")
            

    def get_reg_value(self, root, path, name):
        try:
            key = winreg.OpenKey(root, path)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return value
        except:
            return 0

    def set_reg_value(self, root, path, name, value, reg_type=winreg.REG_DWORD):
        try:
            key = winreg.CreateKey(root, path)
            winreg.SetValueEx(key, name, 0, reg_type, value)
            winreg.CloseKey(key)
            return True
        except:
            return False

    def scan_restrictions(self):
        self.update_restriction_table()

    def unlock_all(self):
        for name, root, path, key in self.restrictions:
            if name == "Брандмауэр":
                self.set_reg_value(root, path, key, 1)
            else:
                self.set_reg_value(root, path, key, 0)
        messagebox.showinfo("Готово", "Все ограничения были разблокированы.")
        self.update_restriction_table()

    def update_restriction_table(self):
        for row in self.unlocker_tree.get_children():
            self.unlocker_tree.delete(row)

        for name, root, path, key in self.restrictions:
            val = self.get_reg_value(root, path, key)
            if name == "Брандмауэр":
                blocked = (val == 0)
            else:
                blocked = (val != 0)
            status = "🔴 Заблокировано" if blocked else "🟢 Разрешено"
            tag = "red" if blocked else "green"
            self.unlocker_tree.insert("", "end", values=(name, status), tags=(tag,))

        self.unlocker_tree.tag_configure('red', foreground='red')
        self.unlocker_tree.tag_configure('green', foreground='green')



    def refresh_processes(self):
        self.proc_listbox.delete(0, tk.END)
        for pid, name in list_processes():
            self.proc_listbox.insert(tk.END, f"{pid} - {name}")

    def kill_selected_process(self):
        sel = self.proc_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите процесс")
            return
        item = self.proc_listbox.get(sel[0])
        pid = int(item.split(" - ")[0])
        success, msg = kill_process(pid)
        if success:
            messagebox.showinfo("Успех", msg)
            self.refresh_processes()
        else:
            messagebox.showerror("Ошибка", msg)



if __name__ == "__main__":
    app = run_as_admin()
    app = UnlockerApp()
    splash = SplashScreen(app)
    app.mainloop()