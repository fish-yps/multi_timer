# -*- coding: utf-8 -*-
"""多倒计时命令行控制脚本：通过本地 socket API 控制运行中的程序。

用法:
  python multi_timer_ctl.py add 7:00            添加并开始倒计时
  python multi_timer_ctl.py add 7:00 泡面       添加并命名
  python multi_timer_ctl.py add 120             添加 120 秒
  python multi_timer_ctl.py list                查看所有计时器 (JSON)
  python multi_timer_ctl.py toggle 1            暂停/继续 1 号
  python multi_timer_ctl.py rename 1 新名字     重命名
  python multi_timer_ctl.py remove 1            删除 1 号
  python multi_timer_ctl.py pause               全部暂停
"""

import socket
import sys

HOST = "127.0.0.1"
PORT = 8765


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = " ".join(sys.argv[1:])
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as s:
            s.sendall(cmd.encode("utf-8"))
            reply = s.recv(65536).decode("utf-8", "replace")
        print(reply)
    except (ConnectionRefusedError, OSError):
        print("ERR 连不上多倒计时程序（没启动？）")


if __name__ == "__main__":
    main()
