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


p1_character = "P1"
p2_character = "P2"
cpu_mode = False
cpu_level = None
cpu_player = None

round_timer = None
current_round = 1

game_over_ui = None

p1_wins = 0
p2_wins = 0


P1 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "wasd",
    "max_hp": 100,
    "bb": {"w": 0.40, "h": 0.555, "x_offset": 55, "y_offset": -30}, # 박스 크기 비율과 오프셋
    "idle":  {"image":"resource/player1/player1_Idle.png", "cols":10, "w":499, "h":489, "scale":1.0, "base_face": 1},
    "spawn": {"x": 300, "y": 300},
    "walk_backward": {"image":"resource/player1/player1_Walk_Backward.png", "cols": 10, "w": 499, "h": 489, "scale": 1.0},
    "walk_forward":  {"image":"resource/player1/player1_Walk_Forward.png",  "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "front_hand": {"image":"resource/player1/player1_FrontHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 1.0,"speed": 30, "base_face": 1, "forward_movement": {3 : 2}},
    "uppercut": {"image":"resource/player1/player1_Uppercut.png",  "cols": 7, "w": 499, "h": 489, "scale": 1.0,"speed": 15, "base_face": 1, "forward_movement": {4: 4}},
    "rear_hand": {"image":"resource/player1/player1_RearHand.png",  "cols": 6, "w": 499, "h": 489, "scale": 1.0,"speed": 22, "base_face": 1, "forward_movement": {3: 3}},
    "blocking": {"image":"resource/player1/player1_Blocking.png",  "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "hurt": {"image":"resource/player1/player1_Hurt.png",  "cols": 8, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "dizzy": {"image":"resource/player1/player1_Dizzy.png",  "cols": 8, "w": 499, "h": 489, "scale": 1.0, "base_face": 1},
    "ko": {"image":"resource/player1/player1_KO.png",  "cols": 10, "w": 499, "h": 489, "scale": 1.0, "base_face": 1}
}

P2 = {
    "face_map": {"left": -1, "right": 1},
    "controls": "arrows",
    "max_hp": 100,
    "bb": {"w": 0.555, "h": 0.7, "x_offset": -35, "y_offset": -20},
    "idle":  {"image":"resource/player2/player2_Idle.png", "cols":10, "w":744, "h":711, "scale":0.55, "base_face": -1},
    "spawn": {"x": 1800, "y": 300, "base_face": -1},
    "walk_backward": {"image":"resource/player2/player2_Walk_Backward.png", "cols": 10, "w":746, "h":713, "scale":0.55},
    "walk_forward":  {"image":"resource/player2/player2_Walk_Forward.png",  "cols": 10, "w":746, "h":713, "scale":0.55, "base_face": -1},
    "front_hand": {"image":"resource/player2/player2_FrontHand.png",  "cols": 8, "w":744, "h":713, "scale":0.55,"speed": 30, "base_face": -1, "forward_movement": {3 : 2}},
    "uppercut": {"image":"resource/player2/player2_Uppercut.png",  "cols": 8, "w":744, "h":713, "scale":0.55,"speed": 15, "base_face": -1, "forward_movement": {4: 4}},
    "rear_hand": {"image":"resource/player2/player2_RearHand.png",  "cols": 8, "w":744, "h":713, "scale":0.55,"speed": 22, "base_face": -1, "forward_movement": {3: 3}},
    "blocking": {"image":"resource/player2/player2_Block.png",  "cols": 10, "w":744, "h":713, "scale":0.55, "base_face": -1},
    "hurt": {"image":"resource/player2/player2_Hurt.png",  "cols": 8, "w":744, "h":711, "scale":0.55, "base_face": -1},
    "dizzy": {"image":"resource/player2/player2_Dizzy.png",  "cols": 10, "w":744, "h":711, "scale":0.55, "base_face": -1},
    "ko": {"image":"resource/player2/player2_KO.png",  "cols": 8, "w":744, "h":711, "scale":0.55, "base_face": -1}
}

buttons = []

paused = False
pause_ui = []

gear_open = False
gear_ui = []

sound_level = 0

