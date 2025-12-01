from pico2d import *

from key_events import *
from state_machine import StateMachine

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

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    # 플레이어 1 (A/D 키)
                     a_down: self.WALK,
                    d_down: self.WALK,
                    # 플레이어 1 (F/G/H 키)
                    f_down: self.FRONT_HAND,
                    g_down: self.REAR_HAND,
                    h_down: self.UPPERCUT,
                    # 플레이어 2 (←/→ 키)
                    left_down: self.WALK,
                    right_down: self.WALK,
                    # 플레이어 2(콤마, 피리어드, 슬래시)
                    comma_down: self.FRONT_HAND,
                    period_down: self.REAR_HAND,
                    slash_down: self.UPPERCUT

                },
                # self.WALK_BACKWARD: {a_up: self.IDLE, right_up: self.IDLE,
                #                      f_down: self.FRONT_HAND,
                #                      g_down: self.REAR_HAND,
                #                      h_down: self.UPPERCUT,
                #                      comma_down: self.FRONT_HAND,
                #                      period_down: self.REAR_HAND,
                #                      slash_down: self.UPPERCUT
                #                      },
                self.WALK: {d_up: self.IDLE, left_up: self.IDLE,
                                    f_down: self.FRONT_HAND,
                                    g_down: self.REAR_HAND,
                                    h_down: self.UPPERCUT,
                                    comma_down: self.FRONT_HAND,
                                    period_down: self.REAR_HAND,
                                    slash_down: self.UPPERCUT
                                    },
                # 공격 상태에서 IDLE로 전환
                self.FRONT_HAND: {event_stop: self.IDLE,
                                  a_down: self.WALK,
                                  d_down: self.WALK,
                                  left_down: self.WALK,
                                  right_down: self.WALK
                                  },
                self.REAR_HAND: {event_stop: self.IDLE,
                                 a_down: self.WALK,
                                 d_down: self.WALK,
                                 left_down: self.WALK,
                                 right_down: self.WALK
                                 },
                self.UPPERCUT: {event_stop: self.IDLE,
                                a_down: self.WALK,
                                d_down: self.WALK,
                                left_down: self.WALK,
                                right_down: self.WALK
                                }
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

        # ⚠ frame이 float이므로 반드시 정수로 변환
        frame_index = int(self.frame)

        src_x = frame_index * self.frame_w
        w, h = int(self.frame_w * self.scale), int(self.frame_h * self.scale)

        if self.face_dir == 1:
            self.image.clip_draw(src_x, 0, self.frame_w, self.frame_h, self.x, self.y, w, h)
        else:
            self.image.clip_composite_draw(src_x, 0, self.frame_w, self.frame_h, 0, 'h',
                                           self.x, self.y, w, h)

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN, SDLK_a, SDLK_d, SDLK_w, SDLK_s):
            cur_xdir, cur_ydir = self.xdir, self.ydir
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_LEFT: self.xdir -= 1
                elif event.key == SDLK_RIGHT: self.xdir += 1
                elif event.key == SDLK_UP: self.ydir -= 1
                elif event.key == SDLK_DOWN: self.ydir += 1
                elif event.key == SDLK_a: self.xdir -= 1
                elif event.key == SDLK_d: self.xdir += 1
                elif event.key == SDLK_w: self.ydir -= 1
                elif event.key == SDLK_s: self.ydir += 1

            elif event.type == SDL_KEYUP:
                if event.key == SDLK_LEFT: self.xdir += 1
                elif event.key == SDLK_RIGHT: self.xdir -= 1
                elif event.key == SDLK_UP: self.ydir += 1
                elif event.key == SDLK_DOWN: self.ydir -= 1
                elif event.key == SDLK_a: self.xdir += 1
                elif event.key == SDLK_d: self.xdir -= 1
                elif event.key == SDLK_w: self.ydir += 1
                elif event.key == SDLK_s: self.ydir -= 1

            if cur_xdir != self.xdir or cur_ydir != self.ydir: # 방향키에 따른 변화가 있으면
                if self.xdir == 0 and self.ydir:  # 멈춤
                    self.state_machine.handle_state_event(('STOP', self.face_dir))  # 스탑 시 이전 방향 전달
                else:  # 움직임
                    self.state_machine.handle_state_event(('WALK', None))
        else:
            self.state_machine.handle_state_event(('INPUT', event))

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
        attack_type = self.current_attack_type
        if attack_type is None:
            return

        # 🔥 캐릭터별 히트박스 데이터
        HITBOX_DATA = {
            'wasd': {  # P1용
                'front_hand': {
                    3: (85, 12, 65, 38)
                },
                'rear_hand': {
                    3: (92, 15, 70, 42)
                },
                'uppercut': {
                    4: (150, 80, 55, 85)
                }
            },
            'arrows': {  # P2용
                'front_hand': {
                    2: (60, 15, 60, 35)
                },
                'rear_hand': {
                    3: (70, 20, 65, 40)
                },
                'uppercut': {
                    4: (35, 65, 45, 75)
                }
            }
        }

        # 내 캐릭터가 어떤 그룹(P1/P2)에 속하는지 결정
        char_key = self.controls   # 'wasd' 또는 'arrows'

        # 내 캐릭터에 대한 히트박스 데이터가 없으면 종료
        if char_key not in HITBOX_DATA:
            return

        char_data = HITBOX_DATA[char_key] # 공격 타입별 데이터

        # 현재 공격 타입에 대한 데이터가 없으면 종료
        if attack_type not in char_data:
            return

        raw_offsets = char_data[attack_type]  # {frame: (ox, oy, w, h)}

        # 좌우 방향(face)에 따라 x 오프셋 반전
        frame_offsets = {}
        for frame, (ox, oy, w, h) in raw_offsets.items():
            if self.face == 1:      # 오른쪽 바라보는 경우
                frame_offsets[frame] = (ox, oy, w, h)
            else:                   # 왼쪽 바라보는 경우 → x 반전
                frame_offsets[frame] = (-ox, oy, w, h)

        # 실제 히트박스 생성
        hitbox = HitBox(
            self,      # owner
            0, 0,      # 기본 오프셋(프레임별 히트박스가 우선 적용됨)
            0, 0,      # 기본 크기(프레임별 히트박스가 적용됨)
            1.0,      # 히트박스 지속시간
            frame_offsets=frame_offsets
        )

        # 게임 월드 등록 + 충돌 그룹 등록
        game_world.add_object(hitbox, 1)
        game_world.add_collision_pair('atk:hit', hitbox, self.opponent) # 히트박스 vs 상대방

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
