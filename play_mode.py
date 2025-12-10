import lobby_mode
import game_framework
import game_world
import hitbox_edit
import sound_manager
import report_manager

from pico2d import *
from boxer import Boxer
from hp_ui import HpUi
from boxing_ring import BoxingRing
from button import Button, SpriteSheetButton
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos
from round_timer import RoundTimer
from round_intro import RoundIntro
from heart_ui import HeartUI
from game_over_ui import GameOverUI

# ============================================================
#  설정 / 전역 상태
# ============================================================

# 플레이어 캐릭터 선택 (현재는 P1/P2 고정)
p1_character = "P1"
p2_character = "P2"

# CPU 모드 설정 (lobby_mode / levels_mode 에서 조정)
cpu_mode = False      # True면 CPU vs Player
cpu_level = None      # 난이도 정보
cpu_player = None     # "P1" 또는 "P2" 중 누구를 CPU로 할지

# 라운드/승리/게임오버 상태
round_timer = None
round_intro = None
game_over_ui = None

current_round = 1
p1_wins = 0
p2_wins = 0

# 화면/오브젝트/버튼 관련
screen_w = 0
screen_h = 0

p1 = None
p2 = None
hpui = None
heart_ui = None
boxing_ring = None

buttons = []       # 상시 버튼(일시정지, 기어)
paused = False
pause_ui = []      # 일시정지 메뉴 버튼들

gear_open = False
gear_ui = []       # 기어(옵션) 메뉴 버튼들

sound_level = 0


# ============================================================
#  플레이어 설정 (P1 / P2)
# ============================================================

