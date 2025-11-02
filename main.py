from pico2d import *
from boxer import Boxer

P1 = {
    "controls": "wasd",
    "idle":  {"image":"player2/player2_Idle.png", "cols":10, "w":499, "h":489, "scale":0.5},
    "spawn": {"x": 100, "y": 300, "face": 1},
    "walk_backward": {"image":"player2/player2_Walk_Backward.png", "cols":10, "w": 499, "h":489, "scale":0.5},
    "walk_forward":  {"image":"player2/player2_Walk_Forward.png",  "cols":10, "w": 499, "h":489, "scale":0.5}

}

P2 = {
    "controls": "arrows",
    "idle":  {"image":"player1/player1_Idle.png", "cols":10, "w":744, "h":711, "scale":0.3},
    "spawn": {"x": 700, "y": 300, "face": 1},
    "walk_backward": {"image":"player1/player1_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.3},
    "walk_forward":  {"image":"player1/player1_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.3},
    "FrontRightPunch": {"image":"player1/player1_FrontRightPunch.png",  "cols": 8, "w":180, "h":561, "scale":0.3},
    "FrontRightUppercut": {"image":"player1/player1_FrontRightUppercut.png",  "cols": 8, "w":180, "h":561, "scale":0.3},
    "FrontLeftPunch": {"image":"player1/player1_FrontLeftPunch.png",  "cols": 8, "w":180, "h":561, "scale":0.3}
}

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            p1.handle_event(event)
            p2.handle_event(event)

def reset_world():
    global world
    global p1, p2

    world = []

    p1 = Boxer(P1)
    p2 = Boxer(P2)

    world.append(p1)
    world.append(p2)

def update_world():
    for o in world:
        o.update()
    pass

def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()

running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()


