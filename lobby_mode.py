import game_world
import play_mode
import game_world
import game_framework

from pico2d import *
from boxing_ring import BoxingRing
from button import Button

def start_game():
    game_framework.change_state(play_mode)

def how_to_play():
    pass

def exit_game():
    game_framework.quit()

def init(set_game=None):
    global bg, start_btn, how_btn, exit_btn, settings_btn

    game_world.clear()

    bg = BoxingRing()
    game_world.add_object(bg, 0)

    # start_btn = Button(400, 300, 250, 80,
    #                    'ui/start_normal.png',
    #                    'ui/start_hover.png',
    #                    on_click=start_game)

    settings_btn = Button(
        400, 300, 250, 80,
        'Button_Itch_Pack/settings/settings1.png',  # normal
        'Button_Itch_Pack/settings/settings_sheet.png',  # anim_sheet
        frame_count=5,  # 시트에 포함된 프레임 수
        fps=20,  # 원하는 애니메이션 속도
        on_click = set_game
    )

    # how_btn = Button(400, 200, 250, 80,
    #                  'ui/how_normal.png',
    #                  'ui/how_hover.png',
    #                  on_click=how_to_play)

    # exit_btn = Button(400, 100, 250, 80,
    #                   'ui/exit_normal.png',
    #                   'ui/exit_hover.png',
    #                   on_click=exit_game)

    # game_world.add_object(start_btn, 1)
    # game_world.add_object(how_btn, 1)
    # game_world.add_object(exit_btn, 1)
    game_world.add_object(settings_btn, 1)


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            exit_game()

        # 버튼 이벤트 전달
        for obj in game_world.world[1]:
            obj.handle_event(e)

        if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            exit_game()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass