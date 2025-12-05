from pico2d import *

_mouse_x, _mouse_y = 0, 0

def update(e):
    global _mouse_x, _mouse_y
    _mouse_x = e.x
    _mouse_y = get_canvas_height() - e.y   # 좌표 반전

def get_pos():
    return _mouse_x, _mouse_y
