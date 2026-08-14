# -*- coding: utf-8 -*-
"""计时器核心逻辑：多倒计时状态管理与计时滴答。"""

import json

from . import config as C


class TimerTask:
    def __init__(self, _id, total, name=None):
        self.id = _id
        self.total = int(total)
        self.remaining = self.total
        self.name = name or f"{C.tr('timer_default')} {_id}"
        self.state = "paused"  # running / paused / done

    def start(self):
        self.state = "running"

    def pause(self):
        if self.state == "running":
            self.state = "paused"

    def toggle(self):
        self.state = "running" if self.state != "running" else "paused"

    def reset(self):
        self.remaining = self.total
        self.state = "paused"

    def tick(self):
        """每秒调用一次，返回 True 表示到点。"""
        if self.state != "running":
            return False
        self.remaining -= 1
        if self.remaining <= 0:
            self.remaining = 0
            self.state = "done"
            return True
        return False

    def to_dict(self):
        return {"id": self.id, "name": self.name, "remaining": self.remaining,
                "total": self.total, "state": self.state}

    @classmethod
    def from_dict(cls, d):
        task = cls(int(d["id"]), int(d["total"]), d.get("name"))
        task.remaining = int(d.get("remaining", task.total))
        task.state = d.get("state", "paused")
        return task

    @staticmethod
    def parse_time(text):
        text = str(text).strip().replace(" ", "")
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2:
                m, s = int(parts[0]), int(parts[1])
            elif len(parts) == 3:
                h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                return h * 3600 + m * 60 + s
            else:
                raise ValueError("时间格式错误")
            return m * 60 + s
        return int(float(text))

    @staticmethod
    def format_time(sec):
        sec = max(0, int(sec))
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


class TimerManager:
    """管理所有 TimerTask 的集合。"""

    def __init__(self):
        self.tasks = []
        self._seq = 0

    def add(self, seconds, start=True, name=None):
        self._seq += 1
        task = TimerTask(self._seq, seconds, name)
        if start:
            task.start()
        self.tasks.append(task)
        return task

    def remove(self, _id):
        for i, t in enumerate(self.tasks):
            if t.id == _id:
                del self.tasks[i]
                return True
        return False

    def get(self, _id):
        for t in self.tasks:
            if t.id == _id:
                return t
        return None

    def rename(self, _id, name):
        t = self.get(_id)
        if t:
            t.name = name or t.name
            return True
        return False

    def pause_all(self):
        for t in self.tasks:
            t.pause()

    def tick_all(self):
        """全部滴答一秒，返回到点的任务列表。"""
        due = []
        for t in self.tasks:
            if t.tick():
                due.append(t)
        return due

    def to_json(self):
        return json.dumps([t.to_dict() for t in self.tasks], ensure_ascii=False)

    def save(self, path):
        data = [t.to_dict() for t in self.tasks]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        self.tasks = [TimerTask.from_dict(d) for d in data]
        self._seq = max([t.id for t in self.tasks], default=0)
        for t in self.tasks:
            if t.state == "done":
                t.state = "paused"
