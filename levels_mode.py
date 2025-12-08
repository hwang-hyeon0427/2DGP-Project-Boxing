from pico2d import *
from button import SpriteSheetButton
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos
from boxing_ring import BoxingRing

import game_framework
import game_world
import character_select_mode

selected_level = None
buttons = []


def init():
    global background, buttons, selected_level
    game_world.clear()

    background = BoxingRing()
    game_world.add_object(background, 0)

    selected_level = None

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    buttons = [
        SpriteSheetButton(sheet, row=2, x=400, y=400, scale=6,
                          on_click=lambda: level_selected(1)), # Level easy
        SpriteSheetButton(sheet, row=5, x=400, y=300, scale=6,
                          on_click=lambda: level_selected(2)), # Level medium
        SpriteSheetButton(sheet, row=3, x=400, y=200, scale=6,
                          on_click=lambda: level_selected(3)), # Level hard
    ]

def level_selected(level_no):
    global selected_level
    selected_level = level_no
    print("LEVEL SELECTED:", selected_level)
    character_select_mode.selected_level = level_no
    game_framework.change_mode(character_select_mode)

def update():
    mx, my = mouse_get_pos()
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
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_MOUSEMOTION:
            mouse_update(e)
        elif e.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)

def finish(): pass
def pause(): pass
def resume(): pass
