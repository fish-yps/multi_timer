# -*- coding: utf-8 -*-
"""全局配置：API、主题、常用时长。"""

import os
import sys

API_HOST = "127.0.0.1"
API_PORT = 8765

APP_NAME = "MultiTimer"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

PRESETS = [(60, "1分"), (300, "5分"), (600, "10分"),
           (1500, "25分"), (1800, "30分"), (3600, "60分")]

# 状态文件与日志目录：打包 exe 旁 / 源码目录
_STATE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if getattr(sys, "frozen", False):
    _STATE_DIR = os.path.dirname(sys.executable)
STATE_FILE = os.path.join(_STATE_DIR, "multi_timer_state.json")
LOG_FILE = os.path.join(_STATE_DIR, "multi_timer_api.log")

# 墨绿玻璃主题
GREEN = "#156847"
GREEN_BRIGHT = "#1d8a5f"
GREEN_DARK = "#0c2c1e"
GREEN_BORDER = "#2b7a55"
BG_GLASS = "#08120c"
FG = "#d8efe2"
FG_MUTED = "#8fb8a3"
WARN = "#f9e2af"
SURFACE = "#0f2419"
SURFACE_LIGHT = "#143320"
BTN_DELETE_BG = "#4a5568"
BTN_DELETE_FG = "#e2e8f0"
BTN_PAUSE_BG = "#c9a227"
BTN_PAUSE_FG = "#1e1e2e"

WINDOW_TITLE = "多倒计时"
WINDOW_SIZE = "560x640"
WINDOW_MIN = (460, 420)

FONT_TITLE = ("Microsoft YaHei UI", 13, "bold")
FONT_BTN = ("Microsoft YaHei UI", 9, "bold")
FONT_LABEL = ("Microsoft YaHei UI", 9)
FONT_TIME = ("Consolas", 22, "bold")
FONT_ENTRY = ("Consolas", 13, "bold")
