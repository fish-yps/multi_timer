# -*- coding: utf-8 -*-
"""主窗口入口：单实例检查 + 启动 timer_pack 应用。"""

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


def main():
    if not check_single_instance():
        _wake_existing()
        return
    app = TimerPackApp()
    app.mainloop()
