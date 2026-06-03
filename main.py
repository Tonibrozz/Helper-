import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import psutil
import subprocess
import winreg
import ctypes
import shutil
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
import pathlib

# Global functions
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

def clear_debuggers():
    debuggers = ["ollydbg.exe", "x64dbg.exe", "ida64.exe", "ida.exe", "windbg.exe"]
    errors = []
    for dbg in debuggers:
        result = subprocess.run(f'taskkill /f /im {dbg}', shell=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            errors.append(dbg)
    if errors:
        return False, f"Не удалось завершить: {', '.join(errors)}"
    return True, "Отладчики завершены"

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
            self.start_shining()  
        else:
            self.after(30, self.animate)

    def start_shining(self):
        if self.shine_count >= self.max_shines:
            self.finish()  
            return

        if self.shine_count % 2 == 0:  
            self.canvas.itemconfig(self.letter_h, fill="cyan")
            self.canvas.itemconfig(self.letter_p, fill="cyan")
        else:
            self.canvas.itemconfig(self.letter_h, fill="black")
            self.canvas.itemconfig(self.letter_p, fill="black")

        self.shine_count += 1
        self.after(300, self.start_shining)  

    def finish(self):
        self.destroy()
        self.parent.deiconify()

class UnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WinUnlocker")
        self.geometry("483x453")
        self['bg'] = 'black'
        self.withdraw()

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
                foreground=[('selected', '#00ffcc')])

        self.tabs = ttk.Notebook(self, style='lefttab.TNotebook')
        self.tabs.pack(fill='both', expand=True)

        # Create tabs
        self.protection_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.process_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.autorun_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.tinstall_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.explorer_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.winlogon_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.asses_tab = ttk.Frame(self.tabs, style='Dark.TFrame')
        self.uninstaller_tab = ttk.Frame(self.tabs, style='Dark.TFrame')

        self.tabs.add(self.protection_tab, text="Защита")
        self.tabs.add(self.process_tab, text="Диспетчер\nзадач")
        self.tabs.add(self.autorun_tab, text="Авто\nзапуск")
        self.tabs.add(self.tinstall_tab, text="Установить\nи следить")
        self.tabs.add(self.uninstaller_tab, text="Удаление")
        self.tabs.add(self.explorer_tab, text="Проводник")
        self.tabs.add(self.winlogon_tab, text="Winlogon")
        self.tabs.add(self.asses_tab, text="Ассоциации")

        self.create_protection_tab()
        self.create_process_tab()
        self.create_autorun_tab()
        self.create_tinstall_tab()
        self.create_explorer_tab()
        self.create_winlogon_tab()
        self.create_asses_tab()
        self.create_uninstaller_tab()

    def is_potentially_dangerous(self, proc):
        try:
            path = proc.exe()
            score = 0

            if "AppData" in path or "Temp" in path:
                score += 1
            if not os.path.exists(path):
                score += 1
            if not path.lower().endswith(".exe"):
                score += 1
            if "Program Files" not in path:
                score += 1

            if score >= 3:
                return True, "⚠ ПОДОЗРИТЕЛЬНО"
            return False, ""
        except:
            return False, ""

    def list_processes(self):
        procs = []
        pid_map = {}

        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'exe']):
            pid_map[proc.pid] = proc

        def get_indent_level(proc):
            level = 0
            try:
                while proc.ppid() in pid_map:
                    proc = pid_map[proc.ppid()]
                    level += 1
            except:
                pass
            return level

        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'exe']):
            indent = "  " * get_indent_level(proc)
            is_danger, label = self.is_potentially_dangerous(proc)
            name = f"{indent}{proc.name()} {label}".strip()
            procs.append((proc.pid, name))

        return procs

    def kill_process(self, pid):
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)
            for child in children:
                child.kill()
            proc.kill()
            return True, f"Процесс {pid} и {len(children)} дочерних завершены."
        except psutil.NoSuchProcess:
            return False, "Процесс не найден."
        except Exception as e:
            return False, f"Ошибка завершения: {e}"

    def create_protection_tab(self):
        btn_youtube = ttk.Button(self.protection_tab, text="Автор", command=self.open_youtube)
        btn_youtube.pack(padx=10, pady=5)

        btn_teleqram = ttk.Button(self.protection_tab, text="служба поддержки", command=self.open_telegram)
        btn_teleqram.pack(pady=10)

        btn_create_proc = ttk.Button(self.protection_tab, text="запустить Проводник", command=start_explorer)
        btn_create_proc.pack(pady=10)

        btn_clear_debug = ttk.Button(self.protection_tab, text="Очистка от дебагеров", command=self.clear_debuggers)
        btn_clear_debug.pack(pady=10)

        btn_fontreset = ttk.Button(self.protection_tab, text='Восстановить шрифты', command=self.install_font)
        btn_fontreset.pack(pady=10)

        btn_unblock_taskmgr = ttk.Button(self.protection_tab, 
                                       text="Разблокировать Диспетчер задач", 
                                       command=self.unblock_taskmgr)
        btn_unblock_taskmgr.pack(pady=10)

        btn_block_taskmgr = ttk.Button(self.protection_tab, 
                                      text="Заблокировать Диспетчер задач", 
                                      command=self.block_taskmgr)
        btn_block_taskmgr.pack(pady=10)

        btn_unblock_registry = ttk.Button(self.protection_tab, 
                                         text="Разблокировать Редактор реестра", 
                                         command=self.unblock_registry)
        btn_unblock_registry.pack(pady=10)

        footer = ttk.Label(self.protection_tab, text="ToniBrozz©", 
                          background='#000000', foreground='#ffffff')
        footer.pack(side="bottom", anchor="se", padx=10, pady=5)

    def install_font(self):
        font_file = "arial.ttf"
        font_name = os.path.basename(font_file)
        fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
        dest_path = os.path.join(fonts_dir, font_name)

        try:
            shutil.copy(font_file, dest_path)

            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "Arial (TrueType)", 0, winreg.REG_SZ, font_name)

            ctypes.windll.gdi32.AddFontResourceW(dest_path)
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  

            messagebox.showinfo("Успешно", f"Шрифт {font_name} установлен.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить шрифт:\n{e}")

    def open_youtube(self):
        webbrowser.open_new("https://www.youtube.com/@TONIBROZZ")

    def start_explorer(self):
        create_process("explorer.exe")

    def clear_debuggers(self):
        success, msg = clear_debuggers()
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

    def open_telegram(self):
        webbrowser.open("https://t.me/ToniBroz")

    def create_asses_tab(self):
        label = ttk.Label(self.asses_tab, text="Восстановление ассоциаций файлов", font=("Arial", 12))
        label.pack(pady=10)

        restore_button = ttk.Button(
            self.asses_tab,
            text="Восстановить ассоциации",
            command=self.restore_associations
        )
        restore_button.pack(pady=10)

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
                run = messagebox.askyesno("Удалить через системный Uninstaller?", 
                                        f"Удалить {name} через стандартный деинсталлятор?")
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

    def create_explorer_tab(self):
        def delete_selected():
            try:
                picked = listbox.get(listbox.curselection()[0])
                path = os.path.join(current_path.get(), picked)

                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)

                path_change()
            except Exception as e:
                print(f"Ошибка при удалении: {e}")

        ctypes.windll.shcore.SetProcessDpiAwareness(True)

        def path_change(*args):
            listbox.delete(0, tk.END)
            try:
                directory = os.listdir(current_path.get())
                for file in directory:
                    listbox.insert(tk.END, file)
            except Exception as e:
                print(f"Ошибка: {e}")

        def change_path_by_click(event=None):
            try:
                picked = listbox.get(listbox.curselection()[0])
                path = os.path.join(current_path.get(), picked)
                if os.path.isfile(path):
                    os.startfile(path)
                else:
                    current_path.set(path)
            except:
                pass

        def go_back():
            new_path = pathlib.Path(current_path.get()).parent
            current_path.set(str(new_path))

        def windows_new_file_or_folder():
            global new_window
            new_window = tk.Toplevel(self)
            new_window.geometry('250x150')
            new_window.resizable(0, 0)
            new_window.title('Новый файл или папка')
            tk.Label(new_window, text="Введите название нового файла/папки").pack(pady=10)
            tk.Entry(new_window, textvariable=new_file_name).pack(pady=5)
            tk.Button(new_window, text='Создать', command=new_file_or_folder).pack(pady=10)

        def new_file_or_folder():
            name = new_file_name.get()
            full_path = os.path.join(current_path.get(), name)
            try:
                if '.' in name:
                    open(full_path, 'w').close()
                else:
                    os.mkdir(full_path)
                path_change()
                new_window.destroy()
            except Exception as e:
                print(f"Ошибка при создании: {e}")

        new_file_name = tk.StringVar(value="Блокнот.txt")
        current_path = tk.StringVar(value=str(pathlib.Path.cwd()))
        current_path.trace_add("write", path_change)

        tk.Entry(self.explorer_tab, textvariable=current_path).grid(row=0, column=0, columnspan=2, sticky="nsew", ipady=5, padx=5, pady=5)

        btn_back = ttk.Button(self.explorer_tab, text="Назад", command=go_back)
        btn_back.grid(row=1, column=0, sticky="ew", padx=5)

        btn_new = ttk.Button(self.explorer_tab, text="Новый файл/папка", command=windows_new_file_or_folder)
        btn_new.grid(row=1, column=1, sticky="ew", padx=5)

        btn_delete = ttk.Button(self.explorer_tab, text="Удалить", command=delete_selected)
        btn_delete.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        listbox = tk.Listbox(self.explorer_tab)
        listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        listbox.bind("<Double-Button-1>", change_path_by_click)

        self.explorer_tab.grid_rowconfigure(2, weight=1)
        self.explorer_tab.grid_columnconfigure(0, weight=1)
        self.explorer_tab.grid_columnconfigure(1, weight=1)

        path_change()

    def create_process_tab(self):
        frame = ttk.Frame(self.process_tab)
        frame.pack(fill='both', expand=True)

        self.proc_listbox = tk.Listbox(frame)
        self.proc_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.proc_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.proc_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(self.process_tab)
        btn_frame.pack(fill='x')

        btn_refresh = ttk.Button(btn_frame, text="Обновить", command=self.refresh_processes)
        btn_refresh.pack(side='left', padx=5, pady=5)

        btn_kill = ttk.Button(btn_frame, text="Завершить процесс", command=self.kill_selected_process)
        btn_kill.pack(side='left', padx=5, pady=5)

        self.refresh_processes()

    def kill_selected_process(self):
        sel = self.proc_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите процесс")
            return
        item = self.proc_listbox.get(sel[0])
        pid = int(item.split(" - ")[0])
        success, msg = self.kill_process(pid)
        if success:
            messagebox.showinfo("Успех", msg)
            self.refresh_processes()
        else:
            messagebox.showerror("Ошибка", msg)

    def refresh_processes(self):
        self.proc_listbox.delete(0, tk.END)
        for pid, name in self.list_processes():
            self.proc_listbox.insert(tk.END, f"{pid} - {name}")

    def create_tinstall_tab(self):
        global exe_path, log_file
        exe_path = None
        log_file = "install_monitor_log.txt"

        log_text = scrolledtext.ScrolledText(self.tinstall_tab, width=85, height=20)
        log_text.pack(padx=10, pady=10, expand=True, fill='both')

        def log_to_interface(text):
            log_text.insert(tk.END, text + "\n")
            log_text.see(tk.END)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")

        class FileActivityHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                log_to_interface(f"FILE: {event.event_type.upper()} - {event.src_path}")

        def launch_and_monitor():
            global monitored_process, observer

            if not exe_path:
                messagebox.showerror("Ошибка", "Выберите EXE файл.")
                return

            log_to_interface(f"\n[ЗАПУСК ПРОГРАММЫ]: {exe_path}")
            try:
                monitored_process = subprocess.Popen([exe_path], shell=False)
                pid = monitored_process.pid
                proc = psutil.Process(pid)
            except Exception as e:
                log_to_interface(f"[Ошибка запуска]: {e}")
                return

            observer = Observer()
            observer.schedule(FileActivityHandler(), "C:\\", recursive=True)
            observer.start()

            try:
                while proc.is_running():
                    open_files = proc.open_files()
                    if open_files:
                        for f in open_files:
                            log_to_interface(f"PROC: открыт файл — {f.path}")
                    time.sleep(2)
            except Exception as e:
                log_to_interface(f"[Ошибка мониторинга]: {e}")

            observer.stop()
            observer.join()
            log_to_interface("[ЗАВЕРШЕНО]: Мониторинг завершен.")

        def choose_exe():
            global exe_path
            exe_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
            exe_label.config(text=f"Выбрано: {exe_path}")

        ttk.Button(self.tinstall_tab, text="Выбрать программу", command=choose_exe).pack(pady=5)
        exe_label = tk.Label(self.tinstall_tab, text="Выбрано: ничего")
        exe_label.pack()

        ttk.Button(self.tinstall_tab, text="▶ Запустить и следить", 
                  command=lambda: threading.Thread(target=launch_and_monitor).start()).pack(pady=10)

    def create_autorun_tab(self):
        def get_startup_apps():
            startup_apps = []
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_apps.append((name, value))
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Ошибка при чтении реестра: {e}")
            return startup_apps

        def update_listbox():
            apps = get_startup_apps()
            self.listbox.delete(0, tk.END)
            for name, value in apps:
                self.listbox.insert(tk.END, f"{name}: {value}")

        def add_to_startup():
            file_path = filedialog.askopenfilename(
                title="Выберите файл для добавления в автозагрузку",
                filetypes=[("Все файлы", "*.*")]
            )
            if file_path:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                       0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, os.path.basename(file_path), 0, winreg.REG_SZ, file_path)
                    winreg.CloseKey(key)
                    messagebox.showinfo("Успех", "Программа добавлена в автозагрузку")
                    update_listbox()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось добавить в автозагрузку: {e}")

        def remove_from_startup():
            selection = self.listbox.curselection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите программу для удаления")
                return
            
            selected_item = self.listbox.get(selection[0])
            app_name = selected_item.split(":")[0].strip()
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                    0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, app_name)
                winreg.CloseKey(key)
                messagebox.showinfo("Успех", f"Программа '{app_name}' удалена из автозагрузки")
                update_listbox()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить программу: {e}")

        self.listbox = tk.Listbox(self.autorun_tab, width=80)
        self.listbox.pack(padx=10, pady=10, expand=True, fill='both')

        btn_frame = ttk.Frame(self.autorun_tab)
        btn_frame.pack(pady=5)

        update_button = ttk.Button(btn_frame, text="Обновить", command=update_listbox)
        update_button.pack(side='left', padx=5)

        add_button = ttk.Button(btn_frame, text="Добавить", command=add_to_startup)
        add_button.pack(side='left', padx=5)

        remove_button = ttk.Button(btn_frame, text="Удалить", command=remove_from_startup)
        remove_button.pack(side='left', padx=5)

        update_listbox()

    def create_winlogon_tab(self):
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

        shell_val = tk.StringVar()
        userinit_val = tk.StringVar()

        ttk.Label(self.winlogon_tab, text="Shell (explorer.exe):").pack(anchor="w", padx=10, pady=5)
        tk.Entry(self.winlogon_tab, textvariable=shell_val, width=80).pack(padx=10)

        ttk.Label(self.winlogon_tab, text="Userinit (userinit.exe,):").pack(anchor="w", padx=10, pady=5)
        tk.Entry(self.winlogon_tab, textvariable=userinit_val, width=80).pack(padx=10)

        tk.Button(self.winlogon_tab, text="Сохранить изменения", command=save_values).pack(pady=10)
        tk.Button(self.winlogon_tab, text="Обновить значения", command=update_values).pack()

        update_values()

if __name__ == "__main__":
    app = UnlockerApp()
    splash = SplashScreen(app)
    app.mainloop()