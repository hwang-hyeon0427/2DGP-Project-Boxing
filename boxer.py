from pico2d import *

from key_events import a_down, a_up, d_down, d_up, left_down, left_up, right_down, right_up, comma_down, period_down, \
    slash_down, f_down, g_down, h_down
from state_machine import StateMachine

from hitbox import HitBox
import game_world
from idle import Idle
from attack_state import AttackState
from walk_backward import WalkBackward
from walk_forward import WalkForward


def animation_end(e):
    return e[0] == 'ANIMATION_END'

class Boxer:
    _img_cache = {}

    def __init__(self, cfg: dict):
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
        self.FRONT_HAND = AttackState(self, 'front_hand')
        self.REAR_HAND = AttackState(self, 'rear_hand')
        self.UPPERCUT = AttackState(self, 'uppercut')

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    # 플레이어 1 (A/D 키)
                    a_down: self.WALK_BACKWARD,
                    d_down: self.WALK_FORWARD,
                    # 플레이어 1 (F/G/H 키)
                    f_down: self.FRONT_HAND,
                    g_down: self.REAR_HAND,
                    h_down: self.UPPERCUT,
                    # 플레이어 2 (←/→ 키)
                    left_down: self.WALK_FORWARD,
                    right_down: self.WALK_BACKWARD,
                    # 플레이어 2(콤마, 피리어드, 슬래시)
                    comma_down: self.FRONT_HAND,
                    period_down: self.REAR_HAND,
                    slash_down: self.UPPERCUT

                },
                self.WALK_BACKWARD: {a_up: self.IDLE, right_up: self.IDLE},
                self.WALK_FORWARD: {d_up: self.IDLE, left_up: self.IDLE},
                # 공격 상태에서 IDLE로 전환
                self.FRONT_HAND: {animation_end: self.IDLE},
                self.REAR_HAND: {animation_end: self.IDLE},
                self.UPPERCUT: {animation_end: self.IDLE}
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
        self.last_x, self.last_y = self.x, self.y
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, e):
        if hasattr(e, 'type') and e.type in (SDL_KEYDOWN, SDL_KEYUP):
            # 플레이어 1: A/D 이동, F/G/H 공격
            if self.controls == 'wasd':
                if e.key not in (SDLK_a, SDLK_d, SDLK_f, SDLK_g, SDLK_h):
                    return
            elif self.controls == 'arrows':
                # 플레이어 2: 방향키 이동,
                if e.key not in (SDLK_LEFT, SDLK_RIGHT, SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH):
                    return
        self.state_machine.handle_state_event(('INPUT', e))

    def get_bb(self):
        bb_cfg = self.cfg["bb"]

        # 한 프레임 이미지의 실제 픽셀 크기
        frame_w = self.frame_w * self.scale # 화면에 실제로 그려지는 프레임의 너비 = 원본 프레임 너비 * 확대/축소 비율
        frame_h = self.frame_h * self.scale # 화면에 실제로 그려지는 프레임의 높이 = 원본 프레임 높이 * 확대/축소 비율

        # 비율 기반 실제 박스 크기
        bb_w = frame_w * bb_cfg["w"] # 충돌 박스의 실제 너비 = 실제 프레임 너비 * 박스 너비 비율(0~1 사이)
        bb_h = frame_h * bb_cfg["h"]

        # 오프셋
        x_offset = bb_cfg["x_offset"] # 캐릭터의 중심(self.x)에서 충돌 박스를 좌우로 얼마나 이동시킬지 결정
        y_offset = bb_cfg["y_offset"]

        left = self.x - bb_w / 2 + x_offset
        right = self.x + bb_w / 2 + x_offset
        bottom = self.y - bb_h / 2 + y_offset
        top = self.y + bb_h / 2 + y_offset

        return left, bottom, right, top

    def spawn_hitbox(self):
        # 오른쪽 / 왼쪽 방향에 따라 공격 거리 변경
        x_offset = 80 if self.face == 1 else -80

        # 공격을 위한 히트박스 생성
        hitbox = HitBox(
            self,  # owner → 이 히트박스를 만든 캐릭터(Boxer 인스턴스)
            0, 0,  # 기본 오프셋 offset_x, offset_y (지금은 프레임별 히트박스를 사용하므로 0으로 둬도 됨)
            0, 0,  # 기본 히트박스 크기 w, h (이 역시 프레임별 값이 적용되므로 0으로 둬도 됨)
            0.15,  # duration → 히트박스가 존재할 시간(초). 0.15초 후 자동 삭제됨.

            # 🔥 frame_offsets: 특정 프레임에서 히트박스가 어떻게 생겨야 하는지를 정의하는 딕셔너리
            # key = 공격 애니메이션 프레임 번호(self.frame)
            # value = (offset_x, offset_y, width, height)
            frame_offsets={
                2: (80, 20, 70, 40)
                # → 공격 애니메이션의 2번 프레임에서
                #    owner.x + 80, owner.y + 20 위치에
                #    가로 70, 세로 40 크기의 히트박스를 생성하라는 의미
            }
        )

        # 게임월드 등록
        game_world.add_object(hitbox, 1)

        # 상대방과 충돌 그룹 생성
        game_world.add_collision_pair('atk:hit', hitbox, self.opponent)

    def handle_collision(self, group, other):
        now = get_time()

        if group == 'body:block' and other is self.opponent:
            l1, b1, r1, t1 = self.get_bb()
            l2, b2, r2, t2 = other.get_bb()

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
