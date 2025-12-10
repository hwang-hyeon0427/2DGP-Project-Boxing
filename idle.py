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
        log(DEBUG_EVENT,
            f"[ENTER] Idle: reset xdir/ydir from {self.boxer.xdir}, {self.boxer.ydir}")

        from_attack = (isinstance(e, tuple) and e[0] == 'ATTACK_END')

        if from_attack:
            key_map = self.boxer.move_key_down

            xdir = 0
            ydir = 0
            if key_map['left'] and not key_map['right']:
                xdir = -1
            elif key_map['right'] and not key_map['left']:
                xdir = 1

            if key_map['up'] and not key_map['down']:
                ydir = 1
            elif key_map['down'] and not key_map['up']:
                ydir = -1

            if xdir != 0 or ydir != 0:
                self.boxer.xdir = xdir
                self.boxer.ydir = ydir
                if xdir != 0:
                    self.boxer.face_dir = xdir

                log(DEBUG_EVENT, f"[RESUME MOVE] Idle → WALK xdir={xdir}, ydir={ydir} after ATTACK_END")
                self.boxer.state_machine.handle_state_event(('WALK', None))
                return

        self.boxer.xdir = 0
        self.boxer.ydir = 0
        self.boxer.input_buffer.clear()
        self.boxer.use_sheet(self.boxer.cfg['idle'])

    def exit(self, e):
        pass

    def do(self):
        self.boxer.frame = ( self.boxer.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        log(DEBUG_STATE,f"[WALK DO] xdir={self.boxer.xdir}, ydir={self.boxer.ydir}, x={self.boxer.x}, y={self.boxer.y}")

    def handle_event(self, e):
        if isinstance(e, tuple) and e[0] == 'WALK':
            return self.boxer.WALK

    def draw(self):
        self.boxer.draw_current()