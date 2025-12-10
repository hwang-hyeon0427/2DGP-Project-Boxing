import game_framework
from debug_manager import debug

# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        # 상태 진입 로그
        debug.state(
            f"IDLE ENTER: event={e}, move_keys={self.boxer.move_key_down}"
        )

        # xdir/ydir 리셋 로그
        debug.state(
            f"IDLE RESET DIR: from xdir={self.boxer.xdir}, ydir={self.boxer.ydir}"
        )

        # Idle 은 절대 자동 WALK로 복귀하지 않음
        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.use_sheet(self.boxer.cfg['idle'])

    def exit(self, e):
        # Idle은 별도의 exit 로그 필요 없음 (원하면 추가 가능)
        pass

    def do(self):
        # Idle 애니메이션 업데이트
        self.boxer.frame = (
            self.boxer.frame
            + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        ) % 10

        # 프레임 루프에서는 verbose 로그만 사용해야 성능 이슈 없음
        debug.state(
            f"IDLE DO: xdir={self.boxer.xdir}, ydir={self.boxer.ydir}, "
            f"x={self.boxer.x}, y={self.boxer.y}",
            verbose=True
        )

    def handle_event(self, e):
        # WALK 이벤트 처리
        if isinstance(e, tuple) and e[0] == 'WALK':
            debug.state("IDLE → WALK requested by WALK event")
            return self.boxer.WALK

    def draw(self):
        self.boxer.draw_current()
