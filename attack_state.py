from pico2d import get_time
import game_framework

class AttackState:
    def __init__(self, boxer, attack_type):
        self.b = boxer
        self.type = attack_type
        self.done = False
        self.spawned_frames = set()

    def enter(self, e):
        sheet = self.b.cfg[self.type]
        self.b.use_sheet(sheet)

        self.b.frame = 0
        self.done = False
        self.spawned_frames.clear()

        self.b.is_attacking = True
        self.b.current_attack_type = self.type

        self.hit_frames = sheet.get('hit_frames', [])

        self.b.last_attack_time = get_time()

    def exit(self, e):
        self.b.is_attacking = False
        self.b.current_attack_type = None

    def do(self):
        if self.done:
            return

        self.b.frame += self.b.FRAMES_PER_ACTION * self.b.ACTION_PER_TIME * game_framework.frame_time

        cur_frame = int(self.b.frame)

        if cur_frame in self.hit_frames and cur_frame not in self.spawned_frames:
            self.b.spawn_hitbox()
            self.spawned_frames.add(cur_frame)

        if self.b.frame >= self.b.cols:
            self.done = True
            self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        self.b.frame = float(self.b.frame)  # 안전장치 (optional)
        self.b.image.clip_draw(
            int(self.b.frame) * self.b.frame_w,
            0,
            self.b.frame_w,
            self.b.frame_h,
            self.b.x,
            self.b.y
        )

