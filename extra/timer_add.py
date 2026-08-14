# -*- coding: utf-8 -*-
"""YASB Custom Widget 用：点击添加一个倒计时。

用法: python timer_add.py <时长>
      时长格式: 秒 或 分:秒 (如 300 或 5:00)
"""

import socket
import sys

HOST = "127.0.0.1"
PORT = 8765


def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else "25:00"
    try:
        with socket.create_connection((HOST, PORT), timeout=3) as s:
            s.sendall(f"add {spec}".encode("utf-8"))
            _ = s.recv(4096)
    except (ConnectionRefusedError, OSError):
        pass


if __name__ == "__main__":
    main()
