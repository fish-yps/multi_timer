# -*- coding: utf-8 -*-
"""YASB Custom Widget 用：查询 MultiTimer 的倒计时状态，输出纯文本。

用法: python timer_status.py
输出: 活跃（运行中/暂停）的倒计时剩余时间，如 "6:59 1:58"。
      无任何活跃倒计时时输出空字符串。
"""

import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 8765


def fmt(sec):
    sec = max(0, int(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main():
    try:
        with socket.create_connection((HOST, PORT), timeout=2) as s:
            s.sendall(b"list")
            data = b""
            while True:
                chunk = s.recv(65536)
                if not chunk:
                    break
                data += chunk
    except (ConnectionRefusedError, OSError):
        sys.stdout.write("")
        return

    try:
        items = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        sys.stdout.write("")
        return

    active = [t for t in items if t.get("state") in ("running", "paused")]
    if not active:
        sys.stdout.write("")
        return

    active.sort(key=lambda t: t["remaining"])
    out = " ".join(fmt(t["remaining"]) for t in active)
    sys.stdout.buffer.write(out.encode("utf-8"))


if __name__ == "__main__":
    main()
