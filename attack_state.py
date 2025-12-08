import game_framework
from pico2d import *
from hitbox_data import HITBOX_DATA

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

        # ★ 공격별 속도 적용
        attack_speed = self.boxer.cfg[self.attack_type].get("speed", 20)
        frame_speed = attack_speed * game_framework.frame_time

        # 프레임 증가 (1번만)
        self.boxer.frame += frame_speed
        cur_frame = int(self.boxer.frame)

        # === 히트박스 처리 ===
        hitbox_info = HITBOX_DATA[self.boxer.controls][self.attack_type]

        if cur_frame in hitbox_info and cur_frame not in self.spawned_frames:
            self.boxer.spawn_hitbox()
            self.spawned_frames.add(cur_frame)

        # === 전진 이동 ===
        forward_date = self.boxer.cfg[self.attack_type].get("forward_movement", {})
        if cur_frame in forward_date:
            move = forward_date[cur_frame]
            self.boxer.x += move * self.boxer.face_dir

        # === 공격 종료 ===
        if cur_frame >= self.total_frames:
            self.done = True

            # 1) 버퍼에 공격이 남아 있으면 바로 다음 공격 실행 (Idle 금지)
            if self.boxer.attack_router.has_buffer():
                next_attack = self.boxer.attack_router.pop_buffer()

                # 공격 체인: Idle로 가지 않고 바로 AttackState 다시 시작
                self.boxer.state_machine.handle_state_event(('ATTACK', next_attack))
                return

            # 2) 버퍼가 없으면 Idle로 이동
            self.boxer.state_machine.handle_state_event(('ATTACK_END', None))
            return

    def draw(self):
        self.boxer.draw_current()
