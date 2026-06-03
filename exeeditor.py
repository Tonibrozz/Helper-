import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pefile
import os

class ExeInspectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EXE Инспектор")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.selected_file = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)

        title = tk.Label(frame, text="Выберите EXE файл для анализа", font=("Arial", 14))
        title.pack(pady=10)

        select_btn = tk.Button(frame, text="Выбрать файл", command=self.choose_file)
        select_btn.pack(pady=5)

        self.file_label = tk.Label(frame, textvariable=self.selected_file, wraplength=400, fg="blue")
        self.file_label.pack(pady=5)

        self.btn_code = tk.Button(frame, text="Просмотреть байткод", command=self.view_code)
        self.btn_files = tk.Button(frame, text="Структура EXE", command=self.view_structure)

        # Кнопки появятся только после выбора файла

    def choose_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("EXE files", "*.exe")])
        if filepath:
            self.selected_file.set(filepath)
            self.btn_code.pack(pady=5)
            self.btn_files.pack(pady=5)

    def view_code(self):
        filepath = self.selected_file.get()
        try:
            pe = pefile.PE(filepath)
            code = ""
            for section in pe.sections:
                name = section.Name.decode(errors="ignore").strip()
                hex_data = section.get_data()[:64].hex()  # первые 64 байта
                code += f"[{name}]\n{hex_data}\n\n"
            self.show_text_window("Байткод EXE (первые 64 байта каждой секции)", code)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать код: {e}")

    def view_structure(self):
        filepath = self.selected_file.get()
        try:
            pe = pefile.PE(filepath)
            info = f"Файл: {os.path.basename(filepath)}\n\nСекции EXE:\n"
            for section in pe.sections:
                name = section.Name.decode(errors="ignore").strip()
                size = section.SizeOfRawData
                addr = hex(section.VirtualAddress)
                info += f"{name:<10} | Размер: {size:<8} | Адрес: {addr}\n"
            self.show_text_window("Структура EXE файла", info)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать EXE: {e}")

    def show_text_window(self, title, content):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
        text.insert(tk.END, content)
        text.pack(expand=True, fill='both')


# Запуск программы
if __name__ == "__main__":
    root = tk.Tk()
    app = ExeInspectorApp(root)
    root.mainloop()
