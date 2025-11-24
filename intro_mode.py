from pico2d import *
import game_framework
import title_mode

image= None

frame = 0.0
FRAME_COUNT = 8
FRAME_ROWS = 3
TARGET_ROWS = 1

ANIMATION_SPEED = 10.0

FRAME_W = 2237 // FRAME_COUNT
FRAME_H = 737 // FRAME_ROWS

logo_start_time = 0


def init():
    global image, logo_start_time, frame
    image = load_image('image/intro.png')
    frame = 0.0
    logo_start_time = get_time()

def finish():
    global image
    del image

def update():
    global frame
    frame += ANIMATION_SPEED * game_framework.frame_time

    if frame >= FRAME_COUNT:
        game_framework.chage_mode(title_mode)

def draw():
    pass

def handle_events(): pass
def pause(): pass
def pause(): pass
def resume(): pass