from pico2d import *
import game_framework
import title_mode

image = None
logo_stop_time = 0
w, h = 0, 0

def init():
    global image, logo_stop_time, w, h
    image = load_image('tuk_credit.png')
    logo_stop_time = get_time()
    w, h = image.w, image.h


def finish():
    global image
    del image

def update():
    if get_time() - logo_stop_time > 2.0:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    scale = 1.5
    image.draw(317*4//2, 128*6//2, w * scale, h * scale)
    update_canvas()

def handle_events():
    event_list = get_events() # 버퍼로부터 모든 입력을 갖고 온다.
    # no nothing

def pause():
    pass

def resume():
    pass