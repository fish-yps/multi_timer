# -*- coding: utf-8 -*-
"""功能包入口：主窗口、毛玻璃、API socket、计时主循环。"""

import ctypes
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
import winreg

from . import config as C
from .api import ApiServer
from .cards import RoundButton, RoundEntry, TimerCard
from .task import TimerManager, TimerTask

try:
    import pystray
    from PIL import Image
    _HAS_TRAY = True
except ImportError:
    _HAS_TRAY = False


MUTEX_NAME = "MultiTimer_SingleInstance_Mutex"
# WinError 183: ERROR_ALREADY_EXISTS (mutex 已被其他进程持有)
ERROR_ALREADY_EXISTS = 183
# WCA 属性 19 = ACCENT_POLICY (毛玻璃); 玻璃色 ARGB(alpha=0x99, B=0x47, G=0x68, R=0x15)
WCA_ACCENT = 19
GLASS_COLOR = 0x99476815


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [("AccentState", ctypes.c_uint), ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_uint)]


class WINDOW_COMPOSITION_ATTR(ctypes.Structure):
    _fields_ = [("Attribute", ctypes.c_int), ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t)]


def check_single_instance():
    """返回 True 表示当前是唯一实例，False 表示已有实例在运行。"""
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            ctypes.windll.kernel32.CloseHandle(handle)
            return False
        return True
    except Exception:
        return True


def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, C.RUN_KEY, 0,
                            winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, C.APP_NAME)
            return True
    except OSError:
        return False


def autostart_set(enable):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, C.RUN_KEY) as key:
            if enable:
                exe = sys.executable if getattr(sys, "frozen", False) else None
                if not exe:
                    return
                winreg.SetValueEx(key, C.APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
            else:
                try:
                    winreg.DeleteValue(key, C.APP_NAME)
                except OSError:
                    pass
    except OSError:
        pass


def enable_glass(hwnd, state=4, color=GLASS_COLOR):
    """启用 Win10/11 毛玻璃 (Acrylic) 背景。state=4 表示 Acrylic。"""
    try:
        accent = ACCENT_POLICY(state, 2, color, 0)
        data = WINDOW_COMPOSITION_ATTR(
            WCA_ACCENT,
            ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p),
            ctypes.sizeof(accent),
        )
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        return True
    except Exception:
        return False