P1 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "wasd",
    "max_hp": 100,
    "bb": {"w": 0.40, "h": 0.555, "x_offset": 55, "y_offset": -30},
    "idle":  {"image": "resource/player1/player1_Idle.png",
              "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "spawn": {"x": 300, "y": 300},
    "walk_backward": {"image": "resource/player1/player1_Walk_Backward.png",
                      "cols": 10, "w": 499, "h": 489, "scale": 1.0},
    "walk_forward":  {"image": "resource/player1/player1_Walk_Forward.png",
                      "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "front_hand": {"image": "resource/player1/player1_FrontHand.png",
                   "cols": 6, "w": 499, "h": 489, "scale": 1.0,
                   "speed": 30, "base_face": 1,
                   "forward_movement": {3: 2}},
    "uppercut": {"image": "resource/player1/player1_Uppercut.png",
                 "cols": 7, "w": 499, "h": 489, "scale": 1.0,
                 "speed": 15, "base_face": 1,
                 "forward_movement": {4: 4}},
    "rear_hand": {"image": "resource/player1/player1_RearHand.png",
                  "cols": 6, "w": 499, "h": 489, "scale": 1.0,
                  "speed": 22, "base_face": 1,
                  "forward_movement": {3: 3}},
    "blocking": {"image": "resource/player1/player1_Blocking.png",
                 "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "hurt": {"image": "resource/player1/player1_Hurt.png",
             "cols": 8, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "dizzy": {"image": "resource/player1/player1_Dizzy.png",
              "cols": 8, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "ko": {"image": "resource/player1/player1_KO.png",
           "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1}
}

P2 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "arrows",
    "max_hp": 100,
    "bb": {"w": 0.555, "h": 0.7, "x_offset": -35, "y_offset": -20},
    "idle":  {"image": "resource/player2/player2_Idle.png",
              "cols": 10, "w": 744, "h": 711, "scale": 0.55, "base_face": -1},
    "spawn": {"x": 1800, "y": 300, "base_face": -1},
    "walk_backward": {"image": "resource/player2/player2_Walk_Backward.png",
                      "cols": 10, "w": 746, "h": 713, "scale": 0.55},
    "walk_forward":  {"image": "resource/player2/player2_Walk_Forward.png",
                      "cols": 10, "w": 746, "h": 713, "scale": 0.55, "base_face": -1},
    "front_hand": {"image": "resource/player2/player2_FrontHand.png",
                   "cols": 8, "w": 744, "h": 713, "scale": 0.55,
                   "speed": 30, "base_face": -1,
                   "forward_movement": {3: 2}},
    "uppercut": {"image": "resource/player2/player2_Uppercut.png",
                 "cols": 8, "w": 744, "h": 713, "scale": 0.55,
                 "speed": 15, "base_face": -1,
                 "forward_movement": {4: 4}},
    "rear_hand": {"image": "resource/player2/player2_RearHand.png",
                  "cols": 8, "w": 744, "h": 713, "scale": 0.55,
                  "speed": 22, "base_face": -1,
                  "forward_movement": {3: 3}},
    "blocking": {"image": "resource/player2/player2_Block.png",
                 "cols": 10, "w": 744, "h": 713, "scale": 0.55, "base_face": -1},
    "hurt": {"image": "resource/player2/player2_Hurt.png",
             "cols": 8, "w": 744, "h": 711, "scale": 0.55, "base_face": -1},
    "dizzy": {"image": "resource/player2/player2_Dizzy.png",
              "cols": 10, "w": 744, "h": 711, "scale": 0.55, "base_face": -1},
    "ko": {"image": "resource/player2/player2_KO.png",
           "cols": 8, "w": 744, "h": 711, "scale": 0.55, "base_face": -1}
}


# ============================================================
#  경기 상태 초기화 유틸
# ============================================================

def reset_match_state(reset_cpu: bool = False):
    """
    경기 전체(라운드/승수/게임오버)를 초기화하는 헬퍼.
    - GameOverUI나 ESC → 로비로 갈 때 재사용 가능.
    """
    global current_round, p1_wins, p2_wins, game_over_ui
    global cpu_mode, cpu_level, cpu_player

    current_round = 1
    p1_wins = 0
    p2_wins = 0
    game_over_ui = None

    if reset_cpu:
        cpu_mode = False
        cpu_level = None
        cpu_player = None


# ============================================================
#  라운드 종료 / 승패 처리
# ============================================================

def on_round_end(winner):
    """
    winner: 'p1', 'p2', None
    - None: 무승부, 라운드만 증가
    - 'p1' / 'p2': 해당 플레이어 승리, 승수 처리 후 하트/게임오버 판정
    """
    global p1_wins, p2_wins, current_round
    global round_intro, round_timer, game_over_ui, cpu_mode, cpu_player

    # ---------------------------
    # 승수 계산
    # ---------------------------
    if winner == 'p1':
        p1_wins += 1
    elif winner == 'p2':
        p2_wins += 1
    # 무승부일 때는 라운드만 증가
    else:
        current_round += 1
        if round_timer:
            round_timer.reset()
        is_final = (current_round == 3 and p1_wins == 1 and p2_wins == 1)
        if round_intro:
            round_intro.start(current_round, is_final=is_final)
        return

    # ---------------------------
    # 하트 UI 업데이트
    # ---------------------------
    p1_hearts = 2 - p2_wins
    p2_hearts = 2 - p1_wins
    heart_ui.set_hearts(p1_hearts, p2_hearts)

    # ---------------------------
    # 경기 종료 조건: 하트 0
    # ---------------------------
    match_over = (p1_hearts == 0 or p2_hearts == 0)
    if match_over:
        # ---- CPU 모드 ----
        if cpu_mode:
            # CPU가 P1이면 사용자는 P2, 반대면 반대로 계산
            if cpu_player == "P1":
                user_win = (winner == 'p2')
            else:
                user_win = (winner == 'p1')

            result = 'win' if user_win else 'lose'
            game_over_ui = GameOverUI(result=result, cpu_mode=True)
        else:
            # ---- PVP ----
            result = 'P1' if winner == 'p1' else 'P2'
            game_over_ui = GameOverUI(result=result, cpu_mode=False)
        return

    # ===========================
    #     경기 진행 중 (다음 라운드)
    # ===========================
    current_round += 1
    if round_timer:
        round_timer.reset()

    # Final Round 조건
    is_final = (current_round == 3 and p1_wins == 1 and p2_wins == 1)

    # 라운드 인트로 시작
    if round_intro:
        round_intro.start(current_round, is_final=is_final)


# ============================================================
#  초기화: 플레이어/월드/UI 세팅
# ============================================================

def _spawn_players():
    """
    p1, p2를 생성하고 cpu_mode 설정에 따라 AI를 붙인다.
    """
    global p1, p2

    cfg1 = P1 if p1_character == "P1" else P2
    cfg2 = P1 if p2_character == "P1" else P2

    p1 = Boxer(cfg1)
    p2 = Boxer(cfg2)
    p1.config_id = p1_character
    p2.config_id = p2_character

    # 서로 상대 지정
    p1.opponent = p2
    p2.opponent = p1

    # CPU 모드면 AI 활성화
    if cpu_mode:
        if cpu_player == "P1":
            p1.enable_ai(cpu_level)
        else:
            p2.enable_ai(cpu_level)

    # 월드에 등록
    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)
    game_world.add_collision_pair('body:block', p1, p2)  # 서로의 몸통 충돌


def _setup_ui():
    """
    HpUI / HeartUI / 상단 버튼들 설정.
    """
    global hpui, heart_ui, buttons

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    hpui = HpUi(p1, p2,
                x=screen_w // 2,
                y=int(screen_h * 0.92),
                scale=4)
    game_world.add_object(hpui, 2)

    heart_ui = HeartUI(
        x_p1=screen_w * 0.1,
        y_p1=screen_h * 0.15,
        x_p2=screen_w * 0.8,
        y_p2=screen_h * 0.15,
        scale=3.0
    )

    buttons = []

    pause_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Pause.png",
        x=screen_w // 2,
        y=int(screen_h * 0.97),
        scale=1.0,
        on_click=pause_game
    )
    gear_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Gear.png",
        x=screen_w // 2 + 60,
        y=int(screen_h * 0.97),
        scale=1.0,
        on_click=build_gear_menu
    )

    buttons.append(gear_btn)
    buttons.append(pause_btn)


