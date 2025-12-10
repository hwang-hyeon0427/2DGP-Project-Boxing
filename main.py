from pico2d import *
from ctypes import windll

import logo_mode as start_mode
import game_framework
import sound_manager


# Windows에서 화면 해상도 가져옴 (DPI 보정 포함)
user32 = windll.user32
user32.SetProcessDPIAware()
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)


open_canvas(screen_w, screen_h)

sound_manager.load()

game_framework.run(start_mode)
close_canvas()
