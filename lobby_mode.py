from pico2d import *
import game_framework
import game_world
import play_mode

from button import SpriteSheetButton
from boxing_ring import BoxingRing   # ← 최적화된 배경 클래스
import mouse


background = None
buttons = []

def levels():
    print("LEVELS")
    game_framework.change_mode(lobby_mode)

def start_game():
    print("START GAME")
    game_framework.change_mode(play_mode)

def init():
    global background, buttons

    game_world.clear()

    # -----------------------------
    # 애니메이션 배경 BoxingRing
    # -----------------------------
    background = BoxingRing()
    game_world.add_object(background, 0)   # depth 0에 배경 추가

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    start_btn = SpriteSheetButton(
        sheet_path = sheet,
        row = 9,            # START 버튼 row
        x = 400, y = 300,
        scale = 8,
        on_click=start_game
    )

    # back_btn = SpriteSheetButton(
    #     sheet_path=sheet,
    #     row=1,            # BACK 버튼 row
    #     x=400, y=200,
    #     scale=4,
    #     on_click= game_framework.quit
    # )

    buttons = [start_btn]


def finish(): pass
def pause(): pass
def resume(): pass

def update():
    mx, my = mouse.get_pos()

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
            mouse.update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse.get_pos()
            for b in buttons:
                b.click(mx, my)