def init():
    """
    play_mode 진입 시 호출되는 초기화 함수.
    - 월드 클리어
    - 링/플레이어/타이머/UI 세팅
    """
    global screen_w, screen_h
    global paused, gear_open
    global pause_ui, gear_ui
    global boxing_ring
    global round_timer, round_intro, game_over_ui

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    paused = False
    gear_open = False
    pause_ui = []
    gear_ui = []
    game_over_ui = None

    game_world.clear()

    # 배경(링) 추가
    boxing_ring = BoxingRing()
    game_world.add_object(boxing_ring, 0)

    # 플레이어 생성
    _spawn_players()

    # 라운드 타이머/인트로
    round_timer = RoundTimer()
    round_timer.reset()

    round_intro = RoundIntro(scale=0.5)
    round_intro.start(current_round, is_final=False)

    # UI 세팅
    _setup_ui()

    print("[DEBUG SETUP] p1 config_id =", p1.config_id)
    print("[DEBUG SETUP] p2 config_id =", p2.config_id)


# ============================================================
#  기어(옵션) 메뉴 / 일시정지 메뉴
# ============================================================

def build_gear_menu():
    global gear_open, gear_ui

    gear_open = True
    gear_ui = []

    cx = screen_w // 2
    cy = screen_h // 2
    spacing = 50
    btn_y = cy + 40

    close_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Cross.png",
        x=cx + 140, y=cy + 90,
        scale=1.0,
        on_click=close_gear_menu
    )

    sound_none_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-None.png",
        x=cx - spacing * 2, y=btn_y,
        scale=1.0,
        on_click=sound_none
    )
    sound_one_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-One.png",
        x=cx - spacing, y=btn_y,
        scale=1.0,
        on_click=sound_one
    )
    sound_two_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Two.png",
        x=cx, y=btn_y,
        scale=1.0,
        on_click=sound_two
    )
    sound_three_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Three.png",
        x=cx + spacing, y=btn_y,
        scale=1.0,
        on_click=sound_three
    )

    gear_ui = [
        sound_none_btn, sound_one_btn,
        sound_two_btn, sound_three_btn,
        close_btn
    ]


def build_pause_menu():
    global pause_ui

    resume_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row=7,
        x=screen_w // 2, y=int(screen_h * 0.8),
        scale=6,
        on_click=resume_game
    )
    main_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row=10,
        x=screen_w // 2, y=int(screen_h * 0.7),
        scale=6,
        on_click=go_to_main_menu
    )
    back_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row=1,
        x=screen_w // 2, y=int(screen_h * 0.55),
        scale=6,
        on_click=resume_game
    )

    pause_ui = [resume_btn, main_btn, back_btn]


def resume_game():
    global paused, pause_ui
    print("RESUME GAME")
    paused = False
    pause_ui.clear()


def pause_game():
    global paused
    print("GAME PAUSED")
    paused = True
    build_pause_menu()


def go_to_main_menu():
    """
    일시정지 메뉴에서 '메인으로' 선택 시 호출.
    CPU 모드 상태는 lobby_mode에서 다시 세팅하므로 여기서는 건드리지 않음.
    """
    print("MAIN MENU")
    game_framework.change_mode(lobby_mode)


