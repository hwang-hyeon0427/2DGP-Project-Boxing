from pico2d import *
from button import SpriteSheetButton

import game_framework
import game_world
import mouse

buttons = []

def level_selected(level_no):
    print("LEVEL:", level_no)
    # 필요하면 play_mode로 이동
    # game_framework.change_mode(play_mode)

def init():
    global buttons
    game_world.clear()

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    buttons = [
        SpriteSheetButton(sheet, row=3, x=400, y=400, scale=6,
                          on_click=lambda: level_selected(1)),
        SpriteSheetButton(sheet, row=4, x=400, y=300, scale=6,
                          on_click=lambda: level_selected(2)),
        SpriteSheetButton(sheet, row=5, x=400, y=200, scale=6,
                          on_click=lambda: level_selected(3)),
    ]

def update():
    mx, my = mouse.get_pos()
    for b in buttons:
        b.update(mx, my)

def draw():
    clear_canvas()
    for b in buttons:
        b.draw()
    update_canvas()

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_MOUSEMOTION:
            mouse.update(e)
        elif e.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse.get_pos()
            for b in buttons:
                b.click(mx, my)

def finish(): pass
def pause(): pass
def resume(): pass