def on_round_end(winner):
    global p1_wins, p2_wins, current_round
    global round_intro, round_timer
    global game_over_ui, cpu_mode, cpu_player

    # winner: 'p1', 'p2', None

    # ---------------------------
    # 승수 계산
    # ---------------------------
    if winner == 'p1':
        p1_wins += 1
    elif winner == 'p2':
        p2_wins += 1
    # 무승부일 때는 그냥 라운드만 증가
    else:
        current_round += 1
        round_timer.reset()
        is_final = (current_round == 3 and p1_wins == 1 and p2_wins == 1)
        round_intro.start(current_round, is_final=is_final)
        return

    # ---------------------------
    # 하트 UI 업데이트 (기존 구조 유지)
    # ---------------------------
    p1_hearts = 2 - p2_wins
    p2_hearts = 2 - p1_wins
    heart_ui.set_hearts(p1_hearts, p2_hearts)

    # ---------------------------
    # 경기 종료 조건: 하트 0
    # ---------------------------
    match_over = (p1_hearts == 0 or p2_hearts == 0)
    if match_over:
        if cpu_mode:
            # CPU가 P1이라면 사용자는 P2
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
    #     경기 진행 중 (라운드 이동)
    # ===========================
    current_round += 1
    round_timer.reset()

    # Final Round 조건
    is_final = (current_round == 3 and p1_wins == 1 and p2_wins == 1)

    # 라운드 인트로 시작
    round_intro.start(current_round, is_final=is_final)

def init():
    global p1, p2, hpui, boxing_ring
    global buttons, paused, pause_ui, gear_open, gear_ui
    global screen_w, screen_h
    global round_timer, round_intro
    global heart_ui

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    paused = False
    gear_open = False
    buttons = []
    pause_ui = []
    gear_ui = []

    game_world.clear()

    boxing_ring = BoxingRing()
    game_world.add_object(boxing_ring, 0)

    cfg1 = P1 if p1_character == "P1" else P2
    cfg2 = P1 if p2_character == "P1" else P2

    p1 = Boxer(cfg1)
    p2 = Boxer(cfg2)
    p1.config_id = p1_character
    p2.config_id = p2_character

    round_timer = RoundTimer()
    round_timer.reset()
    round_intro = RoundIntro(scale=0.5)
    round_intro.start(current_round, is_final=False)

    print("[DEBUG SETUP] p1 config_id =", p1.config_id)
    print("[DEBUG SETUP] p2 config_id =", p2.config_id)

    p1.opponent = p2
    p2.opponent = p1

    if cpu_mode:
        if cpu_player == "P1":
            p1.enable_ai(cpu_level)
        else:
            p2.enable_ai(cpu_level)

    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)
    game_world.add_collision_pair('body:block', p1, p2)

    hpui = HpUi(p1, p2, x = screen_w // 2, y = screen_h * 0.92, scale=4)
    game_world.add_object(hpui, 2)

    heart_ui = HeartUI(x_p1=screen_w * 0.1,
                       y_p1=screen_h * 0.15,
                       x_p2=screen_w * 0.8,
                       y_p2=screen_h * 0.15,
                       scale=3.0)

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    pause_btn = Button(
        "resource\Prinbles_YetAnotherIcons\png\White-Icon\Pause.png",
        x = screen_w // 2,
        y = screen_h * 0.97,
        scale=1.0,
        on_click=lambda: pause_game()
    )
    gear_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Gear.png",
        x = screen_w // 2 + 60,
        y = screen_h * 0.97,
        scale=1.0,
        on_click=lambda: build_gear_menu()
    )

    buttons.append(gear_btn)
    buttons.append(pause_btn)

    game_world.add_collision_pair('body:block', p1, p2) # 서로의 몸통끼리 충돌

def build_gear_menu():
    global gear_open, gear_ui, screen_w, screen_h

    gear_open = True
    gear_ui = []

    cx = screen_w // 2 # 중앙 x 위치
    cy = screen_h // 2 # 중앙 y 위치
    spacing = 50 # 버튼 간격
    btn_y = cy + 40 # 사운드 버튼 y 위치

    close_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Cross.png",
        x=cx + 140,
        y=cy + 90,
        scale=1.0,
        on_click=lambda: close_gear_menu()
    )

    sound_none_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-None.png",
        x=cx - spacing * 2,
        y=btn_y,
        scale=1.0,
        on_click = sound_none
    )
    sound_one_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-One.png",
        x=cx - spacing,
        y=btn_y,
        scale=1.0,
        on_click = sound_one
    )
    sound_two_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Two.png",
        x=cx,
        y=btn_y,
        scale=1.0,
        on_click = sound_two
    )
    sound_three_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Three.png",
        x=cx + spacing,
        y=btn_y,
        scale=1.0,
        on_click = sound_three
    )

    gear_ui = [sound_none_btn, sound_one_btn, sound_two_btn, sound_three_btn,
               close_btn
               ]

