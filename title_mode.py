from pico2d import *
import game_framework
import play_mode

image = None
w, h = 0, 0

def init():
    global image, w, h
    image = load_image('title_screen.png')
    w, h = image.w, image.h

def finish():
    global image
    del image

def update():
    pass

def draw():
    clear_canvas()
    scale = 3.5  # 0 ~ 1 사이의 값으로 조절
    image.draw(317*4//2, 128*6//2, w * scale, h * scale)
    update_canvas()

def handle_events():
    event_list = get_events() # 버퍼로부터 모든 입력을 갖고 온다.
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)

def pause():
    pass

def resume():
    pass