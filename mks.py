import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class WindowsActivator:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Activator")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Стиль
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Активатор Windows", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Информация
        info_text = """Выберите тип активации:
        • KMS - временная активация (180 дней)
        • Online - постоянная активация"""
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Выбор типа активации
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(pady=(0, 20))
        
        ttk.Label(mode_frame, text="Тип активации:").pack(side=tk.LEFT)
        
        self.activation_mode = tk.StringVar(value="kms")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.activation_mode, 
                                 values=["kms", "online"], state="readonly", width=10)
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопка активации
        self.activate_btn = ttk.Button(main_frame, text="Активировать Windows", 
                                      command=self.start_activation)
        self.activate_btn.pack(pady=(0, 10))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к активации", 
                                     foreground="green")
        self.status_label.pack()
        
        # Лог
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        ttk.Label(log_frame, text="Лог выполнения:").pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, height=6, font=('Consolas', 8))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_message(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_command(self, command):
        """Выполняет команду и возвращает результат"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                   text=True, encoding='cp866')
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def activate_windows(self):
        """Выполняет активацию Windows"""
        self.activate_btn.config(state='disabled')
        self.progress.start(10)
        self.status_label.config(text="Идет активация...", foreground="orange")
        self.log_message("Начало процесса активации...")
        
        try:
            if self.activation_mode.get() == "kms":
                # KMS активация
                self.log_message("Установка KMS-сервера...")
                commands = [
                    'slmgr /upk',
                    'slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX',
                    'slmgr /skms kms8.msguides.com',
                    'slmgr /ato'
                ]
            else:
                # Online активация
                self.log_message("Онлайн активация...")
                commands = [
                    'slmgr /upk',
                    'slmgr /ipk TX9XD-98N7V-6WMQ6-BX7FG-H8Q99',
                    'slmgr /ato'
                ]
            
            for cmd in commands:
                self.log_message(f"Выполнение: {cmd}")
                returncode, stdout, stderr = self.run_command(cmd)
                
                if returncode == 0:
                    self.log_message("Успешно!")
                    if stdout:
                        self.log_message(stdout.strip())
                else:
                    self.log_message(f"Ошибка: {stderr}")
            
            # Проверка статуса
            self.log_message("Проверка статуса активации...")
            returncode, stdout, stderr = self.run_command('slmgr /xpr')
            
            if returncode == 0:
                self.log_message(stdout)
                self.status_label.config(text="Активация завершена!", foreground="green")
                messagebox.showinfo("Успех", "Активация выполнена успешно!")
            else:
                self.status_label.config(text="Ошибка активации", foreground="red")
                messagebox.showerror("Ошибка", "Произошла ошибка при активации")
                
        except Exception as e:
            self.log_message(f"Критическая ошибка: {str(e)}")
            self.status_label.config(text="Ошибка", foreground="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        
        finally:
            self.progress.stop()
            self.activate_btn.config(state='normal')
    
    def start_activation(self):
        """Запускает активацию в отдельном потоке"""
        thread = threading.Thread(target=self.activate_windows)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = WindowsActivator(root)
    root.mainloop()

if __name__ == "__main__":
    main()