from pico2d import *
import game_framework
import title_mode

image = None

frame = 0.0
FRAME_COUNT = 3

FRAME_W = 826 //3
FRAME_H = 272

ANIMATTION_SPEED = 10.0
logo_start_time = 0

def init():
    global image, logo_start_time, frame
    image = load_image('image/SUPER-PUNCH-OUT_logo.png')
    frame = 0.0
    logo_start_time = get_time()


def finish():
    global image
    del image

def update():
    global frame
    frame += ANIMATTION_SPEED * game_framework.frame_time
    frame %= FRAME_COUNT

    if get_time() - logo_start_time > 2.0:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    current_frame = int(frame)
    src_x = current_frame * FRAME_W # 현재 프레임에 해당하는 이미지의 x 좌표
    scale = 3

    w, h = get_canvas_width(), get_canvas_height() # 캔버스 크기 가져오기
    image.clip_draw(src_x, 0, FRAME_W, FRAME_H, w // 2, h // 2, FRAME_W * scale, FRAME_H * scale)  # clip_draw (src_x, src_y, src_w, src_h, x, y)

    update_canvas()

def handle_events():
    event_list = get_events() # 버퍼로부터 모든 입력을 갖고 온다.
    # no nothing

def pause():
    pass

def resume():
    pass