# -*- coding: utf-8 -*-
"""全局配置：API、主题、常用时长、多语言。"""

import os
import sys

API_HOST = "127.0.0.1"
API_PORT = 8765

APP_NAME = "MultiTimer"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

PRESETS = [(60, "preset_1m"), (300, "preset_5m"), (600, "preset_10m"),
           (1500, "preset_25m"), (1800, "preset_30m"), (3600, "preset_60m")]

# 状态文件与日志目录：打包 exe 旁 / 源码目录
_STATE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if getattr(sys, "frozen", False):
    _STATE_DIR = os.path.dirname(sys.executable)
STATE_FILE = os.path.join(_STATE_DIR, "multi_timer_state.json")
LOG_FILE = os.path.join(_STATE_DIR, "multi_timer_api.log")

# ---------- 多语言 ----------
LANG = "zh"  # "zh" / "en"，启动时由语言选择框决定


def tr(key):
    """按当前语言取文案。"""
    return TEXTS.get(key, {}).get(LANG, key)


TEXTS = {
    # 窗口/通用
    "title": {"zh": "多倒计时", "en": "MultiTimer"},
    "time_hint": {"zh": "时长 分:秒", "en": "Duration min:sec"},
    "add": {"zh": "添加", "en": "Add"},
    "pause_all": {"zh": "全部暂停", "en": "Pause All"},
    "start": {"zh": "开始", "en": "Start"},
    "pause": {"zh": "暂停", "en": "Pause"},
    "resume": {"zh": "继续", "en": "Resume"},
    "done": {"zh": "完成", "en": "Done"},
    "restart": {"zh": "重开", "en": "Restart"},
    "delete": {"zh": "删除", "en": "Delete"},
    "timer_default": {"zh": "计时器", "en": "Timer"},
    # 预设
    "preset_1m": {"zh": "1分", "en": "1m"},
    "preset_5m": {"zh": "5分", "en": "5m"},
    "preset_10m": {"zh": "10分", "en": "10m"},
    "preset_25m": {"zh": "25分", "en": "25m"},
    "preset_30m": {"zh": "30分", "en": "30m"},
    "preset_60m": {"zh": "60分", "en": "60m"},
    # 输入/警告
    "bad_format_title": {"zh": "格式错误", "en": "Invalid Format"},
    "bad_format_msg": {"zh": "请输入秒数或 分:秒（如 25:00 或 1:30:00）",
                       "en": "Enter seconds or min:sec (e.g. 25:00 or 1:30:00)"},
    # 通知
    "toast_done": {"zh": "倒计时已结束", "en": "Countdown Finished"},
    # 托盘
    "tray_show": {"zh": "显示窗口", "en": "Show Window"},
    "tray_autostart": {"zh": "开机自启", "en": "Auto Start on Boot"},
    "tray_quit": {"zh": "退出", "en": "Quit"},
    # 单实例
    "already_running": {"zh": "程序已在运行中", "en": "The app is already running"},
    # 语言选择
    "choose_lang": {"zh": "选择语言", "en": "Choose Language"},
    "lang_zh": {"zh": "中文", "en": "Chinese"},
    "lang_en": {"zh": "English", "en": "English"},
}

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

WINDOW_SIZE = "560x640"
WINDOW_MIN = (460, 420)

FONT_TITLE = ("Microsoft YaHei UI", 13, "bold")
FONT_BTN = ("Microsoft YaHei UI", 9, "bold")
FONT_LABEL = ("Microsoft YaHei UI", 9)
FONT_TIME = ("Consolas", 22, "bold")
FONT_ENTRY = ("Consolas", 13, "bold")