def close_gear_menu():
    global gear_open, gear_ui
    gear_open = False
    gear_ui.clear()


# ============================================================
#  사운드 설정
# ============================================================

def sound_none():
    global sound_level
    sound_level = 0
    sound_manager.set_sfx_volume(sound_level)
    print("Sound: NONE")


def sound_one():
    global sound_level
    sound_level = 1
    sound_manager.set_sfx_volume(sound_level)
    print("Sound: ONE")


def sound_two():
    global sound_level
    sound_level = 2
    sound_manager.set_sfx_volume(sound_level)
    print("Sound: TWO")


def sound_three():
    global sound_level
    sound_level = 3
    sound_manager.set_sfx_volume(sound_level)
    print("Sound: THREE")


def draw_gear_popup_panel():
    # 중앙 패널 테두리
    w, h = 360, 220
    cx = screen_w // 2
    cy = screen_h // 2

    x1 = cx - w // 2
    y1 = cy - h // 2
    x2 = cx + w // 2
    y2 = cy + h // 2

    draw_rectangle(x1, y1, x2, y2)


# ============================================================
#  메인 업데이트 루프
# ============================================================

def update():
    """
    매 프레임 호출.
    - 라운드 인트로
    - 기어/일시정지 메뉴
    - 게임오버 체크
    - 평상시 게임 로직
    """
    global round_timer, game_over_ui

    # 1) 라운드 인트로 진행 중이면, 그쪽만 업데이트
    if not round_intro.is_done():
        round_intro.update(game_framework.frame_time)

        if round_intro.is_done():
            # 라운드 시작 준비
            p1.hp = p1.max_hp
            p2.hp = p2.max_hp

            p1.state_machine.cur_state = p1.IDLE
            p1.IDLE.enter(None)
            p2.state_machine.cur_state = p2.IDLE
            p2.IDLE.enter(None)

            p1.x = p1.cfg["spawn"]["x"]
            p1.y = p1.cfg["spawn"]["y"]
            p2.x = p2.cfg["spawn"]["x"]
            p2.y = p2.cfg["spawn"]["y"]

            round_timer.reset()
        return

    # 2) 버튼/기어/일시정지 UI 업데이트
    mx, my = mouse_get_pos()

    if gear_open:
        for b in gear_ui:
            b.update(mx, my)
        return

    if paused:
        for b in pause_ui:
            b.update(mx, my)
        return

    for b in buttons:
        b.update(mx, my)

    # 3) 게임오버면 캐릭터 업데이트 중지
    if game_over_ui:
        return

    # 4) 평상시 게임 로직
    game_world.update()
    heart_ui.update(game_framework.frame_time)
    round_timer.update(game_framework.frame_time)

    limit_boxer_in_boxing_ring(p1)
    limit_boxer_in_boxing_ring(p2)
    game_world.handle_collisions()

    # 5) 라운드 종료 조건 검사
    if p1.hp <= 0 and not getattr(p1, "on_ko_end", None):
        p1.on_ko_end = lambda: on_round_end("p2")
        return
    if p2.hp <= 0 and not getattr(p2, "on_ko_end", None):
        p2.on_ko_end = lambda: on_round_end("p1")
        return

    hpui.update()


# ============================================================
#  렌더링
# ============================================================

def draw():
    clear_canvas()
    game_world.render()

    round_timer.draw()
    round_intro.draw()

    for b in buttons:
        b.draw()

    hpui.draw()
    heart_ui.draw()

    if game_over_ui:
        game_over_ui.draw()

    if paused:
        for b in pause_ui:
            b.draw()

    if gear_open:
        draw_gear_popup_panel()
        for b in gear_ui:
            b.draw()

    if hitbox_edit.edit_mode:
        draw_rectangle(hitbox_edit.x1, hitbox_edit.y1,
                       hitbox_edit.x2, hitbox_edit.y2)

    update_canvas()


def finish():
    game_world.clear()


def pause():
    pass


def resume():
    pass


# ============================================================
#  이벤트 처리
# ============================================================

