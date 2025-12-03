from pico2d import *

from key_events import *
from state_machine import StateMachine

from hitbox_data import HITBOX_DATA
from hitbox import HitBox
import game_world
import game_framework
from idle import Idle
from attack_state import AttackState
# from walk_backward import WalkBackward
from walk import Walk
def event_stop(e):
    return e[0] == 'STOP'

def event_walk(e):
    return e[0] == 'WALK'
# boxer 속도 단위 환산
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
WALK_SPEED_KMPH = 20.0  # Km / Hour
WALK_SPEED_MPM = (WALK_SPEED_KMPH * 1000.0 / 60.0)
WALK_SPEED_MPS = (WALK_SPEED_MPM / 60.0)
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER)

# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Boxer:
    _img_cache = {}

    FRAMES_PER_ACTION = FRAMES_PER_ACTION
    ACTION_PER_TIME = ACTION_PER_TIME

    def __init__(self, cfg: dict):
        self.base_face = None
        self.cfg = cfg


        self.hits = 0
        self.max_hp = int(cfg.get('max_hp', 100))  # 값 복사
        self.hp = self.max_hp  # hp는 무조건 새로 생성
        self.opponent = None

        self.hit_cool = 0.3
        self.last_hit_time = 0.0

        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face_dir = spawn.get('face', 1)
        self.xdir, self.ydir = 0, 0

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
        self.WALK = Walk(self)
        # self.WALK_BACKWARD = WalkBackward(self)
        self.FRONT_HAND = AttackState(self, 'front_hand')
        self.REAR_HAND = AttackState(self, 'rear_hand')
        self.UPPERCUT = AttackState(self, 'uppercut')

        # 상태머신 이벤트 테이블 분리
        self.transitions_wasd = {
            self.IDLE: {
                event_walk: self.WALK,
                a_down: self.WALK,
                d_down: self.WALK,
                w_down: self.WALK,
                s_down: self.WALK,

                f_down: self.FRONT_HAND,
                g_down: self.REAR_HAND,
                h_down: self.UPPERCUT
            },

            self.WALK: {
                event_stop: self.IDLE,

                f_down: self.FRONT_HAND,
                g_down: self.REAR_HAND,
                h_down: self.UPPERCUT
            },

            self.FRONT_HAND: {event_stop: self.IDLE, event_walk: self.WALK},
            self.REAR_HAND: {event_stop: self.IDLE, event_walk: self.WALK},
            self.UPPERCUT: {event_stop: self.IDLE, event_walk: self.WALK},
        }

        self.transitions_arrows = {
            self.IDLE: {
                event_walk: self.WALK,
                left_down: self.WALK,
                right_down: self.WALK,
                up_down: self.WALK,
                down_down: self.WALK,

                comma_down: self.FRONT_HAND,
                period_down: self.REAR_HAND,
                slash_down: self.UPPERCUT
            },

            self.WALK: {
                event_stop: self.IDLE,

                comma_down: self.FRONT_HAND,
                period_down: self.REAR_HAND,
                slash_down: self.UPPERCUT
            },

            self.FRONT_HAND: {event_stop: self.IDLE, event_walk: self.WALK},
            self.REAR_HAND: {event_stop: self.IDLE, event_walk: self.WALK},
            self.UPPERCUT: {event_stop: self.IDLE, event_walk: self.WALK},
        }

        # controls에 따라 상태머신 선택
        if self.controls == 'wasd':
            transitions = self.transitions_wasd
        else:
            transitions = self.transitions_arrows

        self.state_machine = StateMachine(self.IDLE, transitions)

    def use_sheet(self, sheet: dict):
        path = sheet['image']
        self.image = Boxer._img_cache.setdefault(path, load_image(path))

        self.cols = sheet['cols']
        self.frame_w = sheet['w']
        self.frame_h = sheet['h']

        self.scale = sheet.get('scale', 1.0)
        
        self.base_face = sheet.get('face', 1)

    def draw_current(self):
        if not self.image:
            return

        # 1) frame index
        frame = int(self.frame) % self.cols

        # 2) 정확한 src 좌표 (프레임 시트는 가로 1줄)
        src_x = frame * self.frame_w
        src_y = 0
        src_w = self.frame_w
        src_h = self.frame_h

        # 3) 출력 크기 (확대/축소)
        draw_w = int(self.frame_w * self.scale)
        draw_h = int(self.frame_h * self.scale)

        # 4) 좌우 방향 반영
        if self.face_dir == self.base_face:
            self.image.clip_draw(src_x, src_y, src_w, src_h,
                                 self.x, self.y,
                                 draw_w, draw_h)
        else:
            self.image.clip_composite_draw(src_x, src_y, src_w, src_h,
                                           0, 'h',
                                           self.x, self.y,
                                           draw_w, draw_h)

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):

        if event.type == SDL_KEYDOWN:
            face_map = self.cfg.get("face_map", {"left": -1, "right": 1})
            if self.controls == 'wasd':
                if event.key == SDLK_a:
                    self.face_dir = face_map["left"]
                elif event.key == SDLK_d:
                    self.face_dir = face_map["right"]

            else:  # arrows
                if event.key == SDLK_LEFT:
                    self.face_dir = face_map["left"]
                elif event.key == SDLK_RIGHT:
                    self.face_dir = face_map["right"]

        # 키보드 입력(KEYDOWN/KEYUP) 처리
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):

            # 1. controls에 따라 이동키 세트 분리
            if self.controls == 'wasd':
                move_keys = {SDLK_a, SDLK_d, SDLK_w, SDLK_s}
            else:
                move_keys = {SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN}

            # 2. 이동키 처리
            if event.key in move_keys:

                cur_xdir, cur_ydir = self.xdir, self.ydir

                # KEYDOWN
                if event.type == SDL_KEYDOWN:
                    if self.controls == 'wasd':
                        if event.key == SDLK_a: self.xdir -= 1
                        elif event.key == SDLK_d: self.xdir += 1
                        elif event.key == SDLK_w: self.ydir += 1
                        elif event.key == SDLK_s: self.ydir -= 1
                    else:
                        if event.key == SDLK_LEFT: self.xdir -= 1
                        elif event.key == SDLK_RIGHT: self.xdir += 1
                        elif event.key == SDLK_UP: self.ydir += 1
                        elif event.key == SDLK_DOWN: self.ydir -= 1

                # KEYUP
                elif event.type == SDL_KEYUP:
                    if self.controls == 'wasd':
                        if event.key == SDLK_a: self.xdir += 1
                        elif event.key == SDLK_d: self.xdir -= 1
                        elif event.key == SDLK_w: self.ydir -= 1
                        elif event.key == SDLK_s: self.ydir += 1
                    else:
                        if event.key == SDLK_LEFT: self.xdir += 1
                        elif event.key == SDLK_RIGHT: self.xdir -= 1
                        elif event.key == SDLK_UP: self.ydir -= 1
                        elif event.key == SDLK_DOWN: self.ydir += 1

                if cur_xdir != self.xdir or cur_ydir != self.ydir:  # 방향키에 따른 변화가 있으면
                    if self.xdir == 0 and self.ydir == 0:  # 멈춤
                        self.state_machine.handle_state_event(('STOP', self.face_dir))  # 스탑 시 이전 방향 전달
                    else:  # 움직임
                        self.state_machine.handle_state_event(('WALK', None))

        # 그 외의 이벤트는 상태머신에 직접 전달
        self.state_machine.handle_state_event(('INPUT', event))

    def get_bb(self):
        bb_cfg = self.cfg["bb"]

        # 1) 한 프레임 이미지의 실제 픽셀 크기 (화면 기준)
        frame_w = self.frame_w * self.scale
        frame_h = self.frame_h * self.scale

        # 2) 비율 기반 실제 박스 크기
        bb_w = frame_w * bb_cfg["w"]
        bb_h = frame_h * bb_cfg["h"]

        # 3) 오프셋 (스케일 + 좌우 반전 모두 반영)
        #    - x_offset, y_offset 은 "원본 스프라이트 기준" 거리라고 가정
        x_offset = bb_cfg["x_offset"] * self.scale
        y_offset = bb_cfg["y_offset"] * self.scale

        # draw_current() 와 동일한 기준:
        # base_face 방향으로 그릴 땐 flip 없음, 다를 땐 좌우 반전.
        flipped = (self.face_dir != self.base_face)
        if flipped:
            x_offset = -x_offset  # 이미지가 좌우 반전되면 오프셋도 같이 반전

        # 4) 박스 중심 좌표
        cx = self.x + x_offset
        cy = self.y + y_offset

        left = cx - bb_w / 2
        right = cx + bb_w / 2
        bottom = cy - bb_h / 2
        top = cy + bb_h / 2

        return left, bottom, right, top

    def spawn_hitbox(self):
        attack_type = self.current_attack_type
        if attack_type is None:
            return

        frame_offsets = HITBOX_DATA[self.controls][attack_type]

        hitbox = HitBox(
            owner=self,
            frame_offsets=frame_offsets,
            duration=0.15  # 또는 원하는 지속시간
        )

        game_world.add_object(hitbox, 1)
        game_world.add_collision_pair('atk:hit', hitbox, self.opponent)

    def handle_collision(self, group, other):
        now = get_time()

        if group == 'body:block' and other is self.opponent: # 몸통끼리 충돌
            l1, b1, r1, t1 = self.get_bb() # 자신의 바운딩 박스
            l2, b2, r2, t2 = other.get_bb() # 상대방의 바운딩 박스

            # 겹친 정도(overlap)를 계산
            overlap = min(r1 - l2, r2 - l1)

            if overlap > 0:
                # 자기 기준으로 반씩 밀기
                push_amount = overlap / 2

                # 자신의 얼굴 방향 기준이 아니라 두 플레이어의 위치 관계로 밀기
                if self.x < other.x:
                    self.x -= push_amount
                    other.x += push_amount
                else:
                    self.x += push_amount
                    other.x -= push_amount

            return

        if now - self.last_hit_time < self.hit_cool:
            return

        if group == 'atk:hit' and other is self.opponent:
            shared_hp = max(self.hp, self.opponent.hp)
            shared_hp -= 5
            self.hp = shared_hp
            self.opponent.hp = shared_hp
            self.last_hit_time = now
