import game_framework

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


class BlockExit:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        print("[ENTER] BlockExit: force stop movement")

        # 이동 중지
        self.boxer.xdir = 0
        self.boxer.ydir = 0

        # BlockExit 상태 직후 첫 KEYUP 무시
        self.boxer.ignore_next_move_keyup = True

        # blocking 이미지에서 역순으로 재생
        self.boxer.use_sheet(self.boxer.cfg['blocking'])
        self.boxer.frame = self.boxer.cols - 1

    def exit(self, e):
        # ★ 중요: 반드시 self.boxer 사용
        self.boxer.resume_move_after_action()

    def do(self):
        # 프레임 감소하여 역재생
        self.boxer.frame -= FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

        # 종료 조건
        if self.boxer.frame <= 0:
            self.boxer.frame = 0
            self.boxer.state_machine.handle_state_event(('BLOCK_EXIT_DONE', None))

    def draw(self):
        self.boxer.draw_current()
