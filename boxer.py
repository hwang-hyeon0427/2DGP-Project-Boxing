from pico2d import *
from key_events import *
from state_machine import StateMachine
from hitbox_data import HITBOX_DATA
from hitbox import HitBox
from attack_state import AttackState
# from walk_backward import WalkBackward

import game_framework
import game_world

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
    # 공격 종류별 넉백 세기(픽셀)
    KNOCKBACK_POWER = {
        'front_hand': 20,  # 잽
        'rear_hand': 35,  # 스트레이트
        'uppercut': 50  # 어퍼컷
    }

    def __init__(self, cfg: dict):
        self.current_attack_type = None
        self.base_face = None
        self.cfg = cfg

        # 넉백 상태 변수
        self.pushback_velocity_x = 0
        self.pushback_velocity_y = 0
        self.pushback_time = 0
        self.pushback_duration = 0

        # 중력 계수
        self.pushback_gravity = -600  # 튕김 후 아래로 떨어지는 힘

        self.hits = 0
        self.max_hp = cfg["max_hp"]  # 값 복사
        self.hp = self.max_hp  # hp는 무조건 새로 생성
        self.opponent = None

        self.hit_cool = 0.3
        self.last_hit_time = 0.0

        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face_dir = spawn.get('base_face', 1)
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
        self.HURT = Hurt(self)
        self.DIZZY = Dizzy(self)
        self.KO = Ko(self)

        # 상태머신 이벤트 테이블 분리
        self.transitions_wasd = {
            self.IDLE: {
                event_walk: self.WALK,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

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

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                f_down: self.FRONT_HAND,
                g_down: self.REAR_HAND,
                h_down: self.UPPERCUT
            },
            self.FRONT_HAND: {event_stop: self.IDLE, event_walk: self.WALK,
                              event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.REAR_HAND: {event_stop: self.IDLE, event_walk: self.WALK,
                             event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.UPPERCUT: {event_stop: self.IDLE, event_walk: self.WALK,
                            event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.HURT: {event_hurt_done: self.IDLE, event_ko: self.KO},
            self.DIZZY: {event_dizzy_done: self.IDLE, event_ko: self.KO},
            self.KO: {}
        }

        self.transitions_arrows = {
            self.IDLE: {
                event_walk: self.WALK,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

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

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                comma_down: self.FRONT_HAND,
                period_down: self.REAR_HAND,
                slash_down: self.UPPERCUT
            },

            self.FRONT_HAND: {event_stop: self.IDLE, event_walk: self.WALK,
                              event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.REAR_HAND: {event_stop: self.IDLE, event_walk: self.WALK,
                             event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.UPPERCUT: {event_stop: self.IDLE, event_walk: self.WALK,
                            event_hurt: self.HURT, event_dizzy: self.DIZZY, event_ko: self.KO},
            self.HURT: {event_hurt_done: self.IDLE,event_ko: self.KO},
            self.DIZZY: {event_dizzy_done: self.IDLE,event_ko: self.KO},
            self.KO: {}
        }

        # controls에 따라 상태머신 선택
        if self.controls == 'wasd':
            transitions = self.transitions_wasd
        else:
            transitions = self.transitions_arrows

        self.state_machine = StateMachine(self.IDLE, transitions)

    def adjust_knockback_based_on_distance(self, attacker, base_knockback):
        distance = abs(self.x - attacker.x)

        min_dist = 40
        max_dist = 160

        if distance < min_dist:
            scale = 0.4
        elif distance > max_dist:
            scale = 1.0
        else:
            scale = (distance - min_dist) / (max_dist - min_dist)
            scale = max(0.4, scale)

        return base_knockback * scale

    def start_pushback(self, attacker, amount=40, duration=0.18):
        # 1) 기본 방향 = 공격자의 바라보는 방향
        dir_x = attacker.face_dir

        # 2) y 성분은 좌표 차이의 10% 정도만 사용 (벨트스크롤 전형)
        dy = self.y - attacker.y
        dir_y = dy * 0.1

        # 3) 정규화
        length = max((dir_x * dir_x + dir_y * dir_y) ** 0.5, 0.001)
        nx = dir_x / length
        ny = dir_y / length

        # 4) 넉백 속도 설정
        self.pushback_velocity_x = nx * (amount / duration)
        self.pushback_velocity_y = ny * (amount / duration) + 70

        # 5) 중력
        self.pushback_gravity = -1200

        # 6) 시간이동
        self.pushback_time = duration
        self.pushback_duration = duration

    def use_sheet(self, sheet: dict):
        path = sheet['image']
        self.image = Boxer._img_cache.setdefault(path, load_image(path))

        self.cols = sheet['cols']
        self.frame_w = sheet['w']
        self.frame_h = sheet['h']

        self.scale = sheet.get('scale', 1.0)
        
        self.base_face = sheet.get('base_face', 1)

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

        # ============================
        # Final Fight 스타일 넉백 물리
        # ============================
        if self.pushback_time > 0:
            dt = game_framework.frame_time

            # -------- X축 이동 --------
            new_x = self.x + self.pushback_velocity_x * dt

            LEFT_WALL = 50
            RIGHT_WALL = 750

            # 벽 충돌 → 넉백 종료
            if new_x < LEFT_WALL:
                new_x = LEFT_WALL
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                self.pushback_velocity_y = 0

            elif new_x > RIGHT_WALL:
                new_x = RIGHT_WALL
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                self.pushback_velocity_y = 0

            self.x = new_x

            # -------- Y축 작은 튕김 + 중력 --------
            self.pushback_velocity_y += self.pushback_gravity * dt
            self.y += self.pushback_velocity_y * dt

            FLOOR_Y = 90

            if self.y < FLOOR_Y:
                self.y = FLOOR_Y
                self.pushback_velocity_y = 0

            # -------- 넉백 시간 감소 --------
            self.pushback_time -= dt
            if self.pushback_time <= 0:
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                self.pushback_velocity_y = 0

        # ============================
        # 상태머신 업데이트
        # ============================
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        if self.pushback_time > 0:
            return

        if isinstance(self.state_machine.cur_state, Ko):
            return

        if isinstance(self.state_machine.cur_state, Dizzy):
            return

        if event.type == SDL_KEYDOWN:
            face_map = self.cfg.get("face_map", {"left": -1, "right": 1})
            if self.controls == 'wasd':
                if event.key == SDLK_a:
                    self.face_dir = face_map["left"]
                elif event.key == SDLK_d:
                    self.face_dir = face_map["right"]
            else:
                if event.key == SDLK_LEFT:
                    self.face_dir = face_map["left"]
                elif event.key == SDLK_RIGHT:
                    self.face_dir = face_map["right"]

        if event.type in (SDL_KEYDOWN, SDL_KEYUP):

            if self.controls == 'wasd':
                move_keys = {SDLK_a, SDLK_d, SDLK_w, SDLK_s}
            else:
                move_keys = {SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN}

            if event.key in move_keys:

                cur_xdir, cur_ydir = self.xdir, self.ydir

                if event.type == SDL_KEYDOWN:
                    if self.controls == 'wasd':
                        if event.key == SDLK_a:
                            self.xdir -= 1
                        elif event.key == SDLK_d:
                            self.xdir += 1
                        elif event.key == SDLK_w:
                            self.ydir += 1
                        elif event.key == SDLK_s:
                            self.ydir -= 1
                    else:
                        if event.key == SDLK_LEFT:
                            self.xdir -= 1
                        elif event.key == SDLK_RIGHT:
                            self.xdir += 1
                        elif event.key == SDLK_UP:
                            self.ydir += 1
                        elif event.key == SDLK_DOWN:
                            self.ydir -= 1

                elif event.type == SDL_KEYUP:
                    if self.controls == 'wasd':
                        if event.key == SDLK_a:
                            self.xdir += 1
                        elif event.key == SDLK_d:
                            self.xdir -= 1
                        elif event.key == SDLK_w:
                            self.ydir -= 1
                        elif event.key == SDLK_s:
                            self.ydir += 1
                    else:
                        if event.key == SDLK_LEFT:
                            self.xdir += 1
                        elif event.key == SDLK_RIGHT:
                            self.xdir -= 1
                        elif event.key == SDLK_UP:
                            self.ydir -= 1
                        elif event.key == SDLK_DOWN:
                            self.ydir += 1

                if cur_xdir != self.xdir or cur_ydir != self.ydir:
                    if self.xdir == 0 and self.ydir == 0:
                        self.state_machine.handle_state_event(('STOP', self.face_dir))
                    else:
                        self.state_machine.handle_state_event(('WALK', None))

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

        if self.controls == "wasd":  # P1
            game_world.add_collision_pair('P1_attack:P2', hitbox, self.opponent)
        else:  # P2
            game_world.add_collision_pair('P2_attack:P1', hitbox, self.opponent)

    def handle_collision(self, group, other):
        now = get_time()

        # KO 상태 충돌 무시
        if isinstance(self.state_machine.cur_state, Ko):
            return

        # 넉백 중 모든 충돌 무시 (body:block 포함)
        if self.pushback_time > 0:
            return

        # 피격 직후 무적 시간
        if now - self.last_hit_time < self.hit_cool:
            return

        if self.pushback_time > 0:
            return

        if group == 'body:block' and other is self.opponent:
            l1, b1, r1, t1 = self.get_bb()
            l2, b2, r2, t2 = other.get_bb()

            overlap = min(r1 - l2, r2 - l1)

            if overlap > 0:
                push = overlap / 2
                if self.x < other.x:
                    self.x -= push
                    other.x += push
                else:
                    self.x += push
                    other.x -= push
            return

        if group == 'P1_attack:P2':
            # 공격자 Boxer
            attacker = other.owner

            old_hp = self.hp
            self.hp = max(0, self.hp - 10)

            self.last_hit_time = now

            # KO
            if self.hp <= 0:
                self.state_machine.handle_state_event(('KO', None))
                return

            # Dizzy
            if self.hp <= self.max_hp * 0.3:
                self.state_machine.handle_state_event(('DIZZY', None))
                return

            # ----------------------------------------
            # Final Fight 벡터 기반 넉백
            # ----------------------------------------
            attack_type = attacker.current_attack_type
            base_knockback = Boxer.KNOCKBACK_POWER.get(attack_type, 20)

            # 거리 기반 넉백 보정
            knockback = self.adjust_knockback_based_on_distance(attacker, base_knockback)

            # 넉백 시작 (벡터 기반)
            self.start_pushback(attacker=attacker, amount=knockback, duration=0.18)

            # Hurt 상태 진입
            self.state_machine.handle_state_event(('HURT', None))

            if old_hp != self.hp:
                print("P2 HP:", self.hp)



        elif group == 'P2_attack:P1':
            # 공격자 Boxer
            attacker = other.owner

            old_hp = self.hp
            self.hp = max(0, self.hp - 10)

            self.last_hit_time = now

            # KO
            if self.hp <= 0:
                self.state_machine.handle_state_event(('KO', None))
                return

            # Dizzy
            if self.hp <= self.max_hp * 0.3:
                self.state_machine.handle_state_event(('DIZZY', None))
                return

            # ----------------------------------------
            # Final Fight 벡터 기반 넉백
            # ----------------------------------------
            attack_type = attacker.current_attack_type
            base_knockback = Boxer.KNOCKBACK_POWER.get(attack_type, 20)

            # 거리 기반 넉백 보정
            knockback = self.adjust_knockback_based_on_distance(attacker, base_knockback)

            # 넉백 시작 (벡터 기반)
            self.start_pushback(attacker=attacker, amount=knockback, duration=0.18)

            # Hurt 상태 진입
            self.state_machine.handle_state_event(('HURT', None))

            if old_hp != self.hp:
                print("P1 HP:", self.hp)


class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        # Idle 상태에 진입할 때 idle 시트로 변경
        self.boxer.use_sheet(self.boxer.cfg['idle'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

    def draw(self):
        self.boxer.draw_current()

class Walk:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0

        sheet = self.boxer.cfg.get('walk_forward')
        self.boxer.use_sheet(sheet)

    def exit(self, e):
        self.boxer.dir = 0

    def do(self):
        self.boxer.frame = (self.boxer.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        self.boxer.x += self.boxer.xdir * WALK_SPEED_PPS * game_framework.frame_time
        self.boxer.y += self.boxer.ydir * WALK_SPEED_PPS * game_framework.frame_time

    def draw(self):
        self.boxer.draw_current()

class Hurt:
    DURATION = 0.25  # 피격 모션 길이

    def __init__(self, boxer):
        self.boxer = boxer
        self.start_time = 0

    def enter(self, e):
        self.start_time = get_time()
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['hurt'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        # 모션 끝나면 Idle로 자동 복귀
        if get_time() - self.start_time >= Hurt.DURATION:
            self.boxer.state_machine.handle_state_event(('HURT_DONE', None))

    def draw(self):
        self.boxer.draw_current()

class Dizzy:
    DURATION = 0.8  # 어지러움 유지 시간

    def __init__(self, boxer):
        self.boxer = boxer
        self.start_time = 0

    def enter(self, e):
        self.start_time = get_time()
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['dizzy'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        # 자동 복귀
        if get_time() - self.start_time >= Dizzy.DURATION:
            self.boxer.state_machine.handle_state_event(('DIZZY_DONE', None))

    def draw(self):
        self.boxer.draw_current()

class Ko:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['ko'])

        self.boxer.pushback_time = 0
        self.boxer.pushback_velocity_x = 0
        self.boxer.pushback_velocity_y = 0

    def exit(self, e):
        pass

    def do(self):
        # KO는 마지막 프레임에서 멈춤
        max_frame = self.boxer.cols - 1
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        if self.boxer.frame > max_frame:
            self.boxer.frame = max_frame  # 프레임 고정

    def draw(self):
        self.boxer.draw_current()
