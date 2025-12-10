import game_framework
from debug_manager import log, DEBUG_EVENT, DEBUG_STATE


# Boxer Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        log(DEBUG_EVENT, f"[IDLE ENTER] e={e}, move_keys={self.boxer.move_key_down}")
        log(DEBUG_EVENT, f"[ENTER] Idle: reset xdir/ydir from {self.boxer.xdir}, {self.boxer.ydir}")

        # Idle 은 절대 자동으로 WALK 로 복귀하지 않는다.
        # (공격 후 이동 복귀는 resume_move_after_action() 이 단독으로 수행)

        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.use_sheet(self.boxer.cfg['idle'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        # 현재 상태 로그 출력
        if DEBUG_STATE:
            log(DEBUG_STATE,
                f"[IDLE DO] xdir={self.boxer.xdir}, ydir={self.boxer.ydir}, x={self.boxer.x}, y={self.boxer.y}")

    def handle_event(self, e):
        # WALK 이벤트가 들어오면 WALK 상태로 전이 요청
        if isinstance(e, tuple) and e[0] == 'WALK':
            return self.boxer.WALK

    def draw(self):
        self.boxer.draw_current()