from pico2d import *
import play_mode as start_mode
import game_framework
from ctypes import windll

# Windows에서 화면 해상도 가져옴 (DPI 보정 포함)
user32 = windll.user32
user32.SetProcessDPIAware()
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)


open_canvas(screen_w, screen_h)

game_framework.run(start_mode)
close_canvas()
