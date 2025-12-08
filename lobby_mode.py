from pico2d import *
import game_framework
import game_world
import play_mode
import levels_mode

from button import *
from boxing_ring import BoxingRing   # ← 최적화된 배경 클래스
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos



background = None
buttons = []

def init():
    global background, buttons
    global screen_w, screen_h

    game_world.clear()

    background = BoxingRing()
    game_world.add_object(background, 0)   # depth 0에 배경 추가

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    start_btn = SpriteSheetButton(
        sheet_path = sheet,
        row = 9,            # START 버튼 row
        x = 400, y = 300,
        scale = 8,
        on_click=lambda: game_framework.change_mode(levels_mode)
    )
    two_player_btn = SpriteSheetButton(
        sheet_path=sheet,
        row=0,  # 2 PLAYER 버튼 row
        x=400, y=100,
        scale=8,
        on_click=lambda: game_framework.change_mode(play_mode)
    )

    music_on_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Music-On.png",
        x=screen_w - 170,
        y=screen_h * 0.1,
        scale=1.0,
        on_click=music_on
    )
    music_off_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Music-Off.png",
        x=screen_w - 100,
        y=screen_h * 0.1,
        scale=1.0,
        on_click=music_off
    )

    buttons = [start_btn, two_player_btn,
               music_on_btn, music_off_btn
               ]

def music_on():
    sound_manager.play_bgm("hip-hop_music")
    print("BGM ON")

def music_off():
    sound_manager.stop_bgm("hip-hop_music")
    print("BGM OFF")

def finish(): pass
def pause(): pass
def resume(): pass

def update():
    mx, my = mouse_get_pos()

    for b in buttons:
        b.update(mx, my)

    game_world.update()

def draw():
    clear_canvas()
    game_world.render()

    for b in buttons:
        b.draw()

    update_canvas()

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)