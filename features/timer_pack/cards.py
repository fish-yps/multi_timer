# -*- coding: utf-8 -*-
"""圆角 UI 组件：RoundButton / RoundEntry / TimerCard。"""

import tkinter as tk

from . import config as C


def _lighten(hexc, f=0.3):
    hexc = hexc.lstrip("#")
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, int(r + (255 - r) * f))
    g = min(255, int(g + (255 - g) * f))
    b = min(255, int(b + (255 - b) * f))
    return f"#{r:02x}{g:02x}{b:02x}"


def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundButton(tk.Canvas):
    def __init__(self, master, text, command, bg, fg, bold=False,
                 width=74, height=30, radius=9, surface=None):
        super().__init__(master, bg=surface if surface else master["bg"],
                         highlightthickness=0, bd=0, width=width, height=height,
                         cursor="hand2")
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._bold = bold
        self._bw = width
        self._bh = height
        self._br = radius
        self.bind("<Button-1>", lambda e: self._command())
        self.bind("<Enter>", lambda e: self._paint(_lighten(self._bg, 0.25)))
        self.bind("<Leave>", lambda e: self._paint(self._bg))
        self._paint(self._bg)

    def _paint(self, bg):
        self.delete("all")
        _round_rect(self, 1, 1, self._bw - 1, self._bh - 1, self._br, fill=bg, outline="")
        self.create_text(self._bw / 2, self._bh / 2, text=self._text, fill=self._fg,
                         font=("Microsoft YaHei UI", 9, "bold" if self._bold else "normal"))

    def set_text(self, text):
        self._text = text
        self._paint(self._bg)

    def set_bg(self, bg):
        self._bg = bg
        self._paint(bg)

    def set_fg(self, fg):
        self._fg = fg
        self._paint(self._bg)

    def set_style(self, bg, fg):
        self._bg = bg
        self._fg = fg
        self._paint(bg)


class RoundEntry(tk.Frame):
    def __init__(self, master, width=8, font=C.FONT_ENTRY):
        super().__init__(master, bg=master["bg"])
        self.canvas = tk.Canvas(self, bg=master["bg"], highlightthickness=0, bd=0,
                                width=104, height=32, cursor="xterm")
        self.canvas.pack()
        self.entry = tk.Entry(self.canvas, width=width, font=font, justify="center",
                              bg=C.SURFACE, fg=C.GREEN_BRIGHT,
                              insertbackground=C.GREEN_BRIGHT, relief="flat",
                              bd=0, highlightthickness=0)
        self._id = self.canvas.create_window(52, 16, window=self.entry, anchor="center")
        self.canvas.bind("<Configure>", lambda e: self._layout())
        self._layout()

    def _layout(self):
        w = self.canvas.winfo_width() or 1
        self.canvas.delete("rect")
        _round_rect(self.canvas, 1, 1, w - 1, 30, 9, fill=C.SURFACE,
                    outline=C.GREEN_BORDER, tags="rect")
        self.canvas.coords(self._id, w // 2, 16)
        self.canvas.itemconfig(self._id, width=w - 20, height=28)


class TimerCard:
    """单个计时器的圆角卡片，仅负责展示与转发用户操作。"""

    def __init__(self, master, app, task):
        self.app = app
        self.task = task
        self.card = tk.Canvas(master, bg=C.BG_GLASS, highlightthickness=0, bd=0, height=92)
        self.card.pack(fill="x", pady=4)
        self.start_btn = RoundButton(self.card, "开始",
                                     lambda: app.on_toggle(task.id),
                                     C.GREEN, "#eafff4", bold=True, width=64,
                                     surface=C.SURFACE)
        self.del_btn = RoundButton(self.card, "删除",
                                   lambda: app.on_remove(task.id),
                                   C.BTN_DELETE_BG, C.BTN_DELETE_FG, width=64,
                                   surface=C.SURFACE)
        self._btn1 = self.card.create_window(0, 0, window=self.start_btn, anchor="ne")
        self._btn2 = self.card.create_window(0, 0, window=self.del_btn, anchor="ne")
        self.card.bind("<Configure>", lambda e: self._layout(e.width))
        self.card.bind("<Double-Button-1>", self._on_double_click)
        self._layout(200)

    def _on_double_click(self, event):
        """双击名称区域 -> 弹出改名输入。"""
        try:
            win = tk.Toplevel(self.card)
            win.overrideredirect(True)
            win.configure(bg=C.GREEN_DARK)
            win.attributes("-topmost", True)
            x = self.card.winfo_rootx() + 10
            y = self.card.winfo_rooty() + 6
            win.geometry(f"220x40+{x}+{y}")

            entry = tk.Entry(win, font=C.FONT_LABEL, bg=C.SURFACE, fg=C.FG,
                             insertbackground=C.GREEN_BRIGHT, relief="flat",
                             highlightthickness=1, highlightbackground=C.GREEN_BORDER,
                             highlightcolor=C.GREEN_BRIGHT)
            entry.pack(fill="both", expand=True, padx=4, pady=4)
            entry.insert(0, self.task.name)
            entry.focus_set()
            entry.select_range(0, "end")

            def submit(event=None):
                name = entry.get().strip()
                if name:
                    self.task.name = name
                    if self.card.winfo_exists():
                        self.card.itemconfig("name_t", text=name)
                    save = getattr(self.app, "_save_state", None)
                    if save:
                        save()
                win.destroy()

            def cancel(event=None):
                win.destroy()

            entry.bind("<Return>", submit)
            entry.bind("<Escape>", cancel)
            win.focus_force()
        except tk.TclError:
            pass

    def _layout(self, w):
        self.card.coords(self._btn1, w - 12, 16)
        self.card.coords(self._btn2, w - 12, 52)
        self.card.delete("card_bg", "prog", "progfill", "name_t", "time_t")
        _round_rect(self.card, 2, 2, w - 2, 90, 12, fill=C.SURFACE,
                    outline=C.GREEN_BORDER, tags="card_bg")
        self.card.create_text(16, 20, text=self.task.name, anchor="w", fill=C.FG_MUTED,
                              font=C.FONT_LABEL, tags="name_t")
        self.card.create_text(16, 46, text="", anchor="w", fill=C.GREEN_BRIGHT,
                              font=C.FONT_TIME, tags="time_t")
        _round_rect(self.card, 16, 76, max(w - 200, 20), 84, 4, fill=C.GREEN_DARK, tags="prog")
        self.card.create_rectangle(16, 76, 16, 84, fill=C.GREEN, outline="", tags="progfill")
        self.update_progress()

    def update_time(self, text, color):
        if self.card.winfo_exists():
            self.card.itemconfig("time_t", text=text, fill=color)

    def update_progress(self):
        try:
            maxw = max(self.card.winfo_width() - 200, 20)
            frac = max(0.0, 1.0 - self.task.remaining / max(1, self.task.total))
            if self.card.winfo_exists():
                self.card.coords("progfill", 16, 76, 16 + maxw * frac, 84)
        except tk.TclError:
            pass

    def destroy(self):
        self.card.destroy()
