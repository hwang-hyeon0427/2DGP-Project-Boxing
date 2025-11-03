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

# =============================================
# 플레이어1 (앞손: F, 뒷손: G, 어퍼: H, 가드: SPACE)
# =============================================

def f_down(e): # 앞손
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_f

def f_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_f

def g_down(e): # 뒷손
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_g

def g_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_g

def h_down(e): # 어퍼
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_h

def h_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_h

def space_down(e): # 가드
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def space_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_SPACE

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

# ===========================================================
# 플레이어2 (앞손: 콤마, 뒷손: 피리어드, 앞손 어펴: 슬래시)
# ===========================================================

def comma_down(e): # 앞손
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_COMMA

def comma_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_COMMA

def period_down(e): # 뒷손
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_PERIOD

def period_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_PERIOD

def slash_down(e): # 어퍼
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SLASH

def slash_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_SLASH

class FrontRightPunch:
    def __init__(self, boxer):
        self.b = boxer
        self.done = False

    def enter(self, e):
        # 설정에 키가 없으면 idle 사용
        if 'front_right_punch' in self.b.cfg:
            sheet = self.b.cfg['front_right_punch']
        else:
            sheet = self.b.cfg['idle']
        self.b.use_sheet(sheet)
        self.b.frame = 0
        self.done = False

    def exit(self, e):
        pass

    def do(self):
        if not self.done:
            self.b.frame += 1
            if self.b.frame >= self.b.cols:
                self.done = True
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        self.b.draw_current()

class BackLeftPunch:
    def __init__(self, boxer):
        self.b = boxer             # Boxer 인스턴스 참조
        self.done = False         # 애니메이션 완료여부

    def enter(self, e):
        # 상태에 집입할 때 실행되는 함수
        # e :  상태 전환의 원인이 된 이벤트

        # 'back_left_punch' 시트가 설정에 있으면 사용, 없으면 'idle' 시트 사용
        if 'back_left_punch' in self.b.cfg:
            sheet = self.b.cfg['back_left_punch']
        else:
            sheet = self.b.cfg['idle']
        self.b.use_sheet(sheet)             # 선택된 시트를 boxer 객체에 적용
        self.b.frame = 0                    # 프레임 인덱스 0으로 초기화
        self.done = False                   # 애니메이션 완료여부 초기화

    def exit(self, e):
        # 상태에서 빠져나갈 때 호출됨 (Exit action)
        # 현재는 특별한 정리 작업이 필요 없어서 pass 처리
        pass

    def do(self):
        # 상태에 머무르는 동안 매 프레임마다 반복 실행 (Do activity)
        if not self.done:
            # 1️⃣ 다음 프레임으로 이동
            self.b.frame += 1
            # 마지막 프레임까지 도달하면 애니메이션 종료
            if self.b.frame >= self.b.cols:
                self.done = True
                # 애니메이션 종료 이벤트를 상태 머신에 전달
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        # 현재 프레임을 실제로 화면에 그리는 함수
        # Boxer 클래스의 draw_current()는 현재 시트, 프레임, 방향(face)에 따라 이미지 클리핑을 수행함
        self.b.draw_current()

class FrontRightUppercut:
    def __init__(self, boxer):
        self.b = boxer
        self.done = False

    def enter(self, e):
        if 'front_right_uppercut' in self.b.cfg:
            sheet = self.b.cfg['front_right_uppercut']
        else:
            sheet = self.b.cfg['idle']
        self.b.use_sheet(sheet)
        self.b.frame = 0
        self.done = False

    def exit(self, e):
        pass

    def do(self):
        if not self.done:
            self.b.frame += 1
            if self.b.frame >= self.b.cols:
                self.done = True
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        self.b.draw_current()

class WalkBackward:
    def __init__(self, boxer):
        self.b = boxer

    def enter(self, e):
        sheet = self.b.cfg.get('walk_backward') or self.b.cfg.get('walk') or self.b.cfg.get('idle')
        self.b.use_sheet(sheet)
        if right_down(e):
            self.b.dir = 1
        elif left_down(e):
            self.b.dir = -1
        else:
            self.b.dir = -self.b.face

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
        if left_down(e):
            self.b.dir = -1
        elif right_down(e):
            self.b.dir = 1
        else:
            self.b.dir = self.b.face

    def exit(self, e):
        self.b.dir = 0

    def do(self):
        self.b.frame = (self.b.frame + 1) % self.b.cols
        self.b.x += self.b.dir * 5

    def draw(self):
        self.b.draw_current()

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['idle'])
        self.boxer.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = (self.boxer.frame + 1) % self.boxer.cols

    def draw(self):
        self.boxer.draw_current()

def animation_end(e):
    return e[0] == 'ANIMATION_END'

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
        self.image = None
        self.cols = 0
        self.frame_w = 0
        self.frame_h = 0
        self.scale = 1.0
        self.use_sheet(idle)

        self.frame = 0
        self.dir = 0

        self.IDLE = Idle(self)
        self.WALK_FORWARD = WalkForward(self)
        self.WALK_BACKWARD = WalkBackward(self)
        self.FRONT_RIGHT_PUNCH = FrontRightPunch(self)
        self.BACK_LEFT_PUNCH = BackLeftPunch(self)
        self.FRONT_RIGHT_UPPERCUT = FrontRightUppercut(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    # 플레이어 1 (A/D 키)
                    a_down: self.WALK_BACKWARD,
                    d_down: self.WALK_FORWARD,
                    # 플레이어 2 (←/→ 키)
                    left_down: self.WALK_FORWARD,
                    right_down: self.WALK_BACKWARD,
                    # 플레이어 2(콤마, 피리어드, 슬래시)
                    comma_down: self.FRONT_RIGHT_PUNCH,
                    period_down: self.BACK_LEFT_PUNCH,
                    slash_down: self.FRONT_RIGHT_UPPERCUT

                },
                self.WALK_BACKWARD: {a_up: self.IDLE, right_up: self.IDLE},
                self.WALK_FORWARD: {d_up: self.IDLE, left_up: self.IDLE},
                # 공격 상태에서 IDLE로 전환
                self.FRONT_RIGHT_PUNCH: {animation_end: self.IDLE},
                self.BACK_LEFT_PUNCH: {animation_end: self.IDLE},
                self.FRONT_RIGHT_UPPERCUT: {animation_end: self.IDLE}
            }
        )

    def use_sheet(self, sheet: dict):
        path = sheet['image']
        self.image = Boxer._img_cache.setdefault(path, load_image(path))
        self.cols = sheet['cols']
        self.frame_w, self.frame_h = sheet['w'], sheet['h']
        self.scale = sheet.get('scale', 1.0)

    def draw_current(self):
        if self.image is None:
            return
        src_x = self.frame * self.frame_w
        w, h = int(self.frame_w * self.scale), int(self.frame_h * self.scale)
        if self.face == 1:
            self.image.clip_draw(src_x, 0, self.frame_w, self.frame_h, self.x, self.y, w, h)
        else:
            self.image.clip_composite_draw(src_x, 0, self.frame_w, self.frame_h, 0, 'h', self.x, self.y, w, h)

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, e):
        if hasattr(e, 'type') and e.type in (SDL_KEYDOWN, SDL_KEYUP):
            # 플레이어 1: A/D 이동, F/G/H 공격
            if self.controls == 'wasd':
                if e.key not in (SDLK_a, SDLK_d):
                    return
            elif self.controls == 'arrows':
                # 플레이어 2: 방향키 이동,
                if e.key not in (SDLK_LEFT, SDLK_RIGHT, SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH):
                    return
        self.state_machine.handle_state_event(('INPUT', e))