class TimerPackApp(tk.Tk):
    """把 TimerManager 与 UI 绑定，暴露命令处理给 API。"""

    def __init__(self):
        super().__init__()
        self.title(C.WINDOW_TITLE)
        self.geometry(C.WINDOW_SIZE)
        self.minsize(*C.WINDOW_MIN)
        self.configure(bg=C.BG_GLASS)
        self._set_icon()

        self.manager = TimerManager()
        self.cards = {}  # id -> TimerCard
        self._tray = None
        self._tray_thread = None
        self._quitting = False

        self.manager.load(C.STATE_FILE)

        self._build_topbar()
        self._build_presets()
        self._build_list()
        for task in self.manager.tasks:
            self._make_card(task)

        self._api = ApiServer(self).start()
        self.after(100, self._poll_api)

        self.after(300, lambda: enable_glass(self.winfo_id(), 4))
        self.after(1000, self._tick)
        self.after(2000, self._start_tray)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _poll_api(self):
        self._api.poll()
        self.after(100, self._poll_api)

    def _on_close(self):
        """关闭按钮：最小化到托盘而不是退出。"""
        if self._quitting:
            self._save_state()
            self.destroy()
            return
        self.withdraw()
        if not _HAS_TRAY or self._tray is None:
            self._save_state()
            self.destroy()

    def _save_state(self):
        try:
            self.manager.save(C.STATE_FILE)
        except OSError:
            pass

    def _start_tray(self):
        if not _HAS_TRAY or self._tray is not None:
            return

        def make_image():
            try:
                img = Image.open(self._icon_path())
                return img.resize((64, 64), Image.LANCZOS)
            except Exception:
                return Image.new("RGBA", (64, 64), (21, 104, 71, 255))

        def on_show(icon, item):
            self.after(0, self._show_window)

        def on_quit(icon, item):
            self.after(0, self._quit_app)

        def on_autostart(icon, item):
            enabled = not autostart_enabled()
            autostart_set(enabled)
            icon.update_menu()

        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", on_show, default=True),
            pystray.MenuItem(
                "开机自启",
                on_autostart,
                checked=lambda item: autostart_enabled(),
            ),
            pystray.MenuItem("退出", on_quit),
        )
        self._tray = pystray.Icon(C.APP_NAME, make_image(), "多倒计时", menu)
        self._tray_thread = threading.Thread(target=self._tray.run, daemon=True)
        self._tray_thread.start()

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_app(self):
        self._quitting = True
        self._save_state()
        if self._tray:
            self._tray.stop()
        self.destroy()

    # ---------- UI ----------
    def _icon_path(self):
        for base in (getattr(sys, "_MEIPASS", ""),
                     os.path.dirname(os.path.abspath(__file__)),
                     os.getcwd()):
            path = os.path.join(base, "MultiTimer.ico")
            if os.path.exists(path):
                return path
        return ""

    def _toast_icon_path(self):
        for base in (getattr(sys, "_MEIPASS", ""),
                     os.path.dirname(os.path.abspath(__file__)),
                     os.getcwd()):
            for name in ("MultiTimer_256.png", "MultiTimer_128.png", "MultiTimer.ico"):
                path = os.path.join(base, name)
                if os.path.exists(path):
                    return path
        return ""

    def _set_icon(self):
        path = self._icon_path()
        if path:
            try:
                self.iconbitmap(path)
            except tk.TclError:
                pass

    def _build_topbar(self):
        bar = tk.Frame(self, bg=C.BG_GLASS)
        bar.pack(fill="x", padx=14, pady=(14, 4))
        tk.Label(bar, text=C.WINDOW_TITLE, fg=C.FG, bg=C.BG_GLASS,
                 font=C.FONT_TITLE).pack(side="left")
        tk.Label(bar, text="  时长 分:秒", fg=C.FG_MUTED, bg=C.BG_GLASS,
                 font=C.FONT_LABEL).pack(side="left", padx=(18, 4))
        self.entry = RoundEntry(bar, width=8)
        self.entry.pack(side="left")
        self.entry.entry.insert(0, "25:00")
        self.entry.entry.bind("<Return>", lambda e: self.add_from_entry())
        RoundButton(bar, "添加", self.add_from_entry, C.GREEN, "#eafff4",
                    bold=True).pack(side="left", padx=6)

    def _build_presets(self):
        presets = tk.Frame(self, bg=C.BG_GLASS)
        presets.pack(fill="x", padx=14, pady=(6, 4))
        for sec, text in C.PRESETS:
            RoundButton(presets, text, lambda s=sec: self.on_add(s),
                        C.SURFACE_LIGHT, C.FG_MUTED, width=52).pack(side="left", padx=3)
        RoundButton(presets, "全部暂停", self.on_pause_all,
                    C.SURFACE_LIGHT, C.WARN, width=72).pack(side="right")

    def _build_list(self):
        wrap = tk.Frame(self, bg=C.BG_GLASS)
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        self.canvas = tk.Canvas(wrap, bg=C.BG_GLASS, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.list_frame = tk.Frame(self.canvas, bg=C.BG_GLASS)
        self._win = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._win, width=e.width))
        sb = tk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview,
                          bg=C.SURFACE, troughcolor=C.BG_GLASS, relief="flat", bd=0,
                          activebackground=C.GREEN_BORDER, highlightthickness=0)
        sb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    # ---------- 操作 ----------
    def add_from_entry(self):
        try:
            seconds = TimerTask.parse_time(self.entry.entry.get())
        except (ValueError, IndexError):
            messagebox.showwarning("格式错误", "请输入秒数或 分:秒（如 25:00 或 1:30:00）")
            return
        if seconds <= 0:
            return
        self.on_add(seconds)
        self.entry.entry.delete(0, "end")

    def on_add(self, seconds, name=None):
        task = self.manager.add(seconds, name=name)
        self._make_card(task)
        self._save_state()
        return task

    def _make_card(self, task):
        card = TimerCard(self.list_frame, self, task)
        self.cards[task.id] = card
        if task.state == "running":
            card.start_btn.set_text("暂停")
            card.start_btn.set_style(C.GREEN_BRIGHT, "#eafff4")
        elif task.state == "paused" and task.remaining < task.total:
            card.start_btn.set_text("继续")
            card.start_btn.set_style(C.BTN_PAUSE_BG, C.BTN_PAUSE_FG)
        self._redraw(task)
        return card

    def on_toggle(self, _id):
        task = self.manager.get(_id)
        if not task:
            return
        task.toggle()
        btn = self.cards[_id].start_btn
        if task.state == "running":
            btn.set_text("暂停")
            btn.set_style(C.GREEN_BRIGHT, "#eafff4")
        else:
            btn.set_text("继续")
            btn.set_style(C.BTN_PAUSE_BG, C.BTN_PAUSE_FG)
        self._redraw(task)
        self._save_state()

    def on_pause_all(self):
        self.manager.pause_all()
        for task in self.manager.tasks:
            self.cards[task.id].start_btn.set_text("继续")
            self.cards[task.id].start_btn.set_style(C.BTN_PAUSE_BG, C.BTN_PAUSE_FG)
            self._redraw(task)
        self._save_state()

    def on_remove(self, _id):
        if self.manager.remove(_id):
            self.cards.pop(_id).destroy()
            self._save_state()

    def _redraw(self, task):
        color = C.GREEN_BRIGHT
        if task.state == "paused":
            color = C.WARN
        if task.remaining <= 10:
            color = "#f38ba8"
        card = self.cards.get(task.id)
        if card:
            card.update_time(TimerTask.format_time(task.remaining), color)
            card.update_progress()

    def _tick(self):
        due = self.manager.tick_all()
        for task in self.manager.tasks:
            self._redraw(task)
        for task in due:
            card = self.cards[task.id]
            card.start_btn.set_text("完成")
            card.start_btn.set_style(C.GREEN, "#eafff4")
            self._redraw(task)
            self._show_toast(task)
            task.reset()
            card.start_btn.set_text("重开")
            card.start_btn.set_style(C.GREEN_BRIGHT, "#eafff4")
            self._redraw(task)
        self.after(1000, self._tick)

    def _show_toast(self, task):
        """Windows 原生 toast 通知（系统默认样式与位置）。"""
        try:
            from winotify import Notification
            toast = Notification(
                app_id="MultiTimer",
                title="倒计时已结束",
                msg=f"{task.name} · {TimerTask.format_time(task.total)}",
                icon=self._toast_icon_path(),
                duration="short",
            )
            toast.show()
        except Exception:
            pass

    # ---------- API 命令处理 ----------
    def log(self, msg):
        try:
            with open(C.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(time.strftime("%H:%M:%S") + " " + msg + "\n")
        except OSError:
            pass

    def exec_cmd(self, cmd):
        parts = cmd.strip().split()
        if not parts:
            return "ERR 空命令"
        op = parts[0].lower()
        try:
            if op == "add":
                spec = parts[1] if len(parts) > 1 else ""
                name = " ".join(parts[2:]) if len(parts) > 2 else None
                try:
                    seconds = TimerTask.parse_time(spec)
                except (ValueError, IndexError):
                    return "ERR 时间格式错误: " + spec
                if seconds <= 0:
                    return "ERR 时间必须为正"
                task = self.on_add(seconds, name)
                return f"OK added {task.id} {spec}"
            if op == "rename" and len(parts) > 2:
                _id = int(parts[1])
                name = " ".join(parts[2:])
                if self.manager.rename(_id, name):
                    self._save_state()
                    return "OK renamed"
                return "ERR 未找到 " + parts[1]
            if op == "remove" and len(parts) > 1:
                _id = int(parts[1])
                return "OK removed " + str(_id) if self.on_remove(_id) else "ERR 未找到 " + parts[1]
            if op == "toggle" and len(parts) > 1:
                _id = int(parts[1])
                if self.manager.get(_id):
                    self.on_toggle(_id)
                    return "OK toggled " + str(_id)
                return "ERR 未找到 " + parts[1]
            if op == "pause":
                self.on_pause_all()
                return "OK all paused"
            if op in ("list", "status"):
                return self.manager.to_json()
            if op == "show":
                self.after(0, self._show_window)
                return "OK showing"
            return "ERR 未知命令: " + op
        except (ValueError, IndexError):
            return "ERR 参数错误"
