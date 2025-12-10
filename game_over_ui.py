from pico2d import *
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos
import game_framework
import lobby_mode


class GameOverUI:
    def __init__(self, result, cpu_mode=False, scale=2.0, font_size=80):
        """
        result:
            CPU 모드 → 'win' or 'lose'
            PVP 모드 → 'P1' or 'P2'
        """
        self.result = result
        self.cpu_mode = cpu_mode
        self.scale = scale
        self.font_size = font_size

        w, h = get_canvas_width(), get_canvas_height()
        self.cx = w // 2
        self.cy = h // 2 + 80

        # ------------ 자원 로드 ------------
        if cpu_mode:
            self.player_win_img  = load_image('resource/image/win_txt.png')
            self.player_lose_img = load_image('resource/image/lose_txt.png')
        else:
            self.font = load_font('ENCR10B.TTF', self.font_size)

        # ------------ 버튼 생성 ------------
        from button import SpriteSheetButton
        sheet = "resource/buttons_spritesheet_Photoroom.png"
        btn_y = self.cy - 150

        self.retry_btn = SpriteSheetButton(
            sheet,
            row=9,
            x=self.cx,
            y=btn_y,
            scale=8,
            on_click=self.on_retry
        )
        self.lobby_btn = SpriteSheetButton(
            sheet,
            row=10,
            x=self.cx,
            y=btn_y - 150,
            scale=8,
            on_click=self.on_lobby
        )

        self.buttons = [self.retry_btn, self.lobby_btn]


    # ============================================================
    #   내부 유틸 — CPU / PVP 상태 초기화
    # ============================================================
    def reset_match_state(self, reset_cpu=False):
        import play_mode

        play_mode.p1_wins = 0
        play_mode.p2_wins = 0
        play_mode.current_round = 1
        play_mode.game_over_ui = None

        # -------- CPU 관련 초기화 --------
        if reset_cpu:
            play_mode.cpu_mode = False
            play_mode.cpu_level = None
            play_mode.cpu_player = None


    # ============================================================
    #   버튼 동작
    # ============================================================
    def on_retry(self):
        import play_mode

        # CPU 모드였으면 CPU 유지
        # PVP였으면 CPU 완전 OFF
        self.reset_match_state(reset_cpu=not self.cpu_mode)

        game_framework.change_mode(play_mode)

    def on_lobby(self):
        # 로비로 돌아갈 때는 항상 플레이어 선택이므로 CPU OFF가 자연스럽다.
        self.reset_match_state(reset_cpu=True)

        game_framework.change_mode(lobby_mode)


    # ============================================================
    #   입력 처리
    # ============================================================
    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            self.on_lobby()
            return

        if event.type == SDL_MOUSEMOTION:
            mouse_update(event)
            mx, my = mouse_get_pos()
            for b in self.buttons:
                b.update(mx, my)
            return

        if event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in self.buttons:
                b.click(mx, my)
            return


    # ============================================================
    #   그리기
    # ============================================================
    def draw(self):
        # ---------- CPU 모드 ----------
        if self.cpu_mode:
            is_player_win = (self.result == 'win')
            img = self.player_win_img if is_player_win else self.player_lose_img
            img.draw(self.cx, self.cy, img.w * self.scale, img.h * self.scale)

        # ---------- PVP 모드 ----------
        else:
            txt = "P1 WIN" if self.result == 'P1' else "P2 WIN"
            self.font.draw(self.cx - self.font_size * 2, self.cy, txt, (255, 255, 0))

        # ---------- 버튼 ----------
        for b in self.buttons:
            b.draw()