def handle_events():
    global paused, gear_open, game_over_ui
    global cpu_mode, cpu_level, cpu_player

    event_list = get_events()
    for event in event_list:
        # 게임오버 UI가 켜져 있으면 거기에 먼저 위임
        if game_over_ui:
            game_over_ui.handle_event(event)
            continue

        # 창 종료
        if event.type == SDL_QUIT:
            game_framework.quit()
            return

        # 디버그 리포트 토글
        if event.type == SDL_KEYDOWN and event.key == SDLK_F5:
            report_manager.toggle()

        # ESC 처리
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if gear_open:
                close_gear_menu()
            elif paused:
                resume_game()
            else:
                # 로비로 돌아갈 때는 CPU 모드까지 완전 초기화
                reset_match_state(reset_cpu=True)
                game_framework.change_mode(lobby_mode)
            return

        # 기어 메뉴가 열려 있으면 그쪽만 처리
        if gear_open:
            if event.type == SDL_MOUSEMOTION:
                mouse_update(event)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mx, my = mouse_get_pos()
                for b in gear_ui:
                    b.click(mx, my)
            continue

        # 일시정지 메뉴가 열려 있으면 그쪽만 처리
        if paused:
            if event.type == SDL_MOUSEMOTION:
                mouse_update(event)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mx, my = mouse_get_pos()
                for b in pause_ui:
                    b.click(mx, my)
            continue

        # 일반 버튼 처리
        if event.type == SDL_MOUSEMOTION:
            mouse_update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)

        # 기타 디버그 키
        if event.type == SDL_KEYDOWN and event.key == SDLK_F10:
            report_manager.print_report()
            continue

        if event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            hitbox_edit.edit_mode = not hitbox_edit.edit_mode
            print(f"Hitbox Edit Mode: {hitbox_edit.edit_mode}")
            return

        # 히트박스 에디터 모드이면 이벤트 넘기고 종료
        if hitbox_edit.edit_mode:
            if handle_hitbox_editor_event(event):
                return

        # 플레이어 입력 전달
        p1.handle_event(event)
        p2.handle_event(event)


# ============================================================
#  유틸 : 링 안에 플레이어 가두기 / 히트박스 에디터
# ============================================================

def limit_boxer_in_boxing_ring(boxer):
    w, h = get_canvas_width(), get_canvas_height()

    BOTTOM_LIMIT = 0
    TOP_LIMIT = h * 0.65
    LEFT_LIMIT = w * 0.05
    RIGHT_LIMIT = w * 0.95

    l, b, r, t = boxer.get_bb()
    center_to_bottom = boxer.y - b
    center_to_top = t - boxer.y
    center_to_left = boxer.x - l
    center_to_right = r - boxer.x

    min_y = BOTTOM_LIMIT + center_to_bottom
    max_y = TOP_LIMIT - center_to_top
    boxer.y = clamp(min_y, boxer.y, max_y)

    min_x = LEFT_LIMIT + center_to_left
    max_x = RIGHT_LIMIT - center_to_right
    boxer.x = clamp(min_x, boxer.x, max_x)


def handle_hitbox_editor_event(event):
    canvas_h = get_canvas_height()

    if event.type == SDL_MOUSEBUTTONDOWN:
        hitbox_edit.dragging = True
        hitbox_edit.x1 = event.x
        hitbox_edit.y1 = canvas_h - event.y
        hitbox_edit.x2 = hitbox_edit.x1
        hitbox_edit.y2 = hitbox_edit.y1
        return True

    elif event.type == SDL_MOUSEMOTION and hitbox_edit.dragging:
        hitbox_edit.x2 = event.x
        hitbox_edit.y2 = canvas_h - event.y
        return True

    elif event.type == SDL_MOUSEBUTTONUP:
        hitbox_edit.dragging = False
        return True

    if event.type == SDL_KEYDOWN and (event.key == SDLK_RETURN or event.key == SDLK_s):
        save_hitbox_for_current_frame()
        return True

    return False


def save_hitbox_for_current_frame():
    boxer = p1  # 편집 대상 플레이어 (필요하면 p2로 스위치 가능)
    frame = int(boxer.frame)
    scale = boxer.scale

    x1, y1 = hitbox_edit.x1, hitbox_edit.y1
    x2, y2 = hitbox_edit.x2, hitbox_edit.y2

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    # boxer 기준 상대 좌표
    ox = (cx - boxer.x) / scale
    oy = (cy - boxer.y) / scale
    w /= scale
    h /= scale

    print()
    print("==== HITBOX SAVED ====")
    print(f"{frame}: ({ox:.1f}, {oy:.1f}, {w:.1f}, {h:.1f})")
    print("=======================")
    print()
