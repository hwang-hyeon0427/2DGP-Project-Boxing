from pico2d import *
from mouse import update as mouse_update
from mouse import get_pos as mouse_get_pos
import game_framework
import lobby_mode

class GameOverUI:
    def __init__(self, result, cpu_mode=False, scale=2.0, font_size=80):
        """
        result = 'p1' or 'p2'
        cpu_mode = True → player_win/player_lose png 사용
        """
        self.result = result
        self.cpu_mode = cpu_mode
        self.scale = scale
        self.font_size = font_size

        w, h = get_canvas_width(), get_canvas_height()
        self.cx = w // 2
        self.cy = h // 2 + 80

        # -------- CPU 모드 전용 이미지 --------
        if cpu_mode:
            self.player_win_img  = load_image('resource/image/win_txt.png')
            self.player_lose_img = load_image('resource/image/lose_txt.png')
            self.font = None

        else:
            # ---- PVP 전용 텍스트/PNG ----
            self.win_img  = load_image('resource/image/win_txt.png')
            self.lose_img = load_image('resource/image/lose_txt.png')
            self.font = load_font('ENCR10B.TTF', self.font_size)

        # ----- 버튼 생성 -----
        from button import SpriteSheetButton
        sheet = "resource/buttons_spritesheet_Photoroom.png"
        btn_y = self.cy - 140

        self.retry_btn = SpriteSheetButton(
            sheet,
            row=9,      # restart button
            x=self.cx,
            y=btn_y,
            scale=8,
            on_click=self.on_retry
        )

        self.lobby_btn = SpriteSheetButton(
            sheet,
            row=10,     # lobby button
            x=self.cx,
            y=btn_y - 140,
            scale=8,
            on_click=self.on_lobby
        )

        self.buttons = [self.retry_btn, self.lobby_btn]


    # ============================
    # 버튼 동작
    # ============================
    def on_retry(self):
        import play_mode
        play_mode.p1_wins = 0
        play_mode.p2_wins = 0
        play_mode.current_round = 1
        play_mode.game_over_ui = None
        game_framework.change_mode(play_mode)

    def on_lobby(self):
        import play_mode
        play_mode.p1_wins = 0
        play_mode.p2_wins = 0
        play_mode.current_round = 1
        play_mode.game_over_ui = None
        game_framework.change_mode(lobby_mode)


    # ============================
    # 입력 처리
    # ============================
    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            self.on_lobby()
            return

        if event.type == SDL_MOUSEMOTION:
            mouse_update(event)
            mx, my = mouse_get_pos()
            for b in self.buttons: b.update(mx, my)
            return

        if event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = mouse_get_pos()
            for b in self.buttons: b.click(mx, my)
            return


    # ============================
    # 그리기
    # ============================
    def draw(self):
        # ---------- CPU 모드 ----------
        if self.cpu_mode:
            # 플레이어가 이겼는지 졌는지 결과 판단
            is_player_win = (self.result == 'p1')  # P1이 사용자라는 의미
            img = self.player_win_img if is_player_win else self.player_lose_img

            w = int(img.w * self.scale)
            h = int(img.h * self.scale)
            img.draw(self.cx, self.cy, w, h)

        # ---------- PVP 모드 ----------
        else:
            if self.result == 'p1':
                txt = "P1 WIN"
                img = self.win_img
            else:
                txt = "P2 WIN"
                img = self.lose_img

            # 텍스트 모드 사용 → 폰트로 그리기
            if self.font:
                self.font.draw(self.cx - self.font_size * 2, self.cy, txt, (255,255,0))

        # 버튼 그리기
        for b in self.buttons:
            b.draw()
