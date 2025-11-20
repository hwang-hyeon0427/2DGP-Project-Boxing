from pico2d import *
from boxer import Boxer
import game_framework
import game_world
from hpbar import HPBar
from map import Map

P1 = {
    "controls": "wasd",
    "bb": {"w": 0.25, "h": 0.35, "x_offset": -40, "y_offset": 0},
    "idle":  {"image":"player1/player1_Idle.png", "cols":10, "w":499, "h":489, "scale":0.5},
    "spawn": {"x": 100, "y": 300, "face": 1},
    "walk_backward": {"image":"player1/player1_Walk_Backward.png", "cols": 10, "w": 499, "h": 489, "scale": 0.5},
    "walk_forward":  {"image":"player1/player1_Walk_Forward.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.5},
    "front_hand": {"image":"player1/player1_FrontHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.5},
    "uppercut": {"image":"player1/player1_Uppercut.png",  "cols": 7, "w": 499, "h": 489, "scale": 0.5},
    "rear_hand": {"image":"player1/player1_RearHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 0.5},
    "blocking": {"image":"player1/player1_Blocking.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.5},
    "dizzy": {"image":"player1/player1_Dizzy.png",  "cols": 8, "w": 499, "h": 489, "scale": 0.5},
    "ko": {"image":"player1/player1_KO.png",  "cols": 10, "w": 499, "h": 489, "scale": 0.5}
}

P2 = {
    "controls": "arrows",
    "bb": {"w": 0.30, "h": 0.40, "x_offset": -70, "y_offset": 0},
    "idle":  {"image":"player2/player2_Idle.png", "cols":10, "w":744, "h":711, "scale":0.3},
    "spawn": {"x": 700, "y": 300, "face": 1},
    "walk_backward": {"image":"player2/player2_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.3},
    "walk_forward":  {"image":"player2/player2_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.3},
    "front_hand": {"image":"player2/player2_FrontHand.png",  "cols": 8, "w":744, "h":713, "scale":0.3},
    "uppercut": {"image":"player2/player2_Uppercut.png",  "cols": 8, "w":744, "h":713, "scale":0.3},
    "rear_hand": {"image":"player2/player2_RearHand.png",  "cols": 8, "w":744, "h":713, "scale":0.3},
    "blocking": {"image":"player2/player2_Block.png",  "cols": 10, "w":744, "h":713, "scale":0.3},
    "dizzy": {"image":"player2/player2_Dizzy.png",  "cols": 10, "w":744, "h":711, "scale":0.3},
    "ko": {"image":"player2/player2_KO.png",  "cols": 8, "w":744, "h":711, "scale":0.3}
}

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            p1.handle_event(event)
            p2.handle_event(event)

def init():
    global p1, p2, map

    map = Map()
    game_world.add_object(map, 0)

    p1 = Boxer(P1)
    game_world.add_object(p1, 1)

    p2 = Boxer(P2)
    game_world.add_object(p2, 1)

    hp_bar1 = HPBar(p1, 200, 550)
    game_world.add_object(hp_bar1,2)

    hp_bar2 = HPBar(p2, 600, 550)
    game_world.add_object(hp_bar2,2)


    game_world.add_collision_pair('boxer:boxer', p1, p2)

def update():
    game_world.update()

    limit_boxer_in_map(p1)
    limit_boxer_in_map(p2)

    game_world.handle_collisions()

def finish():
    game_world.clear()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause(): pass
def resume(): pass

def limit_boxer_in_map(boxer):
    l, b, r, t = map.get_bb()
    boxer.x = clamp(l + 40, boxer.x, r - 40)
    boxer.y = clamp(b + 40, boxer.y, t - 40)