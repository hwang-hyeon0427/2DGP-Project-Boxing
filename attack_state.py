import game_framework

class AttackState:
    def __init__(self, boxer, attack_type):
        """attack_type: 'front_hand', 'rear_hand', 'uppercut'"""
        self.boxer = boxer
        self.attack_type = attack_type

        self.done = False
        self.total_frames = 0
        self.hit_frames = []
        self.spawned_frames = set()

    def enter(self, e):
        sheet = self.boxer.cfg[self.attack_type]
        self.boxer.use_sheet(sheet)

        self.boxer.frame = 0
        self.done = False
        self.spawned_frames.clear()

        self.total_frames = sheet['cols']
        self.hit_frames = sheet.get('hit_frames', [])

        self.boxer.current_attack_type = self.attack_type
        self.boxer.is_attacking = True

    def exit(self, e):
        self.boxer.current_attack_type = None
        self.boxer.is_attacking = False

    def do(self):
        if self.done:
            return

        # ★ 프레임 속도 (초당 10프레임 재생 정도)
        frame_speed = 10 * game_framework.frame_time

        # 프레임 증가
        self.boxer.frame += frame_speed
        cur_frame = int(self.boxer.frame)

        # ★ HITBOX_DATA 기반 hit frame 처리
        from hitbox_data import HITBOX_DATA
        hitbox_info = HITBOX_DATA[self.boxer.controls][self.attack_type]

        if cur_frame in hitbox_info and cur_frame not in self.spawned_frames:
            self.boxer.spawn_hitbox()
            self.spawned_frames.add(cur_frame)

        # 애니메이션 종료
        if cur_frame >= self.total_frames:
            self.done = True
            self.boxer.state_machine.handle_state_event(('STOP', None))

    def draw(self):
        self.boxer.draw_current()
