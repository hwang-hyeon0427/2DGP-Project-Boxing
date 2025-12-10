from pico2d import *
import game_framework
import game_world
import play_mode
import levels_mode

from button import *
from boxing_ring import BoxingRing
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos
from play_mode import sound_none, sound_one, sound_two, sound_three


background = None
buttons = []


# ============================================================
#   INIT : 로비 초기화
# ============================================================
def init():
    global background, buttons
    global screen_w, screen_h

    game_world.clear()

    # 배경
    background = BoxingRing()
    game_world.add_object(background, 0)

    screen_w = get_canvas_width()
    screen_h = get_canvas_height()

    sheet = "resource/buttons_spritesheet_Photoroom.png"

    # --- CPU 모드 (Levels Mode)
    start_btn = SpriteSheetButton(
        sheet_path=sheet,
        row=9,
        x=400, y=300,
        scale=8,
        on_click=lambda: game_framework.change_mode(levels_mode)
    )

    # --- 2인 대전 모드
    two_player_btn = SpriteSheetButton(
        sheet_path=sheet,
        row=0,
        x=400, y=100,
        scale=8,
        on_click=start_two_player
    )

    # --- 사운드 버튼들
    music_on_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Music-On.png",
        x=screen_w - 170,
        y=screen_h * 0.1,
        scale=1.0,
        on_click=music_on
    )
    music_off_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Music-Off.png",
        x=screen_w - 100,
        y=screen_h * 0.1,
        scale=1.0,
        on_click=music_off
    )
    sound_none_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-None.png",
        x=screen_w - 250,
        y=screen_h * 0.2,
        scale=1.0,
        on_click=sound_none
    )
    sound_one_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-One.png",
        x=screen_w - 180,
        y=screen_h * 0.2,
        scale=1.0,
        on_click=sound_one
    )
    sound_two_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Two.png",
        x=screen_w - 110,
        y=screen_h * 0.2,
        scale=1.0,
        on_click=sound_two
    )
    sound_three_btn = Button(
        "resource\\Prinbles_YetAnotherIcons\\png\\White-Icon\\Sound-Three.png",
        x=screen_w - 40,
        y=screen_h * 0.2,
        scale=1.0,
        on_click=sound_three
    )

    # 버튼 등록
    buttons = [
        start_btn, two_player_btn,
        music_on_btn, music_off_btn,
        sound_none_btn, sound_one_btn, sound_two_btn, sound_three_btn
    ]


# ============================================================
#   2인 대전 시작 버튼 콜백
# ============================================================
def start_two_player():
    # play_mode 내부 전역변수 초기화
    from play_mode import cpu_mode, cpu_level, cpu_player
    cpu_mode = False
    cpu_level = None
    cpu_player = None

    # 2인 대전 모드로 진입
    game_framework.change_mode(play_mode)


# ============================================================
#   사운드 제어
# ============================================================
def music_on():
    sound_manager.play_bgm("hip-hop_music")
    print("BGM ON")

def music_off():
    sound_manager.stop_bgm("hip-hop_music")
    print("BGM OFF")


# ============================================================
#   업데이트 / 렌더링
# ============================================================
def update():
    mx, my = mouse_get_pos()
    for b in buttons:
        b.update(mx, my)
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    for b in buttons:
        b.draw()
    update_canvas()


# ============================================================
#   이벤트 처리
# ============================================================
def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_update(event)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in buttons:
                b.click(mx, my)


def finish(): pass
def pause(): pass
def resume(): pass