def build_pause_menu():
    global pause_ui, screen_w, screen_h

    resume_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 7,
        x = screen_w//2, y = screen_h * 0.8,
        scale=6,
        on_click = resume_game
    )
    main_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 10,
        x = screen_w//2, y = screen_h * 0.7,
        scale=6,
        on_click = go_to_main_menu
    )
    back_btn = SpriteSheetButton(
        "resource/buttons_spritesheet_Photoroom.png",
        row = 1 ,
        x = screen_w//2, y = screen_h * 0.55,
        scale=6,
        on_click = resume_game
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
    print("MAIN MENU")
    game_framework.change_mode(lobby_mode)

def close_gear_menu():
    global gear_open, gear_ui
    gear_open = False
    gear_ui.clear()

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
    # 중앙 흰색 패널 테두리
    w, h = 360, 220
    cx = screen_w // 2
    cy = screen_h // 2

    x1 = cx - w // 2
    y1 = cy - h // 2
    x2 = cx + w // 2
    y2 = cy + h // 2

    draw_rectangle(x1, y1, x2, y2)

def update():
    global round_timer, game_over_ui

    # -------------------------------------
    # 라운드 인트로(라운드걸 → fight → done)
    # -------------------------------------
    if not round_intro.is_done():
        round_intro.update(game_framework.frame_time)
        # round_intro가 끝나면 다음 라운드 준비 완료 상태
        if round_intro.is_done():
            p1.hp = p1.max_hp
            p2.hp = p2.max_hp

            # 만약 넉다운/기절 state가 끼어 있다면 idle로 초기화 필요
            p1.state_machine.cur_state = p1.IDLE
            p2.state_machine.cur_state = p2.IDLE

            p1.x = p1.cfg["spawn"]["x"]
            p1.y = p1.cfg["spawn"]["y"]

            p2.x = p2.cfg["spawn"]["x"]
            p2.y = p2.cfg["spawn"]["y"]

            # UI도 라운드별로 정리 가능h
            round_timer.reset()
        return

    # -------------------------------------
    # 버튼 업데이트 / 기어 / 일시정지
    # -------------------------------------
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

    # -------------------------------------
    # 게임오버 → 캐릭터 업데이트 중지
    # -------------------------------------
    if game_over_ui:
        return

    # -------------------------------------
    # 평상시 게임 로직
    # -------------------------------------
    game_world.update()
    heart_ui.update(game_framework.frame_time)
    round_timer.update(game_framework.frame_time)

    limit_boxer_in_boxing_ring(p1)
    limit_boxer_in_boxing_ring(p2)
    game_world.handle_collisions()

    # 라운드 종료 조건 검사
    if p1.hp <= 0:
        on_round_end("p2")
        return
    if p2.hp <= 0:
        on_round_end("p1")
        return

    hpui.update()

def finish():
    game_world.clear()

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
        draw_rectangle(hitbox_edit.x1, hitbox_edit.y1, hitbox_edit.x2, hitbox_edit.y2)

    update_canvas()

def pause(): pass
def resume(): pass

def handle_events():
    global paused, gear_open, game_over_ui

    event_list = get_events()
    for event in event_list:
        if game_over_ui:
            game_over_ui.handle_event(event)
            continue
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F5:
            report_manager.toggle()
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if gear_open:
                close_gear_menu()
            elif paused:
                resume_game()
            else:
                game_framework.change_mode(lobby_mode)
            return
        if gear_open:
            if event.type == SDL_MOUSEMOTION:
                mouse_update(event)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mx, my = mouse_get_pos()
                for b in gear_ui:
                    b.click(mx, my)
            continue
        if paused:
            if event.type == SDL_MOUSEMOTION:
                mouse_update(event)
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mx, my = mouse_get_pos()
                for b in pause_ui:
                    b.click(mx, my)
            continue

        if event.type == SDL_MOUSEMOTION:
            mouse_update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)

        if event.type == SDL_KEYDOWN and event.key == SDLK_F10:
            report_manager.print_report()
            continue
        if event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            hitbox_edit.edit_mode = not hitbox_edit.edit_mode
            print(f"Hitbox Edit Mode: {hitbox_edit.edit_mode}")
            return
        if hitbox_edit.edit_mode:
            if handle_hitbox_editor_event(event):
                return

        p1.handle_event(event)
        p2.handle_event(event)

def limit_boxer_in_boxing_ring(boxer):
    w, h = get_canvas_width(), get_canvas_height()

    BOTTOM_LIMIT = 0 # 바닥
    TOP_LIMIT = h * 0.65 # 최상단 로프
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

        # 중요! 드래그 시작 시 x2,y2 초기화
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
    boxer = p1  # 편집할 플레이어 선택 (p1/p2 스위치 가능)
    frame = int(boxer.frame)
    scale = boxer.scale

    # 드래그한 박스
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
