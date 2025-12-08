from pico2d import *
from key_events import *
from state_machine import StateMachine
from hitbox_data import HITBOX_DATA
from hitbox import HitBox
from attack_state import AttackState
from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action
from attack_router import AttackRouter
from debug_manager import log, DEBUG_EVENT, DEBUG_STATE

# from walk_backward import WalkBackward

import game_framework
import game_world
import random
import sound_manager

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
        'front_hand': 150,  # 잽
        'rear_hand': 300,  # 스트레이트
        'uppercut': 400  # 어퍼컷
    }
    DAMAGE_TABLE = {
        'front_hand': 10,
        'rear_hand': 15,
        'uppercut': 30
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

        self.ignore_next_move_keyup = False

        # 중력 계수
        self.gravity = -600  # 튕김 후 아래로 떨어지는 힘

        self.hits = 0
        self.max_hp = cfg["max_hp"]  # 값 복사
        self.hp = self.max_hp  # hp는 무조건 새로 생성

        self.input_buffer = []  # 공격 입력을 저장하는 버퍼
        self.buffer_time = 0.25  # 입력 유효시간 (0.25초 권장)
        self.last_input_time = 0  # 마지막 입력 기록시간

        self.opponent = None

        self.hit_cool = 0.3
        self.last_hit_time = 0.0

        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face_dir = spawn.get("base_face", 1)
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
        self.BLOCK_ENTER = BlockEnter(self)
        self.BLOCK = Block(self)
        self.BLOCK_EXIT = BlockExit(self)

        self.ATTACK_ROUTER = AttackRouter(self)

        # 상태머신 이벤트 테이블 분리
        self.transitions_wasd = {
            self.IDLE: {
                event_walk: self.WALK,
                event_stop: self.IDLE,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                a_down: self.WALK,
                d_down: self.WALK,
                w_down: self.WALK,
                s_down: self.WALK,

                r_down: self.BLOCK_ENTER,
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
        self.transitions_wasd[self.IDLE].update({r_down: self.BLOCK_ENTER})
        self.transitions_wasd[self.WALK].update({r_down: self.BLOCK_ENTER})
        self.transitions_wasd[self.BLOCK_ENTER] = {block_enter_done: self.BLOCK, r_up: self.BLOCK_EXIT}
        self.transitions_wasd[self.BLOCK] = {r_up: self.BLOCK_EXIT}
        self.transitions_wasd[self.BLOCK_EXIT] = {block_exit_done: self.IDLE}

        self.transitions_arrows = {
            self.IDLE: {
                event_walk: self.WALK,
                event_stop: self.IDLE,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                left_down: self.WALK,
                right_down: self.WALK,
                up_down: self.WALK,
                down_down: self.WALK,

                semicolon_down: self.BLOCK_ENTER,
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

        self.transitions_arrows[self.IDLE].update({semicolon_down: self.BLOCK_ENTER})
        self.transitions_arrows[self.WALK].update({semicolon_down: self.BLOCK_ENTER})
        self.transitions_arrows[self.BLOCK_ENTER] = {block_enter_done: self.BLOCK, semicolon_up: self.BLOCK_EXIT}
        self.transitions_arrows[self.BLOCK] = {semicolon_up: self.BLOCK_EXIT}
        self.transitions_arrows[self.BLOCK_EXIT] = {block_exit_done: self.IDLE}

        # controls에 따라 상태머신 선택
        if self.controls == 'wasd':
            transitions = self.transitions_wasd
        else:
            transitions = self.transitions_arrows

        self.state_machine = StateMachine(self.IDLE, transitions)

        self.is_cpu = False  # 기본은 사람 조작
        self.ai_level = 'easy'  # 'easy' / 'medium' / 'hard'
        self.bt = None  # BehaviorTree 객체 (나중에 build_bt에서 설정)

        self.ai_last_attack_time = 0.0
        self.ai_blocking = False
        self.ai_block_start_time = 0.0

        # 이동 제어용
        self.ai_move_dir = 0

    # ----------------------------
    # AI용 가짜 키 이벤트 클래스
    # ----------------------------
    class _AIKeyEvent:
        def __init__(self, key_type, key_code):
            self.type = key_type
            self.key = key_code

    # ----------------------------
    # AI 입력 함수들 (★ Boxer 메서드)
    # ----------------------------
    def ai_press_key(self, key_code):
        e = Boxer._AIKeyEvent(SDL_KEYDOWN, key_code)
        self.state_machine.handle_state_event(('INPUT', e))

    def ai_release_key(self, key_code):
        e = Boxer._AIKeyEvent(SDL_KEYUP, key_code)
        self.state_machine.handle_state_event(('INPUT', e))

    def ai_stop_move(self):
        if self.ai_move_dir != 0:
            self.ai_move_dir = 0
            self.xdir = 0
            self.state_machine.handle_state_event(('STOP', None))

    def ai_move_towards(self, dir):
        if dir == 0:
            self.ai_stop_move()
            return

        if self.ai_move_dir != dir:
            self.ai_move_dir = dir
            self.xdir = dir
            self.face_dir = dir
            self.state_machine.handle_state_event(('WALK', None))

    def ai_can_act(self):
        cur = self.state_machine.cur_state
        KOType = type(self.KO)
        DizzyType = type(self.DIZZY)
        HurtType = type(self.HURT)

        if isinstance(cur, (KOType, DizzyType, HurtType)):
            self.ai_stop_move()
            return False
        return True

    def ai_distance_to_opponent(self):
        if self.opponent is None:
            return None
        return self.opponent.x - self.x

    def ai_in_attack_range(self):
        d = self.ai_distance_to_opponent()
        if d is None:
            return False

        dx = abs(d)

        if self.ai_level == 'easy':
            max_range = 170
        elif self.ai_level == 'medium':
            max_range = 210
        else:
            max_range = 240

        return dx <= max_range

    def ai_attack_random(self):
        now = get_time()

        if self.ai_level == 'easy':
            base_cd = 0.9
        elif self.ai_level == 'medium':
            base_cd = 0.6
        else:
            base_cd = 0.35

        if now - self.ai_last_attack_time < base_cd:
            return BehaviorTree.FAIL

        cur = self.state_machine.cur_state
        bad_types = (
            type(self.FRONT_HAND), type(self.REAR_HAND), type(self.UPPERCUT),
            type(self.BLOCK), type(self.BLOCK_ENTER), type(self.BLOCK_EXIT),
            type(self.HURT), type(self.DIZZY), type(self.KO)
        )
        if isinstance(cur, bad_types):
            return BehaviorTree.FAIL

        if self.controls == 'wasd':
            front_key, rear_key, upper_key = SDLK_f, SDLK_g, SDLK_h
        else:
            front_key, rear_key, upper_key = SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH

        choice = random.choice(['front', 'rear', 'upper'])
        if choice == 'front':
            self.ai_press_key(front_key)
        elif choice == 'rear':
            self.ai_press_key(rear_key)
        else:
            self.ai_press_key(upper_key)

        self.ai_last_attack_time = now
        return BehaviorTree.SUCCESS

    def ai_should_guard(self):
        if self.opponent is None:
            return False

        opp_state = self.opponent.state_machine.cur_state
        FHType = type(self.opponent.FRONT_HAND)
        RHType = type(self.opponent.REAR_HAND)
        UType = type(self.opponent.UPPERCUT)

        if isinstance(opp_state, (FHType, RHType, UType)):
            return True
        return False

    def ai_do_guard(self):
        if self.controls == 'wasd':
            block_key = SDLK_r
        else:
            block_key = SDLK_SEMICOLON

        now = get_time()

        if not self.ai_blocking:
            if self.ai_level == 'easy':
                guard_prob = 0.3
                hold_time = 0.3
            elif self.ai_level == 'medium':
                guard_prob = 0.6
                hold_time = 0.35
            else:
                guard_prob = 0.9
                hold_time = 0.4

            if random.random() > guard_prob:
                return BehaviorTree.FAIL

            self.ai_blocking = True
            self.ai_block_start_time = now
            self.ai_block_hold_time = hold_time

            self.ai_stop_move()
            self.ai_press_key(block_key)
            return BehaviorTree.RUNNING
        else:
            if now - self.ai_block_start_time >= self.ai_block_hold_time:
                self.ai_blocking = False
                self.ai_release_key(block_key)
                return BehaviorTree.SUCCESS
            else:
                return BehaviorTree.RUNNING

    def bt_is_ko(self):
        if isinstance(self.state_machine.cur_state, type(self.KO)):
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def bt_in_attack_range(self):
        if not self.ai_can_act():
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS if self.ai_in_attack_range() else BehaviorTree.FAIL

    def bt_opponent_attacking(self):
        if not self.ai_can_act():
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS if self.ai_should_guard() else BehaviorTree.FAIL

    def bt_do_nothing(self):
        self.ai_stop_move()
        return BehaviorTree.SUCCESS

    def bt_attack_random(self):
        if not self.ai_can_act():
            return BehaviorTree.FAIL
        if not self.ai_in_attack_range():
            return BehaviorTree.FAIL
        return self.ai_attack_random()

    def bt_guard(self):
        if not self.ai_can_act():
            return BehaviorTree.FAIL
        return self.ai_do_guard()

    def bt_chase(self):
        if not self.ai_can_act():
            return BehaviorTree.FAIL

        d = self.ai_distance_to_opponent()
        if d is None:
            self.ai_stop_move()
            return BehaviorTree.FAIL

        dx = abs(d)
        if dx < 80:
            self.ai_stop_move()
            return BehaviorTree.SUCCESS

        if d > 0:
            self.ai_move_towards(1)
        else:
            self.ai_move_towards(-1)
        return BehaviorTree.RUNNING

    def build_bt(self):
        ko_seq = Sequence("KO Seq",
                          Condition("Is KO", self.bt_is_ko),
                          Action("Do Nothing", self.bt_do_nothing))

        attack_seq = Sequence("Attack Seq",
                              Condition("In Attack Range", self.bt_in_attack_range),
                              Action("Attack Random", self.bt_attack_random))

        guard_seq = Sequence("Guard Seq",
                             Condition("Opponent Attacking", self.bt_opponent_attacking),
                             Action("Guard", self.bt_guard))

        chase_act = Action("Chase", self.bt_chase)

        root = Selector("AI Root", ko_seq, attack_seq, guard_seq, chase_act)
        self.bt = BehaviorTree(root)

    def enable_ai(self, level='easy'):
        self.is_cpu = True
        self.ai_level = level
        self.build_bt()

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
        dx = self.x - attacker.x
        dy = self.y - attacker.y
        length = max((dx * dx + dy * dy) ** 0.5, 0.001)
        nx, ny = dx / length, dy / length

        # 넉백 속도 (y는 너무 튀지 않게 약하게)
        power = amount / duration
        self.pushback_velocity_x = nx * power
        self.pushback_velocity_y = ny * power * 0.25

        self.gravity = -2000
        self.pushback_time = duration
        self.pushback_duration = duration

        self.hit_floor_y = self.y
        # 넉백 중 이동 입력 완전 무시
        self.xdir = 0
        self.ydir = 0

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
        dt = game_framework.frame_time

        if self.pushback_time > 0:
            dt = game_framework.frame_time

            # X 넉백 이동
            self.x += self.pushback_velocity_x * dt

            # Y 넉백 + 중력
            self.pushback_velocity_y += self.gravity * dt
            self.y += self.pushback_velocity_y * dt

            # ★ 피격 레벨 착지 처리
            if self.y <= self.hit_floor_y:
                self.y = self.hit_floor_y
                self.pushback_velocity_y = 0
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                return

            LEFT_WALL = 50
            RIGHT_WALL = 750
            CEILING_Y = 500

            if self.x < LEFT_WALL:
                self.x = LEFT_WALL
                self.pushback_velocity_x = 0  # ★ 여기
            elif self.x > RIGHT_WALL:
                self.x = RIGHT_WALL
                self.pushback_velocity_x = 0  # ★ 여기

            if self.y > CEILING_Y:
                self.y = CEILING_Y

            # ★ 넉백 시간 감소
            self.pushback_time -= dt
            if self.pushback_time <= 0:
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                self.pushback_velocity_y = 0
            return

        self.state_machine.update()

        if self.is_cpu and self.bt is not None:
            self.bt.run()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        # 디버그 로그: 현재 상태 + 들어온 이벤트
        log(
            DEBUG_STATE,
            f"[EVENT] state={self.state_machine.cur_state.__class__.__name__}, "
            f"type={event.type}, key={getattr(event, 'key', None)}, "
            f"xdir={self.xdir}, ydir={self.ydir}"
        )

        # CPU 조작이면 사람 입력 무시
        if self.is_cpu or self.controls == 'cpu':
            return

        # 키보드 입력이 아니면 무시
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        # 넉백 중에는 입력 무시
        if self.pushback_time > 0:
            return

        if self.controls == 'wasd':
            # P1: 이동 + 공격 + 가드 키만
            allowed_keys = {
                SDLK_a, SDLK_d, SDLK_w, SDLK_s,  # 이동
                SDLK_f, SDLK_g, SDLK_h,  # 공격
                SDLK_r  # 가드
            }
        else:
            allowed_keys = {
                SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN,
                SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH,
                SDLK_SEMICOLON
            }

        if event.key not in allowed_keys:
            # 이 Boxer 관할이 아닌 키는 완전히 무시
            return

        if isinstance(self.state_machine.cur_state, (BlockEnter, Block, BlockExit)):
            if event.type == SDL_KEYDOWN:
                if self.controls == 'wasd':
                    if event.key != SDLK_r:
                        log(DEBUG_STATE,print(f"[FILTER] BlockState={self.state_machine.cur_state.__class__.__name__} / "
                              f"IGNORED key={event.key}"))
                        return
                else:
                    if event.key != SDLK_SEMICOLON:
                        log(DEBUG_STATE,print(f"[FILTER] BlockState={self.state_machine.cur_state.__class__.__name__} / "
                              f"IGNORED key={event.key}"))
                        return

        # KO / Dizzy 상태는 입력 무시
        if isinstance(self.state_machine.cur_state, Ko):
            return
        if isinstance(self.state_machine.cur_state, Dizzy):
            return

        if event.type == SDL_KEYDOWN:
            if self.controls == 'wasd':
                if event.key == SDLK_a:
                    self.face_dir = -1  # 왼쪽
                elif event.key == SDLK_d:
                    self.face_dir = +1  # 오른쪽
            else:  # arrows
                if event.key == SDLK_LEFT:
                    self.face_dir = -1  # 왼쪽
                elif event.key == SDLK_RIGHT:
                    self.face_dir = +1  # 오른쪽

        if self.controls == 'wasd':  # P1
            attack_key_map = {
                SDLK_f: 'front_hand',
                SDLK_g: 'rear_hand',
                SDLK_h: 'uppercut'
            }
        else:  # P2
            attack_key_map = {
                SDLK_COMMA: 'front_hand',
                SDLK_PERIOD: 'rear_hand',
                SDLK_SLASH: 'uppercut'
            }

        if event.type == SDL_KEYDOWN and event.key in attack_key_map:
            attack_name = attack_key_map[event.key]
            now = get_time()

            # 공격 중 → 버퍼 저장
            if isinstance(self.state_machine.cur_state, AttackState):
                self.input_buffer.append(attack_name)
                self.last_input_time = now
                log(DEBUG_EVENT,print(f"[BUFFER-ADD] + {attack_name} | buffer={self.input_buffer}"))
                return

                # 공격 중이 아니면 즉시 AttackRouter 실행
            self.last_input_time = now
            log(DEBUG_EVENT,print(f"[ATTACK] immediate → {attack_name}"))
            self.ATTACK_ROUTER.enter(('ATTACK', attack_name))
            return

        # --------------------------------
        # 이동키 처리
        # --------------------------------
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):

            if self.controls == 'wasd':
                move_keys = {SDLK_a, SDLK_d, SDLK_w, SDLK_s}
            else:
                move_keys = {SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN}

            if (event.type == SDL_KEYUP
                    and self.ignore_next_move_keyup
                    and event.key in move_keys):
                log(DEBUG_EVENT,print(f"[BLOCK_EXIT] ignore first move KEYUP: key={event.key}"))
                self.ignore_next_move_keyup = False
                return

            if event.key in move_keys:

                log(DEBUG_EVENT,print(f"[MOVE_KEYS-BEFORE] state={self.state_machine.cur_state.__class__.__name__}, "
                      f"event_type={event.type}, key={event.key}, "
                      f"xdir={self.xdir}, ydir={self.ydir}"))

                cur_xdir, cur_ydir = self.xdir, self.ydir

                if isinstance(self.state_machine.cur_state, BlockExit):
                    log(DEBUG_EVENT,print(f"[PATCH] BlockExit ignores move key: {event.key}"))
                    return

                # 이동키에 따른 바라보는 방향 변경 & xdir/ydir 업데이트
                if event.type == SDL_KEYDOWN:
                    if self.controls == 'wasd':
                        if event.key == SDLK_a:   self.xdir = -1
                        if event.key == SDLK_d:   self.xdir = +1
                        if event.key == SDLK_w:   self.ydir = +1
                        if event.key == SDLK_s:   self.ydir = -1
                    else:
                        if event.key == SDLK_LEFT:   self.xdir = -1
                        if event.key == SDLK_RIGHT:  self.xdir = +1
                        if event.key == SDLK_UP:     self.ydir = +1
                        if event.key == SDLK_DOWN:   self.ydir = -1
                elif event.type == SDL_KEYUP:
                    if event.key in move_keys:

                        if self.ignore_next_move_keyup:
                            log(DEBUG_EVENT,print(f"[PATCH] swallow first keyup after BlockExit: {event.key}"))
                            self.ignore_next_move_keyup = False
                            return

                    if self.controls == 'wasd':
                        if event.key == SDLK_a and self.xdir < 0:  self.xdir = 0
                        if event.key == SDLK_d and self.xdir > 0:  self.xdir = 0
                        if event.key == SDLK_w and self.ydir > 0:  self.ydir = 0
                        if event.key == SDLK_s and self.ydir < 0:  self.ydir = 0
                    else:
                        if event.key == SDLK_LEFT and self.xdir < 0: self.xdir = 0
                        if event.key == SDLK_RIGHT and self.xdir > 0: self.xdir = 0
                        if event.key == SDLK_UP and self.ydir > 0: self.ydir = 0
                        if event.key == SDLK_DOWN and self.ydir < 0: self.ydir = 0

                log(DEBUG_EVENT,print(f"[MOVE_KEYS-AFTER]  state={self.state_machine.cur_state.__class__.__name__}, "
                      f"event_type={event.type}, key={event.key}, "
                      f"xdir={self.xdir}, ydir={self.ydir}"))

                if self.xdir == 0 and self.ydir == 0:
                    log(DEBUG_EVENT,print("[PATCH] => STOP"))
                    self.state_machine.handle_state_event(('STOP', self.face_dir))
                else:
                    # KEYDOWN일 때만 WALK 발생
                    if event.type == SDL_KEYDOWN:
                        log(DEBUG_EVENT,print("[PATCH] => WALK"))
                        self.state_machine.handle_state_event(('WALK', None))

        # --------------------------------
        # 나머지 입력은 그대로 상태머신에 전달
        # (공격키 & 이동키 모두 포함)
        # --------------------------------
        self.state_machine.handle_state_event(('INPUT', event))

    def _select_attack_state(self, attack_name):
        if attack_name == 'front_hand':
            return self.FRONT_HAND
        elif attack_name == 'rear_hand':
            return self.REAR_HAND
        elif attack_name == 'uppercut':
            return self.UPPERCUT

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
        # 피격 쿨타임(1초) 지나면 연속 피격 카운트 초기화
        if now - self.last_hit_time > 1.0:
            self.hits = 0

        # KO 상태 충돌 무시
        if isinstance(self.state_machine.cur_state, Ko):
            return
        if isinstance(self.state_machine.cur_state, Dizzy):
            return
        if isinstance(self.state_machine.cur_state, (BlockEnter, Block)):
            if not hasattr(other, 'owner'):
                return
            sound_manager.play("blocking")
            self.last_hit_time = now

            # 넉백 50% 적용
            attack_type = other.owner.current_attack_type
            base_knock = Boxer.KNOCKBACK_POWER.get(attack_type, 20)
            knock = self.adjust_knockback_based_on_distance(other.owner, base_knock * 0.5)

            self.start_pushback(other.owner, amount=knock, duration=0.18)
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

            # 수평 겹침량 (왼/오)
            overlap_x1 = r1 - l2  # self의 오른쪽이 other의 왼쪽을 침범
            overlap_x2 = r2 - l1  # other의 오른쪽이 self의 왼쪽을 침범
            overlap_x = min(overlap_x1, overlap_x2)

            # 수직 겹침량 (위/아래)
            overlap_y1 = t1 - b2  # self의 위가 other의 아래를 침범
            overlap_y2 = t2 - b1  # other의 위가 self의 아래를 침범
            overlap_y = min(overlap_y1, overlap_y2)

            # 겹침이 실제로 발생했는지 체크
            if overlap_x > 0 and overlap_y > 0:

                # 더 작은 축으로 밀어냄 (MTV 방식)
                if overlap_x < overlap_y:
                    # 좌/우로 밀기
                    push = overlap_x / 2
                    if self.x < other.x:
                        self.x -= push
                        other.x += push
                    else:
                        self.x += push
                        other.x -= push
                else:
                    # 위/아래로 밀기
                    push = overlap_y / 2
                    if self.y < other.y:
                        self.y -= push
                        other.y += push
                    else:
                        self.y += push
                        other.y -= push

            return

        if group in ('P1_attack:P2', 'P2_attack:P1'):
            if not hasattr(other, 'owner'):
                print("[WARNING] attack collision but 'other' has no owner:", other)
                return

            attacker = other.owner
            attack_type = attacker.current_attack_type

            # ★ 공격 타입별 피해량 계산
            damage = Boxer.DAMAGE_TABLE.get(attack_type, 10)

            # 체력 감소
            old_hp = self.hp
            self.hp = max(0, self.hp - damage)
            self.last_hit_time = now

            # 사운드: 공격 타입 이름으로 재생
            sound_manager.play(attack_type)

            # KO / DIZZY 판정
            if self.hp <= 0:
                self.state_machine.handle_state_event(('KO', None))
                return
            # === 연속 피격 카운트 증가 ===
            self.hits += 1

            # === 3번 연속 피격 → DIZZY ===
            if self.hits >= 3:
                self.hits = 0  # 초기화
                self.state_machine.handle_state_event(('DIZZY', None))
                return

            # ====== 넉백 호출 (공격 타입 기반) ======
            base_knock = Boxer.KNOCKBACK_POWER.get(attack_type, 20)
            knockback = self.adjust_knockback_based_on_distance(attacker, base_knock)

            self.start_pushback(attacker, amount=knockback, duration=0.18)

            # 피격 상태로 전환
            self.state_machine.handle_state_event(('HURT', None))

            # 디버그용 HP 출력
            if old_hp != self.hp:
                if group == 'P1_attack:P2':
                    print("P2 HP:", self.hp)
                else:
                    print("P1 HP:", self.hp)

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        log(DEBUG_EVENT, f"[ENTER] Idle: reset xdir/ydir from {self.boxer.xdir}, {self.boxer.ydir}")
        self.boxer.use_sheet(self.boxer.cfg['idle'])
        self.boxer.xdir = 0
        self.boxer.ydir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

        if self.boxer.input_buffer:
            now = get_time()
            if now - self.boxer.last_input_time <= self.boxer.buffer_time:
                next_attack = self.boxer.input_buffer.pop(0)
                log(DEBUG_EVENT,f"[BUFFER-USE] pop='{next_attack}'  buffer={self.boxer.input_buffer}")

                # AttackRouter 직접 호출 (state_machine 사용 X)
                self.boxer.ATTACK_ROUTER.enter(('ATTACK', next_attack))
                return

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

class BlockEnter:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0
        self.boxer.use_sheet(self.boxer.cfg['blocking'])

        # 이동 금지
        self.boxer.xdir = 0
        self.boxer.ydir = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 증가
        self.boxer.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        if self.boxer.frame >= self.boxer.cols - 1:
            self.boxer.frame = self.boxer.cols - 1
            self.boxer.state_machine.handle_state_event(('BLOCK_ENTER_DONE', None))

    def draw(self):
        self.boxer.draw_current()

class Block:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.use_sheet(self.boxer.cfg['blocking'])  # 가드 유지 포즈
        self.boxer.frame = self.boxer.cols - 1  # 마지막 프레임 고정
        self.boxer.xdir = 0
        self.boxer.ydir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = self.boxer.cols - 1

    def draw(self):
        self.boxer.draw_current()

class BlockExit:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        print("[ENTER] BlockExit: force stop movement")
        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.ignore_next_move_keyup = True
        self.boxer.use_sheet(self.boxer.cfg['blocking'])
        self.boxer.frame = self.boxer.cols - 1

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame -= FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        if self.boxer.frame <= 0:
            self.boxer.frame = 0
            self.boxer.state_machine.handle_state_event(('BLOCK_EXIT_DONE', None))

    def draw(self):
        self.boxer.draw_current()
