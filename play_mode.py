import lobby_mode
import game_framework
import game_world

from pico2d import *
from boxer import Boxer
from hp_ui import HpUi
from boxing_ring import BoxingRing
from button import Button, SpriteSheetButton
import mouse

import hitbox_edit

P1 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "wasd",
    "max_hp": 100,
    "bb": {"w": 0.40, "h": 0.55, "x_offset": 55, "y_offset": -30}, # 박스 크기 비율과 오프셋
    "idle":  {"image":"resource/player1/player1_Idle.png", "cols":10, "w":499, "h":489, "scale":0.9, "base_face": 1},
    "spawn": {"x": 300, "y": 300, "base_face": 1},
    "walk_backward": {"image":"resource/player1/player1_Walk_Backward.png", "cols": 10, "w": 499, "h": 489, "scale": 0.9},
    "walk_forward":  {"image":"resource/player1/player1_Walk_Forward.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "front_hand": {"image":"resource/player1/player1_FrontHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "uppercut": {"image":"resource/player1/player1_Uppercut.png",  "cols": 7, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "rear_hand": {"image":"resource/player1/player1_RearHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "blocking": {"image":"resource/player1/player1_Blocking.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "dizzy": {"image":"resource/player1/player1_Dizzy.png",  "cols": 8, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "ko": {"image":"resource/player1/player1_KO.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1}
}

P2 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "arrows",
    "max_hp": 100,
    "bb": {"w": 0.55, "h": 0.7, "x_offset": -35, "y_offset": -20},
    "idle":  {"image":"resource/player2/player2_Idle.png", "cols":10, "w":744, "h":711, "scale":0.5, "base_face": -1},
    "spawn": {"x": 700, "y": 300, "base_face": -1},
    "walk_backward": {"image":"resource/player2/player2_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.5},
    "walk_forward":  {"image":"resource/player2/player2_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.5, "base_face": -1},
    "front_hand": {"image":"resource/player2/player2_FrontHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "uppercut": {"image":"resource/player2/player2_Uppercut.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "rear_hand": {"image":"resource/player2/player2_RearHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "blocking": {"image":"resource/player2/player2_Block.png",  "cols": 10, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "dizzy": {"image":"resource/player2/player2_Dizzy.png",  "cols": 10, "w":744, "h":711, "scale":0.5, "base_face": -1},
    "ko": {"image":"resource/player2/player2_KO.png",  "cols": 8, "w":744, "h":711, "scale":0.5, "base_face": -1}
}

buttons = []
paused = False
pause_ui = []
sound_level = 0   # 0=None, 1=One, 3=Three


def resume_game():
    global paused, pause_ui
    print("RESUME GAME")
    paused = False
    pause_ui.clear()

def go_to_main_menu():
    print("MAIN MENU")
    game_framework.change_mode(lobby_mode)

def build_pause_menu():
    global pause_ui, screen_w, screen_h, buttons

    resume_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 7,
        x = screen_w//2, y = screen_h * 0.9,
        scale=6,
        on_click = resume_game
    )
    main_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 10,
        x = screen_w//2, y = screen_h * 0.7,
        scale=6,
        on_click = go_to_main_menu
    )
    back_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 1 ,
        x = screen_w//2, y = screen_h * 0.5,
        scale=6,
        on_click = resume_game
    )
    sound_none_btn = Button(
        "resource\Prinbles_YetAnotherIcons\png\White-Icon\Sound-None.png",
        x=get_canvas_width() // 2 - 100,
        y = screen_h * 0.75,
        scale=1.0,
        on_click=lambda: sound_none()
    )

    # Sound ONE 버튼
    sound_one_btn = Button(
        "resource\Prinbles_YetAnotherIcons\png\White-Icon\Sound-One.png",
        x=get_canvas_width() // 2,
        y = screen_h * 0.75,
        scale=1.0,
        on_click=lambda: sound_one()
    )

    # Sound THREE 버튼
    sound_three_btn = Button(
        "resource\Prinbles_YetAnotherIcons\png\White-Icon\Sound-Three.png",
        x=get_canvas_width() // 2 + 100,
        y = screen_h * 0.75,
        scale=1.0,
        on_click=lambda: sound_three()
    )

    pause_ui = [resume_btn, main_btn, back_btn, sound_none_btn, sound_one_btn, sound_three_btn]

def pause_game():
    global paused
    print("GAME PAUSED")
    paused = True
    build_pause_menu()

def sound_none():
    global sound_level
    sound_level = 0
    print("Sound: NONE")

def sound_one():
    global sound_level
    sound_level = 1
    print("Sound: ONE")

def sound_three():
    global sound_level
    sound_level = 3
    print("Sound: THREE")


def init():
    global p1, p2, hpui, boxing_ring, buttons, paused, pause_ui, screen_w, screen_h

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    paused = False

    boxing_ring = BoxingRing()
    game_world.add_object(boxing_ring, 0)

    p1 = Boxer(P1)
    game_world.add_object(p1, 1)
    p2 = Boxer(P2)
    game_world.add_object(p2, 1)

    p1.opponent = p2
    p2.opponent = p1

    hpui = HpUi(p1, p2, x = get_canvas_width()//2, y=600, scale=2.8)
    game_world.add_object(hpui, 2)

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    pause_btn = Button(
        "resource\Prinbles_YetAnotherIcons\png\White-Icon\Pause.png",
        x= get_canvas_width()//2, y=550,
        scale=1.0,
        on_click=lambda: pause_game()
    )

    buttons.append(pause_btn)

    game_world.add_collision_pair('body:block', p1, p2) # 서로의 몸통끼리 충돌

def update():
    mx, my = mouse.get_pos()

    if paused:
        for b in pause_ui:
            b.update(mx, my)
        return

    for b in buttons:
        b.update(mx, my)

    game_world.update()


    limit_boxer_in_boxing_ring(p1)
    limit_boxer_in_boxing_ring(p2)

    game_world.handle_collisions()
    hpui.update()

def finish():
    game_world.clear()

def draw():
    clear_canvas()
    game_world.render()

    if not paused:
        for b in buttons:
            b.draw()

    hpui.draw()

    if paused:
        for b in pause_ui:
            b.draw()

    if hitbox_edit.edit_mode:
        draw_rectangle(hitbox_edit.x1, hitbox_edit.y1, hitbox_edit.x2, hitbox_edit.y2)

    update_canvas()

def pause(): pass
def resume(): pass

def handle_events():
    global paused

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if paused:
                resume_game()
            else:
                game_framework.change_mode(lobby_mode)
            return
        if paused:
            if event.type == SDL_MOUSEMOTION:
                mouse.update(event)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mx, my = mouse.get_pos()
                for b in pause_ui:
                    b.click(mx, my)
            return
        if event.type == SDL_MOUSEMOTION:
            mouse.update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse.get_pos()
            for b in buttons:
                b.click(mx, my)


        if event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            hitbox_edit.edit_mode = not hitbox_edit.edit_mode
            print(f"Hitbox Edit Mode: {hitbox_edit.edit_mode}")
            return
        if hitbox_edit.edit_mode:
            if handle_hitbox_editor_event(event):
                return

        p1.handle_event(event)
        p2.handle_event(event)

def limit_boxer_in_boxing_ring(boxer):
    l, b, r, t = boxing_ring.get_bb()
    boxer.x = clamp(l + 40, boxer.x, r - 40)
    boxer.y = clamp(b + 40, boxer.y, t - 40)

def handle_hitbox_editor_event(event):
    canvas_h = get_canvas_height()

    if event.type == SDL_MOUSEBUTTONDOWN:
        hitbox_edit.dragging = True
        hitbox_edit.x1 = event.x
        hitbox_edit.y1 = canvas_h - event.y

        # 중요! 드래그 시작 시 x2,y2 초기화
        hitbox_edit.x2 = hitbox_edit.x1
        hitbox_edit.y2 = hitbox_edit.y1

        return True

    elif event.type == SDL_MOUSEMOTION and hitbox_edit.dragging:
        hitbox_edit.x2 = event.x
        hitbox_edit.y2 = canvas_h - event.y
        return True

    elif event.type == SDL_MOUSEBUTTONUP:
        hitbox_edit.dragging = False
        return True

    if event.type == SDL_KEYDOWN and (event.key == SDLK_RETURN or event.key == SDLK_s):
        save_hitbox_for_current_frame()
        return True

    return False

def save_hitbox_for_current_frame():
    boxer = p1  # 편집할 플레이어 선택 (p1/p2 스위치 가능)
    frame = int(boxer.frame)
    scale = boxer.scale

    # 드래그한 박스
    x1, y1 = hitbox_edit.x1, hitbox_edit.y1
    x2, y2 = hitbox_edit.x2, hitbox_edit.y2

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    # boxer 기준 상대 좌표
    ox = (cx - boxer.x) / scale
    oy = (cy - boxer.y) / scale
    w /= scale
    h /= scale

    print()
    print("==== HITBOX SAVED ====")
    print(f"{frame}: ({ox:.1f}, {oy:.1f}, {w:.1f}, {h:.1f})")
    print("=======================")
    print()
