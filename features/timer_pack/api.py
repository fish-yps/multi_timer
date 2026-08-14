# -*- coding: utf-8 -*-
"""本地 socket API 服务器：供外部命令行/YASB 等控制运行中的程序。

协议：单行文本命令，响应单行文本。
命令: add <时长> [名称] | remove <id> | toggle <id> | rename <id> <名称>
      | pause | list | show
"""

import queue
import socket
import threading
import time

from . import config as C

RECV_BUF = 65536


class ApiServer:
    """独立线程监听端口，命令投递到主线程队列执行。"""

    def __init__(self, app):
        self.app = app
        self._queue = queue.Queue()

    def start(self):
        threading.Thread(target=self._server_loop, daemon=True).start()
        return self

    def poll(self):
        """由主线程定时调用，执行排队命令。"""
        try:
            while True:
                cmd, reply_box = self._queue.get_nowait()
                try:
                    reply = self.app.exec_cmd(cmd)
                except Exception as e:
                    self.app.log(f"exec 异常: {e!r}")
                    reply = "ERR 内部错误"
                self._queue.task_done()
                reply_box.put(reply)
        except queue.Empty:
            pass

    def _server_loop(self):
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((C.API_HOST, C.API_PORT))
            srv.listen(5)
        except OSError:
            return
        while True:
            try:
                conn, _ = srv.accept()
            except OSError:
                break
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn):
        try:
            with conn:
                data = conn.recv(RECV_BUF).decode("utf-8", "replace").strip()
                if not data:
                    return
                self.app.log(f"收到: {data}")
                reply_box = queue.Queue()
                self._queue.put((data, reply_box))
                try:
                    reply = reply_box.get(timeout=10)
                except queue.Empty:
                    reply = "ERR 超时"
                self.app.log(f"回复: {reply[:120]}")
                conn.sendall(reply.encode("utf-8"))
        except OSError:
            pass
