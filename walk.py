# walk.py — DebugManager 적용 완료 버전

import game_framework
from debug_manager import debug

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


class Walk:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        self.boxer.frame = 0
        sheet = self.boxer.cfg.get('walk_forward')
        self.boxer.use_sheet(sheet)

        debug.state(
            f"WALK ENTER: event={e}, xdir={self.boxer.xdir}, ydir={self.boxer.ydir}"
        )

    def exit(self, e):
        self.boxer.dir = 0

    def do(self):
        # 애니메이션 진행
        self.boxer.frame = (
            self.boxer.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 10

        # 이동 계산
        old_x, old_y = self.boxer.x, self.boxer.y
        self.boxer.x += self.boxer.xdir * WALK_SPEED_PPS * game_framework.frame_time
        self.boxer.y += self.boxer.ydir * WALK_SPEED_PPS * game_framework.frame_time

        # verbose 이동 로그
        debug.move(
            f"WALK DO: pos=({old_x:.2f},{old_y:.2f}) → "
            f"({self.boxer.x:.2f},{self.boxer.y:.2f}), "
            f"xdir={self.boxer.xdir}, ydir={self.boxer.ydir}",
            verbose=True
        )

        # STOP 조건
        if self.boxer.xdir == 0 and self.boxer.ydir == 0:
            debug.state(
                f"WALK → STOP (xdir=0, ydir=0)"
            )
            self.boxer.state_machine.handle_state_event(('STOP', self.boxer.face_dir))

    def draw(self):
        self.boxer.draw_current()
