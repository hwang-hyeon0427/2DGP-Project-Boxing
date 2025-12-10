import os
import sys

# 2) SDL2 DLL 경로 강제 설정 (PyInstaller onefile 대응)
if hasattr(sys, "_MEIPASS"):
    # onefile 실행 시, PyInstaller가 모든 리소스를 풀어놓는 임시 폴더
    os.environ["PYSDL2_DLL_PATH"] = sys._MEIPASS
else:
    # 개발 환경에서 실행할 때는 현재 작업 폴더를 사용
    os.environ["PYSDL2_DLL_PATH"] = os.getcwd()

# 3) 이제서야 pico2d import (★ 반드시 이 위치에서!)
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
