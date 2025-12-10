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
        # Idle 상태로 진입했을 때 로그 출력 (xdir, ydir 초기화 상태 확인용)
        log(DEBUG_EVENT,
            f"[ENTER] Idle: reset xdir/ydir from {self.boxer.xdir}, {self.boxer.ydir}")

        # ATTACK_END 이벤트로 진입한 경우만 이동 재개 로직 수행
        from_attack = (isinstance(e, tuple) and e[0] == 'ATTACK_END')

        if from_attack:
            key_map = self.boxer.move_key_down # 현재 눌린 방향키 상태 조회

            xdir = 0
            ydir = 0
            # 좌우 이동 방향 결정
            if key_map['left'] and not key_map['right']:
                xdir = -1
            elif key_map['right'] and not key_map['left']:
                xdir = 1

            # 상하 이동 방향 결정
            if key_map['up'] and not key_map['down']:
                ydir = 1
            elif key_map['down'] and not key_map['up']:
                ydir = -1

            # 눌린 이동키가 있다면 WALK 상태로 전이
            if xdir != 0 or ydir != 0:
                self.boxer.xdir = xdir
                self.boxer.ydir = ydir
                # 좌우 이동이면 face_dir도 같이 설정
                if xdir != 0:
                    self.boxer.face_dir = xdir

                # ✅ 상태머신에 WALK 상태 전이 요청
                self.boxer.state_machine.handle_state_event(('WALK', None))
                log(DEBUG_EVENT, f"[RESUME MOVE] Idle→Walk xdir={xdir}, ydir={ydir} after ATTACK_END")
                return

        # 기본 Idle 진입 로직: 방향 초기화 + 공격 입력 초기화 + idle 이미지 사용
        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.input_buffer.clear()
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