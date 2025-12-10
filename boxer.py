from pico2d import *
from key_events import *
from state_machine import StateMachine
from hitbox_data import HITBOX_DATA
from hitbox import HitBox
from attack_state import AttackState
from attack_router import AttackRouter
from debug_manager import log, DEBUG_EVENT, DEBUG_STATE

from hurt import Hurt
from dizzy import Dizzy
from ko import Ko
from block_enter import BlockEnter
from block import Block
from block_exit import BlockExit
from walk import Walk
from idle import Idle

import game_framework
import game_world
import sound_manager

from boxer_ai import BoxerAI

# ----------------------------
# 상수들
# ----------------------------
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
WALK_SPEED_KMPH = 20.0          # Km / Hour
WALK_SPEED_MPM = (WALK_SPEED_KMPH * 1000.0 / 60.0)
WALK_SPEED_MPS = (WALK_SPEED_MPM / 60.0)
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


class Boxer:
    """
    플레이어/CPU 공용 Boxer 캐릭터
    - 상태머신 기반 이동/공격/가드/피격/KO
    - AI는 BoxerAI(별도 파일)로 분리
    """
    _img_cache = {}

    FRAMES_PER_ACTION = FRAMES_PER_ACTION
    ACTION_PER_TIME = ACTION_PER_TIME

    # 공격 종류별 넉백 세기(픽셀)
    KNOCKBACK_POWER = {
        'front_hand': 150,   # 잽
        'rear_hand': 300,    # 스트레이트
        'uppercut': 400      # 어퍼컷
    }

    # 공격 종류별 데미지
    DAMAGE_TABLE = {
        'front_hand': 10,
        'rear_hand': 15,
        'uppercut': 30
    }

    def __init__(self, cfg: dict):
        # ----------------------------
        # 기본 설정/상태
        # ----------------------------
        self.cfg = cfg
        self.current_attack_type = None   # 현재 공격 종류
        self.base_face = None             # 스프라이트 기준 바라보는 방향
        self.on_ko_end = None             # KO 종료 콜백 (필요 시)

        # 이동/방향
        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face_dir = spawn.get("base_face", 1)
        self.xdir, self.ydir = 0, 0

        self.dir = 0                      # 예전 코드 호환용
        self.resume_move_dir = 0          # 공격 후 재개할 방향

        # 넉백
        self.pushback_velocity_x = 0
        self.pushback_velocity_y = 0
        self.pushback_time = 0
        self.pushback_duration = 0
        self.gravity = -600               # 기본 중력 계수
        self.hit_floor_y = self.y

        # 키 상태 관리
        self.ignore_next_move_keyup = False
        self.move_key_down = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
        # 공격 키 눌림 상태 (오토리핏 방지)
        self.attack_key_down = {
            'front_hand': False,
            'rear_hand': False,
            'uppercut': False
        }

        # 체력/피격
        self.hits = 0
        self.max_hp = cfg["max_hp"]
        self.hp = self.max_hp
        self.hit_cool = 0.3
        self.last_hit_time = 0.0

        # 공격 버퍼
        self.input_buffer = []
        self.buffer_time = 0.45
        self.last_input_time = 0

        # 상대
        self.opponent = None

        # 조작 타입
        self.controls = cfg.get('controls', 'both')  # 'wasd' or 'arrows' etc.
        self.is_cpu = False                          # 기본: 사람 조작
        self.ai = None                               # BoxerAI 인스턴스

        # 스프라이트/이미지 세팅
        idle_sheet = cfg['idle']
        self.image = None
        self.cols = 0
        self.frame_w = 0
        self.frame_h = 0
        self.scale = 1.0
        self.frame = 0
        self.use_sheet(idle_sheet)

        # ----------------------------
        # 상태 객체들 생성
        # ----------------------------
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.FRONT_HAND = AttackState(self, 'front_hand')
        self.REAR_HAND = AttackState(self, 'rear_hand')
        self.UPPERCUT = AttackState(self, 'uppercut')
        self.HURT = Hurt(self)
        self.DIZZY = Dizzy(self)
        self.KO = Ko(self)
        self.BLOCK_ENTER = BlockEnter(self)
        self.BLOCK = Block(self)
        self.BLOCK_EXIT = BlockExit(self)

        # 공격 라우터 (event_attack → 다음 AttackState)
        self.ATTACK_ROUTER = AttackRouter(self)

        # ----------------------------
        # 상태 전이 테이블
        # ----------------------------
        self._build_transitions()

        # controls에 따라 전이 테이블 선택
        if self.controls == 'wasd':
            transitions = self.transitions_wasd
        else:
            transitions = self.transitions_arrows

        # 상태머신 생성 (초기 상태: IDLE)
        self.state_machine = StateMachine(self.IDLE, transitions)

    # ----------------------------
    # 상태 전이 테이블 구성
    # ----------------------------
    def _build_transitions(self):
        # --- WASD (P1) ---
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
                h_down: self.UPPERCUT,
            },
            self.WALK: {
                event_stop: self.IDLE,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                r_down: self.BLOCK_ENTER,
                f_down: self.FRONT_HAND,
                g_down: self.REAR_HAND,
                h_down: self.UPPERCUT,
            },
            self.FRONT_HAND: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.REAR_HAND: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.UPPERCUT: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.HURT: {event_hurt_done: self.IDLE, event_ko: self.KO},
            self.DIZZY: {event_dizzy_done: self.IDLE, event_ko: self.KO},
            self.KO: {},
            self.BLOCK_ENTER: {block_enter_done: self.BLOCK, r_up: self.BLOCK_EXIT},
            self.BLOCK: {r_up: self.BLOCK_EXIT},
            self.BLOCK_EXIT: {block_exit_done: self.IDLE},
        }

        # 가드 진입 중복 안전
        self.transitions_wasd[self.IDLE].update({r_down: self.BLOCK_ENTER})
        self.transitions_wasd[self.WALK].update({r_down: self.BLOCK_ENTER})
        # 이동 중 공격 후 같은 WALK로 복귀
        self.transitions_wasd[self.WALK][event_attack_end] = self.WALK

        # --- 방향키 (P2) ---
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
                slash_down: self.UPPERCUT,
            },
            self.WALK: {
                event_stop: self.IDLE,

                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO,

                semicolon_down: self.BLOCK_ENTER,
                comma_down: self.FRONT_HAND,
                period_down: self.REAR_HAND,
                slash_down: self.UPPERCUT,
            },
            self.FRONT_HAND: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.REAR_HAND: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.UPPERCUT: {
                event_attack: self.ATTACK_ROUTER,
                event_attack_end: self.IDLE,
                event_hurt: self.HURT,
                event_dizzy: self.DIZZY,
                event_ko: self.KO
            },
            self.HURT: {event_hurt_done: self.IDLE, event_ko: self.KO},
            self.DIZZY: {event_dizzy_done: self.IDLE, event_ko: self.KO},
            self.KO: {},
            self.BLOCK_ENTER: {block_enter_done: self.BLOCK, semicolon_up: self.BLOCK_EXIT},
            self.BLOCK: {semicolon_up: self.BLOCK_EXIT},
            self.BLOCK_EXIT: {block_exit_done: self.IDLE},
        }

        self.transitions_arrows[self.IDLE].update({semicolon_down: self.BLOCK_ENTER})
        self.transitions_arrows[self.WALK].update({semicolon_down: self.BLOCK_ENTER})
        self.transitions_arrows[self.WALK][event_attack_end] = self.WALK

    # ----------------------------
    # AI 활성화
    # ----------------------------
    def enable_ai(self, level='easy'):
        self.is_cpu = True
        if self.ai is None:
            self.ai = BoxerAI(self, level)
        else:
            self.ai.set_level(level)

    # ----------------------------
    # 렌더링 관련
    # ----------------------------
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

        frame = int(self.frame) % self.cols

        src_x = frame * self.frame_w
        src_y = 0
        src_w = self.frame_w
        src_h = self.frame_h

        draw_w = int(self.frame_w * self.scale)
        draw_h = int(self.frame_h * self.scale)

        if self.face_dir == self.base_face:
            self.image.clip_draw(
                src_x, src_y, src_w, src_h,
                self.x, self.y,
                draw_w, draw_h
            )
        else:
            self.image.clip_composite_draw(
                src_x, src_y, src_w, src_h,
                0, 'h',
                self.x, self.y,
                draw_w, draw_h
            )

    # ----------------------------
    # 매 프레임 업데이트
    # ----------------------------
    def update(self):
        log(
            DEBUG_STATE,
            f"[UPDATE] cur_state={self.state_machine.cur_state.__class__.__name__}, "
            f"x={self.x}, y={self.y}"
        )

        dt = game_framework.frame_time

        # 넉백 처리
        if self.pushback_time > 0:
            dt = game_framework.frame_time

            # X 넉백 이동
            self.x += self.pushback_velocity_x * dt

            # Y 넉백 + 중력
            self.pushback_velocity_y += self.gravity * dt
            self.y += self.pushback_velocity_y * dt

            # 착지 처리
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
                self.pushback_velocity_x = 0
            elif self.x > RIGHT_WALL:
                self.x = RIGHT_WALL
                self.pushback_velocity_x = 0

            if self.y > CEILING_Y:
                self.y = CEILING_Y

            self.pushback_time -= dt
            if self.pushback_time <= 0:
                self.pushback_time = 0
                self.pushback_velocity_x = 0
                self.pushback_velocity_y = 0
            return

        # 상태머신 로직
        self.state_machine.update()

        # AI 동작
        if self.is_cpu and self.ai is not None:
            self.ai.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    # ----------------------------
    # 입력 처리
    # ----------------------------
    def handle_event(self, event):
        # CPU 조작이면 사람 입력 무시
        if self.is_cpu or self.controls == 'cpu':
            return

        # SDL 키 이벤트만 처리
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        log(
            DEBUG_STATE,
            f"[EVENT] state={self.state_machine.cur_state.__class__.__name__}, "
            f"type={event.type}, key={getattr(event, 'key', None)}, "
            f"xdir={self.xdir}, ydir={self.ydir}"
        )

        # 넉백 중에는 입력 무시
        if self.pushback_time > 0:
            return

        # 1) 이 캐릭터 관할 키만 허용
        if self.controls == 'wasd':
            allowed_keys = {
                SDLK_a, SDLK_d, SDLK_w, SDLK_s,      # 이동
                SDLK_f, SDLK_g, SDLK_h,              # 공격
                SDLK_r                               # 가드
            }
        else:
            allowed_keys = {
                SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN,  # 이동
                SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH,        # 공격
                SDLK_SEMICOLON                              # 가드
            }

        if event.key not in allowed_keys:
            return

        # 2) Block 상태에서 불필요 키 필터링
        if isinstance(self.state_machine.cur_state, (BlockEnter, Block, BlockExit)):
            if event.type == SDL_KEYDOWN:
                attack_keys_wasd = (SDLK_f, SDLK_g, SDLK_h)
                attack_keys_arrow = (SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH)

                if self.controls == 'wasd':
                    if event.key not in (SDLK_r,) + attack_keys_wasd:
                        log(DEBUG_STATE, print(
                            f"[FILTER] BlockState={self.state_machine.cur_state.__class__.__name__} / "
                            f"IGNORED key={event.key}"
                        ))
                        return
                else:
                    if event.key not in (SDLK_SEMICOLON,) + attack_keys_arrow:
                        log(DEBUG_STATE, print(
                            f"[FILTER] BlockState={self.state_machine.cur_state.__class__.__name__} / "
                            f"IGNORED key={event.key}"
                        ))
                        return

        # 3) KO / Dizzy 입력 무시
        if isinstance(self.state_machine.cur_state, Ko):
            return
        if isinstance(self.state_machine.cur_state, Dizzy):
            return

        # 4) 이동키 눌림/해제 플래그 업데이트
        if self.controls == 'wasd':
            left_key, right_key, up_key, down_key = SDLK_a, SDLK_d, SDLK_w, SDLK_s
        else:
            left_key, right_key, up_key, down_key = SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN

        if event.type == SDL_KEYDOWN:
            if event.key == left_key:
                self.face_dir = -1
                self.move_key_down['left'] = True
            elif event.key == right_key:
                self.face_dir = +1
                self.move_key_down['right'] = True
            elif event.key == up_key:
                self.move_key_down['up'] = True
            elif event.key == down_key:
                self.move_key_down['down'] = True

        elif event.type == SDL_KEYUP:
            if event.key == left_key:
                self.move_key_down['left'] = False
            elif event.key == right_key:
                self.move_key_down['right'] = False
            elif event.key == up_key:
                self.move_key_down['up'] = False
            elif event.key == down_key:
                self.move_key_down['down'] = False

        # 5) 공격키 매핑
        if self.controls == 'wasd':
            attack_key_map = {
                SDLK_f: 'front_hand',
                SDLK_g: 'rear_hand',
                SDLK_h: 'uppercut'
            }
        else:
            attack_key_map = {
                SDLK_COMMA: 'front_hand',
                SDLK_PERIOD: 'rear_hand',
                SDLK_SLASH: 'uppercut'
            }

        # 6) 공격 입력 처리(오토리핏 방지 + 버퍼)
        if event.key in attack_key_map:
            attack_name = attack_key_map[event.key]

            if event.type == SDL_KEYDOWN:
                # 자동 반복 방지: 이미 눌려있으면 무시
                if self.attack_key_down[attack_name]:
                    return

                self.attack_key_down[attack_name] = True
                now = get_time()

                # 이미 공격 상태라면 → 버퍼에 저장
                if isinstance(self.state_machine.cur_state, AttackState):
                    self.input_buffer.append(attack_name)
                    self.last_input_time = now
                    log(DEBUG_EVENT, print(
                        f"[BUFFER-ADD] + {attack_name} | buffer={self.input_buffer}"
                    ))
                    return

                # 공격 시작 시, 이동 중이었다면 복귀 방향 기억
                if self.xdir != 0:
                    self.resume_move_dir = self.xdir
                else:
                    self.resume_move_dir = 0

                self.last_input_time = now
                log(DEBUG_EVENT, print(f"[ATTACK] immediate → {attack_name}"))
                self.state_machine.handle_state_event(('ATTACK', attack_name))
                return

            elif event.type == SDL_KEYUP:
                # 눌림 상태 해제
                self.attack_key_down[attack_name] = False
                return

        # 7) 공격 중일 때 이동키에 대한 STOP/WALK 이벤트 차단 (단, 플래그는 이미 위에서 갱신함)
        # 공격 중 이동키 입력 처리
        if isinstance(self.state_machine.cur_state, AttackState):
            if event.key in (left_key, right_key, up_key, down_key):

                # KEYUP은 반드시 move_key_down 갱신해야 한다
                if event.type == SDL_KEYUP:
                    if event.key == left_key:   self.move_key_down['left'] = False
                    if event.key == right_key:  self.move_key_down['right'] = False
                    if event.key == up_key:     self.move_key_down['up'] = False
                    if event.key == down_key:   self.move_key_down['down'] = False

                # KEYDOWN은 플래그만 갱신하고 STOP/WALK 는 막는다
                elif event.type == SDL_KEYDOWN:
                    if event.key == left_key:   self.move_key_down['left'] = True
                    if event.key == right_key:  self.move_key_down['right'] = True
                    if event.key == up_key:     self.move_key_down['up'] = True
                    if event.key == down_key:   self.move_key_down['down'] = True

                # 이동 관련 상태 전환(STOP/WALK)은 차단
                return

        # 8) 이동키 처리 (BlockExit/AttackState 예외 포함)
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):

            # BlockExit 중에는 KEYUP 무시
            if isinstance(self.state_machine.cur_state, BlockExit) and event.type == SDL_KEYUP:
                return

            # BlockExit 상태에서 이동키 아예 무시
            if isinstance(self.state_machine.cur_state, BlockExit):
                if event.key in (left_key, right_key, up_key, down_key):
                    log(DEBUG_EVENT, print(
                        f"[PATCH] BlockExit ignores move key: {event.key}"
                    ))
                    return

            # BlockExit 직후 첫 KEYUP swallow
            move_keys = {left_key, right_key, up_key, down_key}

            if (event.type == SDL_KEYUP
                    and self.ignore_next_move_keyup
                    and event.key in move_keys):
                log(DEBUG_EVENT, print(
                    f"[BLOCK_EXIT] ignore first move KEYUP: key={event.key}"
                ))
                self.ignore_next_move_keyup = False
                return

            if event.key in move_keys:
                log(DEBUG_EVENT, print(
                    f"[MOVE_KEYS-BEFORE] state={self.state_machine.cur_state.__class__.__name__}, "
                    f"event_type={event.type}, key={event.key}, "
                    f"xdir={self.xdir}, ydir={self.ydir}"
                ))

                # KEYDOWN → 방향 설정
                if event.type == SDL_KEYDOWN:
                    if event.key == left_key:
                        self.xdir = -1
                    elif event.key == right_key:
                        self.xdir = +1
                    elif event.key == up_key:
                        self.ydir = +1
                    elif event.key == down_key:
                        self.ydir = -1

                # KEYUP → 해당 방향 해제
                elif event.type == SDL_KEYUP:
                    if self.controls == 'wasd':
                        if event.key == left_key and self.xdir < 0:
                            self.xdir = 0
                        if event.key == right_key and self.xdir > 0:
                            self.xdir = 0
                        if event.key == up_key and self.ydir > 0:
                            self.ydir = 0
                        if event.key == down_key and self.ydir < 0:
                            self.ydir = 0
                    else:
                        if event.key == left_key and self.xdir < 0:
                            self.xdir = 0
                        if event.key == right_key and self.xdir > 0:
                            self.xdir = 0
                        if event.key == up_key and self.ydir > 0:
                            self.ydir = 0
                        if event.key == down_key and self.ydir < 0:
                            self.ydir = 0

                log(DEBUG_EVENT, print(
                    f"[MOVE_KEYS-AFTER]  state={self.state_machine.cur_state.__class__.__name__}, "
                    f"event_type={event.type}, key={event.key}, "
                    f"xdir={self.xdir}, ydir={self.ydir}"
                ))

                # 현재 눌려있는 이동키가 하나라도 있으면 WALK
                any_move_pressed = any(self.move_key_down.values())
                if any_move_pressed:
                    self.state_machine.handle_state_event(('WALK', None))
                else:
                    self.state_machine.handle_state_event(('STOP', self.face_dir))

                # xdir, ydir이 완전히 0이면 STOP 한 번 더
                # xdir, ydir이 완전히 0이면 STOP 한 번 더
                if self.xdir == 0 and self.ydir == 0:
                    log(DEBUG_EVENT, print("[PATCH] => STOP"))
                    self.state_machine.handle_state_event(('STOP', self.face_dir))
                else:
                    # KEYDOWN → '해당 이동키가 새로 눌린 경우'에만 WALK 발생
                    if event.type == SDL_KEYDOWN:
                        # 이 키가 기존엔 False였는지 확인
                        if (
                                (event.key == left_key and self.move_key_down['left'] == False) or
                                (event.key == right_key and self.move_key_down['right'] == False) or
                                (event.key == up_key and self.move_key_down['up'] == False) or
                                (event.key == down_key and self.move_key_down['down'] == False)
                        ):
                            # 새로 눌린 키 → WALK 시작
                            log(DEBUG_EVENT, f"[MOVE] WALK triggered by fresh KEYDOWN key={event.key}, move_key_down={self.move_key_down}")
                            self.state_machine.handle_state_event(('WALK', None))

        # 9) 나머지 입력은 상태머신에 그대로 전달
        self.state_machine.handle_state_event(('INPUT', event))

    # ----------------------------
    # 유틸리티 함수들
    # ----------------------------
    def _select_attack_state(self, attack_name):
        if attack_name == 'front_hand':
            return self.FRONT_HAND
        elif attack_name == 'rear_hand':
            return self.REAR_HAND
        elif attack_name == 'uppercut':
            return self.UPPERCUT

    def get_bb(self):
        bb_cfg = self.cfg["bb"]

        frame_w = self.frame_w * self.scale
        frame_h = self.frame_h * self.scale

        bb_w = frame_w * bb_cfg["w"]
        bb_h = frame_h * bb_cfg["h"]

        x_offset = bb_cfg["x_offset"] * self.scale
        y_offset = bb_cfg["y_offset"] * self.scale

        flipped = (self.face_dir != self.base_face)
        if flipped:
            x_offset = -x_offset

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
            duration=0.15
        )
        game_world.add_object(hitbox, 1)

        if self.controls == "wasd":
            game_world.add_collision_pair('P1_attack:P2', hitbox, self.opponent)
        else:
            game_world.add_collision_pair('P2_attack:P1', hitbox, self.opponent)

    def handle_collision(self, group, other):
        now = get_time()

        if now - self.last_hit_time > 1.0:
            self.hits = 0

        # KO, Dizzy는 충돌 무시
        if isinstance(self.state_machine.cur_state, Ko):
            return
        if isinstance(self.state_machine.cur_state, Dizzy):
            return

        # 가드 중인 경우(BlockEnter, Block)
        if isinstance(self.state_machine.cur_state, (BlockEnter, Block)):
            if not hasattr(other, 'owner'):
                return
            sound_manager.play("blocking")
            self.last_hit_time = now

            attack_type = other.owner.current_attack_type
            base_knock = Boxer.KNOCKBACK_POWER.get(attack_type, 20)
            knock = self.adjust_knockback_based_on_distance(other.owner, base_knock * 0.5)

            self.start_pushback(other.owner, amount=knock, duration=0.18)
            return

        # 넉백 중이면 모든 충돌 무시
        if self.pushback_time > 0:
            return

        # 피격 직후 무적 시간
        if now - self.last_hit_time < self.hit_cool:
            return

        if self.pushback_time > 0:
            return

        # 바디끼리 밀치기
        if group == 'body:block' and other is self.opponent:
            l1, b1, r1, t1 = self.get_bb()
            l2, b2, r2, t2 = other.get_bb()

            overlap_x1 = r1 - l2
            overlap_x2 = r2 - l1
            overlap_x = min(overlap_x1, overlap_x2)

            overlap_y1 = t1 - b2
            overlap_y2 = t2 - b1
            overlap_y = min(overlap_y1, overlap_y2)

            if overlap_x > 0 and overlap_y > 0:
                if overlap_x < overlap_y:
                    push = overlap_x / 2
                    if self.x < other.x:
                        self.x -= push
                        other.x += push
                    else:
                        self.x += push
                        other.x -= push
                else:
                    push = overlap_y / 2
                    if self.y < other.y:
                        self.y -= push
                        other.y += push
                    else:
                        self.y += push
                        other.y -= push

            return

        # 공격 히트
        if group in ('P1_attack:P2', 'P2_attack:P1'):
            if not hasattr(other, 'owner'):
                print("[WARNING] attack collision but 'other' has no owner:", other)
                return

            attacker = other.owner
            attack_type = attacker.current_attack_type

            damage = Boxer.DAMAGE_TABLE.get(attack_type, 10)

            old_hp = self.hp
            self.hp = max(0, self.hp - damage)
            self.last_hit_time = now

            sound_manager.play(attack_type)

            if self.hp <= 0:
                self.state_machine.handle_state_event(('KO', None))
                return

            self.hits += 1

            if self.hits >= 3:
                self.hits = 0
                self.state_machine.handle_state_event(('DIZZY', None))
                return

            base_knock = Boxer.KNOCKBACK_POWER.get(attack_type, 20)
            knockback = self.adjust_knockback_based_on_distance(attacker, base_knock)

            self.start_pushback(attacker, amount=knockback, duration=0.18)

            self.state_machine.handle_state_event(('HURT', None))

            if old_hp != self.hp:
                if group == 'P1_attack:P2':
                    print("P2 HP:", self.hp)
                else:
                    print("P1 HP:", self.hp)

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

        power = amount / duration
        self.pushback_velocity_x = nx * power
        self.pushback_velocity_y = ny * power * 0.25

        self.gravity = -2000
        self.pushback_time = duration
        self.pushback_duration = duration

        self.hit_floor_y = self.y

        self.xdir = 0
        self.ydir = 0

        self.move_key_down = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }

    def resume_move_after_action(self):
        """
        move_key_down 플래그를 기반으로 xdir/ydir를 재구성하고,
        WALK 또는 STOP 이벤트를 발생시킨다.
        """
        x, y = 0, 0

        if self.move_key_down['left']:
            x = -1
        if self.move_key_down['right']:
            x = +1
        if self.move_key_down['up']:
            y = +1
        if self.move_key_down['down']:
            y = -1

        log(DEBUG_EVENT,
            f"[RESUME] move_key_down={self.move_key_down}, new_dir=({x},{y}), old_dir=({self.xdir},{self.ydir})")

        self.xdir, self.ydir = x, y

        if x != 0 or y != 0:
            log(DEBUG_EVENT, "[RESUME] send WALK from resume_move_after_action()")
            self.state_machine.handle_state_event(('WALK', None))
        else:
            log(DEBUG_EVENT, "[RESUME] send STOP from resume_move_after_action()")
            self.state_machine.handle_state_event(('STOP', self.face_dir))
