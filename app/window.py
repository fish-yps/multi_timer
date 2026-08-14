# -*- coding: utf-8 -*-
"""主窗口入口：语言选择 + 单实例检查 + 启动 timer_pack 应用。"""

import tkinter as tk

from features.timer_pack.pack import TimerPackApp, check_single_instance
from features.timer_pack import config as C


def _wake_existing():
    """让已运行的实例显示窗口，然后静默退出。"""
    import socket
    try:
        with socket.create_connection((C.API_HOST, C.API_PORT), timeout=2) as s:
            s.sendall(b"show")
            _ = s.recv(1024)
    except OSError:
        pass


def _choose_language():
    """弹出语言选择对话框，返回 'zh' 或 'en'。"""
    root = tk.Tk()
    root.title(C.APP_NAME)
    root.configure(bg=C.BG_GLASS)
    root.resizable(False, False)

    choice = {"lang": None}
    w, h = 340, 170
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    root.attributes("-topmost", True)

    tk.Label(root, text="Choose Language / 选择语言", fg=C.FG, bg=C.BG_GLASS,
             font=("Microsoft YaHei UI", 12, "bold")).pack(pady=(24, 18))

    btns = tk.Frame(root, bg=C.BG_GLASS)
    btns.pack()

    def pick(lang):
        choice["lang"] = lang
        root.destroy()

    tk.Button(btns, text="English", font=("Segoe UI", 11, "bold"),
              bg=C.GREEN, fg="#eafff4", activebackground=C.GREEN_BRIGHT,
              activeforeground="#eafff4", relief="flat", bd=0,
              padx=22, pady=6, cursor="hand2",
              command=lambda: pick("en")).pack(side="left", padx=10)

    tk.Button(btns, text="中文", font=("Microsoft YaHei UI", 11, "bold"),
              bg=C.SURFACE_LIGHT, fg=C.FG, activebackground=C.SURFACE,
              activeforeground=C.FG, relief="flat", bd=0,
              padx=22, pady=6, cursor="hand2",
              command=lambda: pick("zh")).pack(side="left", padx=10)

    root.mainloop()
    return choice["lang"] or "zh"


def main():
    if not check_single_instance():
        _wake_existing()
        return
    lang = _choose_language()
    C.LANG = lang
    app = TimerPackApp()
    app.mainloop()
