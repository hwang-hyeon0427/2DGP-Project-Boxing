from pico2d import *
import game_framework
import title_mode

image = None
logo_stop_time = 0

def init():
    global image, logo_stop_time
    image = load_image('tuk_credit.png')
    logo_stop_time = get_time()


def finish():
    global image
    del image

def update():
    if get_time() - logo_stop_time > 2.0:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()

def handle_events():
    event_list = get_events() # 버퍼로부터 모든 입력을 갖고 온다.
    # no nothing

def pause():
    pass

def resume():
    pass