from pico2d import *

import title_mode
from boxer import Boxer
import game_framework
import game_world
from hpbar import HPBar
from boxing_ring import BoxingRing
from hitbox import HitBox

P1 = {
    "controls": "wasd",
    "max_hp": 100,
    "bb": {"w": 0.40, "h": 0.55, "x_offset": 55, "y_offset": -30}, # 박스 크기 비율과 오프셋
    "idle":  {"image":"player1/player1_Idle.png", "cols":10, "w":499, "h":489, "scale":0.9},
    "spawn": {"x": 300, "y": 300, "face": 1},
    "walk_backward": {"image":"player1/player1_Walk_Backward.png", "cols": 10, "w": 499, "h": 489, "scale": 0.9},
    "walk_forward":  {"image":"player1/player1_Walk_Forward.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9, "base_face": 1},
    "front_hand": {"image":"player1/player1_FrontHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9},
    "uppercut": {"image":"player1/player1_Uppercut.png",  "cols": 7, "w": 499, "h": 489, "scale": 0.9},
    "rear_hand": {"image":"player1/player1_RearHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.9},
    "blocking": {"image":"player1/player1_Blocking.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9},
    "dizzy": {"image":"player1/player1_Dizzy.png",  "cols": 8, "w": 499, "h": 489, "scale": 0.9},
    "ko": {"image":"player1/player1_KO.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.9}
}

P2 = {
    "controls": "arrows",
    "max_hp": 100,
    "bb": {"w": 0.55, "h": 0.7, "x_offset": -35, "y_offset": -20},
    "idle":  {"image":"player2/player2_Idle.png", "cols":10, "w":744, "h":711, "scale":0.5},
    "spawn": {"x": 700, "y": 300, "face": 1},
    "walk_backward": {"image":"player2/player2_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.5},
    "walk_forward":  {"image":"player2/player2_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.5, "base_face": -1},
    "front_hand": {"image":"player2/player2_FrontHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5},
    "uppercut": {"image":"player2/player2_Uppercut.png",  "cols": 8, "w":744, "h":713, "scale":0.5},
    "rear_hand": {"image":"player2/player2_RearHand.png",  "cols": 8, "w":744, "h":713, "scale":0.5},
    "blocking": {"image":"player2/player2_Block.png",  "cols": 10, "w":744, "h":713, "scale":0.5},
    "dizzy": {"image":"player2/player2_Dizzy.png",  "cols": 10, "w":744, "h":711, "scale":0.5},
    "ko": {"image":"player2/player2_KO.png",  "cols": 8, "w":744, "h":711, "scale":0.5}
}

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            p1.handle_event(event)
            p2.handle_event(event)

def init():
    global p1, p2, hp1, hp2, boxing_ring

    boxing_ring = BoxingRing()
    game_world.add_object(boxing_ring, 0)

    p1 = Boxer(P1)
    game_world.add_object(p1, 1)

    p2 = Boxer(P2)
    game_world.add_object(p2, 1)

    p1.opponent = p2
    p2.opponent = p1

    hp1 = HPBar(p1, x=300, y=550)
    game_world.add_object(hp1, 2)

    hp2 = HPBar(p2, x=1000, y=550)
    game_world.add_object(hp2, 2)

    game_world.add_collision_pair('body:block', p1, p2) # 서로의 몸통끼리 충돌


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
    update_canvas()

def pause(): pass
def resume(): pass

def limit_boxer_in_boxing_ring(boxer):
    l, b, r, t = boxing_ring.get_bb()
    boxer.x = clamp(l + 40, boxer.x, r - 40)
    boxer.y = clamp(b + 40, boxer.y, t - 40)