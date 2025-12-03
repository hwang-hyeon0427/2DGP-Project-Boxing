from pico2d import *
import game_framework
import title_mode

image= None

FRAME_W = 279
FRAME_H = 245
ANIMATION_SPEED = 6.0

frame_index = 0

logo_start_time = 0

FRAME_SEQUENCE = []

for i in range(8):
    FRAME_SEQUENCE.append((i, 0))

for i in range(8):
    FRAME_SEQUENCE.append((i, 1))

for i in range(6):
    FRAME_SEQUENCE.append((i, 2))

TOTAL_FRAMES = len(FRAME_SEQUENCE)

def init():
    global image, logo_start_time, frame_index
    image = load_image('image/intro.png')
    frame_index = 0
    logo_start_time = get_time()

def finish():
    global image
    del image

def update():
    global frame_index
    frame_index += ANIMATION_SPEED * game_framework.frame_time

    if frame_index >= TOTAL_FRAMES:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    w, h = get_canvas_width(), get_canvas_height()

    idx = int(frame_index)
    frame_x, frame_row = FRAME_SEQUENCE[idx]

    src_x = frame_x * FRAME_W
    src_y = (2 - frame_row) * FRAME_H


    image.clip_draw(src_x, src_y, FRAME_W, FRAME_H, w // 2, h // 2, FRAME_W * 3, FRAME_H * 3)

    update_canvas()

def handle_events(): pass
def pause(): pass
def pause(): pass
def resume(): pass