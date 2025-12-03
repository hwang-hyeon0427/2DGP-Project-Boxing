import title_mode
import game_framework
import game_world

from pico2d import *
from boxer import Boxer
from hp_ui import HpUi
from boxing_ring import BoxingRing

import hitbox_edit

P1 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "wasd",
    "max_hp": 100,
    "bb": {"w": 0.40, "h": 0.55, "x_offset": 55, "y_offset": -30}, # 박스 크기 비율과 오프셋
    "idle":  {"image":"player1/player1_Idle.png", "cols":10, "w":499, "h":489, "scale":0.9, "base_face": 1},
    "spawn": {"x": 300, "y": 300, "base_face": 1},
    "walk_backward": {"image":"player1/player1_Walk_Backward.png", "cols": 10, "w": 499, "h": 489, "scale": 0.9},
    "walk_forward":  {"image":"player1/player1_Walk_Forward.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "front_hand": {"image":"player1/player1_FrontHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "uppercut": {"image":"player1/player1_Uppercut.png",  "cols": 7, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "rear_hand": {"image":"player1/player1_RearHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "blocking": {"image":"player1/player1_Blocking.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "dizzy": {"image":"player1/player1_Dizzy.png",  "cols": 8, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "ko": {"image":"player1/player1_KO.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1}
}

P2 = {
    "face_map": {"left": 1, "right": -1},
    "controls": "arrows",
    "max_hp": 100,
    "bb": {"w": 0.55, "h": 0.7, "x_offset": -35, "y_offset": -20},
    "idle":  {"image":"player2/player2_Idle.png", "cols":10, "w":744, "h":711, "scale":0.5, "base_face": -1},
    "spawn": {"x": 700, "y": 300, "base_face": -1},
    "walk_backward": {"image":"player2/player2_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.5},
    "walk_forward":  {"image":"player2/player2_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.5, "base_face": -1},
    "front_hand": {"image":"player2/player2_FrontHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "uppercut": {"image":"player2/player2_Uppercut.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "rear_hand": {"image":"player2/player2_RearHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "blocking": {"image":"player2/player2_Block.png",  "cols": 10, "w":744, "h":713, "scale":0.5, "base_face": -1},
    "dizzy": {"image":"player2/player2_Dizzy.png",  "cols": 10, "w":744, "h":711, "scale":0.5, "base_face": -1},
    "ko": {"image":"player2/player2_KO.png",  "cols": 8, "w":744, "h":711, "scale":0.5, "base_face": -1}
}

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            hitbox_edit.edit_mode = not hitbox_edit.edit_mode
            print(f"Hitbox Edit Mode: {hitbox_edit.edit_mode}")
            return
        if hitbox_edit.edit_mode:
            if handle_hitbox_editor_event(event):
                return

        p1.handle_event(event)
        p2.handle_event(event)


def init():
    global p1, p2, hpui, boxing_ring

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

    game_world.add_collision_pair('body:block', p1, p2) # 서로의 몸통끼리 충돌
    game_world.add_collision_pair('atk:hit', None, p2)
    game_world.add_collision_pair('atk:hit', None, p1)


def update():
    game_world.update()

    limit_boxer_in_boxing_ring(p1)
    limit_boxer_in_boxing_ring(p2)

    game_world.handle_collisions()

def finish():
    game_world.clear()

def draw():
    clear_canvas()
    game_world.render()

    if hitbox_edit.edit_mode:
        draw_rectangle(hitbox_edit.x1, hitbox_edit.y1, hitbox_edit.x2, hitbox_edit.y2)

    update_canvas()

def pause(): pass
def resume(): pass

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
