from pico2d import *
from state_machine import StateMachine
from sdl2 import *

# ===================
# player1 (A / D 키)
# ===================

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a

def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d

def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d

# ===================
# player2 (← / → 키)
# ===================

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

class WalkBackward:
    def __init__(self, boxer):
        self.b = boxer

    def enter(self, e):
        sheet = self.b.cfg.get('walk_backward') or self.b.cfg.get('walk') or self.b.cfg.get('idle')
        self.b.use_sheet(sheet)
        self.b.dir = -1 if self.b.face == 1 else 1

    def exit(self, e):
        self.b.dir = 0

    def do(self):
        self.b.frame = (self.b.frame + 1) % self.b.cols
        self.b.x += self.b.dir * 5

    def draw(self):
        self.b.draw_current()

class WalkForward:
    def __init__(self, boxer):
        self.b = boxer

    def enter(self, e):
        sheet = self.b.cfg.get('walk_forward') or self.b.cfg.get('walk') or self.b.cfg.get('idle')
        self.b.use_sheet(sheet)
        self.b.dir = 1 if self.b.face == 1 else -1

    def exit(self, e):
        self.b.dir = 0


class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = (self.boxer.frame + 1) % self.boxer.cols

    def draw(self):
        b = self.boxer
        fw, fh = b.frame_w, b.frame_h

        src_left = b.frame * fw
        src_bottom = (b.idle_row * fh
                      if not b.from_top
                      else (b.rows - 1 - b.idle_row) * fh)

        draw_w = int(fw * b.scale)
        draw_h = int(fh * b.scale)

        if b.face == 1:
            b.image.clip_draw(src_left, src_bottom, fw, fh, b.x, b.y, draw_w, draw_h)
        else:
            b.image.clip_composite_draw(src_left, src_bottom, fw, fh, 0, 'h', b.x, b.y, draw_w, draw_h)

class Boxer:
    _img_cache = {}

    def __init__(self, cfg: dict):
        self.cfg = cfg

        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face = spawn.get('face', 1)

        self.controls = cfg.get('controls', 'both')

        idle = cfg['idle']

        img_path = idle['image']
        if img_path not in Boxer._img_cache:
            Boxer._img_cache[img_path] = load_image(img_path)
        self.image = Boxer._img_cache[img_path]

        self.cols = int(idle['cols'])
        self.rows = int(idle.get('rows', 1))

        self.sheet_w = int(self.image.w)
        self.sheet_h = int(self.image.h)

        self.frame_w = self.sheet_w // self.cols
        self.frame_h = self.sheet_h // self.rows

        self.from_top = bool(idle.get('from_top', False))

        self.idle_row = int(idle.get('row', 0))
        if self.idle_row < 0:
            self.idle_row = 0
        if self.idle_row > self.rows - 1:
            self.idle_row = self.rows - 1

        self.scale = float(idle.get('scale', 1.0))

        self.frame = 0
        self.dir = 0

        self.IDLE = Idle(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    # 상태 전이 규칙 추가 예정
                }
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, e):
        self.state_machine.handle_state_event(('INPUT', e))