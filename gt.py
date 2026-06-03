import tkinter as tk
from tkinter import Canvas

class FullscreenSplash(tk.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.update_idletasks()
        self.screen_w = self.winfo_screenwidth()
        self.screen_h = self.winfo_screenheight()
        self.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.configure(bg='black')

        self.canvas = Canvas(self, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Центр и размеры
        self.center_x = self.screen_w // 2
        self.center_y = self.screen_h // 2
        self.dot_radius = 50
        self.max_radius = max(self.screen_w, self.screen_h) * 1.2  # до фуллскрина
        self.green_radius = self.dot_radius

        # Положение изначальное
        self.green_x = -self.dot_radius * 2
        self.blue_x = self.screen_w + self.dot_radius * 2

        # Объекты
        self.dot_green = self.canvas.create_oval(0, 0, 0, 0, fill='green', outline='')
        self.dot_blue = self.canvas.create_oval(0, 0, 0, 0, fill='blue', outline='')

        self.text = self.canvas.create_text(
            self.center_x, self.center_y,
            text='Helper++',
            font=('Helvetica', 48, 'bold'),
            fill='black',
            state='hidden'
        )

        self.t = 0.0
        self.phase = "move"
        self.animate()

    def animate(self):
        if self.phase == "move":
            if self.t < 1.0:
                ease = lambda t: t * t * (3 - 2 * t)
                t_mod = ease(self.t)

                # Плавное движение
                target_green = self.center_x - self.dot_radius
                target_blue = self.center_x + self.dot_radius

                self.green_x = -self.dot_radius * 2 + (target_green + self.dot_radius * 2) * t_mod
                self.blue_x = self.screen_w + self.dot_radius * 2 - (self.screen_w - target_blue) * t_mod

                # Синяя под зелёной (вначале отрисовываем её)
                self.update_dot(self.dot_blue, self.blue_x, self.center_y, self.dot_radius)
                self.update_dot(self.dot_green, self.green_x, self.center_y, self.green_radius)

                self.t += 0.01
                self.after(10, self.animate)
            else:
                # Синяя исчезает, зелёная на центре
                self.canvas.delete(self.dot_blue)
                self.phase = "expand"
                self.t = 0.0
                self.animate()

        elif self.phase == "expand":
            if self.t < 1.0:
                # Плавное расширение зелёной точки
                self.green_radius = self.dot_radius + (150 - self.dot_radius) * self.t
                self.update_dot(self.dot_green, self.center_x, self.center_y, self.green_radius)

                self.t += 0.02
                self.after(10, self.animate)
            else:
                self.phase = "show_text"
                self.t = 0.0
                self.canvas.itemconfigure(self.text, state='normal')
                self.after(1000, self.animate)

        elif self.phase == "show_text":
            # Ждём секунду, затем скрываем текст
            self.phase = "fade_text"
            self.t = 0.0
            self.animate()

        elif self.phase == "fade_text":
            if self.t < 1.0:
                alpha = int(255 * (1 - self.t))
                color = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
                self.canvas.itemconfigure(self.text, fill=color)
                self.t += 0.03
                self.after(30, self.animate)
            else:
                self.canvas.itemconfigure(self.text, state='hidden')
                self.phase = "full_expand"
                self.t = 0.0
                self.animate()

        elif self.phase == "full_expand":
            if self.green_radius < self.max_radius:
                self.green_radius += 20
                self.update_dot(self.dot_green, self.center_x, self.center_y, self.green_radius)
                self.after(16, self.animate)
            else:
                self.destroy()

    def update_dot(self, dot_id, center_x, center_y, radius):
        self.canvas.coords(
            dot_id,
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        )

if __name__ == "__main__":
    FullscreenSplash().mainloop()
