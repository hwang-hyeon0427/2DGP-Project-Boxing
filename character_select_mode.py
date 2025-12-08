import game_framework
import game_world
import play_mode
import lobby_mode
from pico2d import *
from boxing_ring import BoxingRing
from button import Button
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos

select_mode = 'cpu'

selected_level = None
buttons = []
background = None
font = None

def init():
    global background, buttons, stage, p1_choice, p2_choice, font
    global screen_w, screen_h

    font = load_font('ENCR10B.TTF', 30)
    print("[CHARACTER SELECT] init")

    game_world.clear()

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    # 상태 초기화
    stage = 1
    p1_choice = None
    p2_choice = None

    # 배경 생성
    background = BoxingRing()
    game_world.add_object(background, 0)

    buttons = [
        Button(
            image_path="resource/player1/player1_button.png",
            x= screen_w / 2 - 400,
            y=300,
            scale= 1.0,
            on_click=lambda: character_selected("P1")
        ),
        Button(
            image_path="resource/player2/player2_button.png",
            x= screen_w / 2 + 400,
            y=300,
            scale= 0.6,
            on_click=lambda: character_selected("P2")
        )
    ]

def character_selected(ch):
    global stage, p1_choice, p2_choice, selected_level

    print(f"[CHAR SELECT] clicked:", ch)

    if select_mode == 'cpu':
        player_choice = ch
        cpu_choice = 'P2' if player_choice == 'P1' else 'P1'

        print(f"[CPU MODE] Player = {player_choice}, CPU = {cpu_choice}")

        # play_mode 에 캐릭터 종류 전달
        play_mode.cpu_mode = True
        play_mode.cpu_level = selected_level
        # p1 = 내가 플레이할 캐릭터
        # p2 = CPU가 플레이할 캐릭터
        play_mode.p1_character = player_choice
        play_mode.p2_character = cpu_choice

        game_framework.change_mode(play_mode)
        return

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

    # 안내 텍스트
    if select_mode == 'cpu':
        draw_text_centered("Choose Your Character", 400, 500)
    else:
        if stage == 1:
            draw_text_centered("P1 - Choose Your Character", 400, 500)
        else:
            draw_text_centered("P2 - Choose Your Character", 400, 500)

    update_canvas()

def draw_text_centered(text, x, y):
    font.draw(screen_w / 2 - 200, screen_h / 3, text, (255, 255, 255))

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.change_mode(lobby_mode)
        elif e.type == SDL_MOUSEMOTION:
            mouse_update(e)
        elif e.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)
def finish(): pass
def pause(): pass
def resume(): pass
