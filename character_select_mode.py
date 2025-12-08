from pico2d import *
import game_framework
import game_world

import play_mode
from boxing_ring import BoxingRing
from button import Button
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos

select_mode = 'cpu'

selected_level = None

# 2P 모드용 단계
stage = 1             # 1 = P1 선택, 2 = P2 선택
p1_choice = None      # 'P1' or 'P2'
p2_choice = None      # 'P1' or 'P2'

buttons = []
background = None

def init():
    global background, buttons, stage, p1_choice, p2_choice

    print(f"[CHAR SELECT] init() | mode = {select_mode}")

    game_world.clear()

    # 상태 초기화
    stage = 1
    p1_choice = None
    p2_choice = None

    # 배경 생성
    background = BoxingRing()
    game_world.add_object(background, 0)

    buttons = [
        Button(
            image_path="resource/player1/player1_Idle.png",
            x=300,
            y=300,
            scale=0.4,
            on_click=lambda: character_selected("P1")
        ),
        Button(
            image_path="resource/player2/player2_Idle.png",
            x=500,
            y=300,
            scale=0.4,
            on_click=lambda: character_selected("P2")
        )
    ]


def character_selected(ch):
    global stage, p1_choice, p2_choice, selected_level

    print(f"[CHAR SELECT] clicked:", ch)

    if select_mode == 'cpu':
        # 사용자가 ch 선택
        player_choice = ch

        # CPU는 남은 캐릭터 선택
        cpu_choice = 'P2' if player_choice == 'P1' else 'P1'

        print(f"[CPU MODE] Player = {player_choice}, CPU = {cpu_choice}")

        # play_mode 설정 전달
        play_mode.cpu_mode = True
        play_mode.cpu_level = selected_level
        play_mode.cpu_player = cpu_choice      # CPU가 조종할 캐릭터
        play_mode.p1_character = player_choice # 유저가 조종할 캐릭터
        play_mode.p2_character = cpu_choice    # CPU 캐릭터

        # play_mode로 진입
        game_framework.change_mode(play_mode)
        return

    if select_mode == 'two_player':

        # stage 1 → P1 선택
        if stage == 1:
            p1_choice = ch
            stage = 2
            print(f"[2P MODE] P1 selected: {p1_choice}")
            return

        # stage 2 → P2 선택
        elif stage == 2:
            if ch == p1_choice:
                print("[2P MODE] P2는 이미 고른 캐릭터를 선택할 수 없음")
                return

            p2_choice = ch
            print(f"[2P MODE] P2 selected: {p2_choice}")

            # play_mode로 전달
            play_mode.cpu_mode = False
            play_mode.p1_character = p1_choice
            play_mode.p2_character = p2_choice

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
    font = load_font("Consolas.ttf", 24)
    font.draw(x - len(text) * 5, y, text, (255, 255, 255))

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
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
