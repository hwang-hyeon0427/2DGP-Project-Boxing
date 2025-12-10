# attack_state.py — DebugManager 적용 완료 버전

import game_framework
from pico2d import *
from hitbox_data import HITBOX_DATA
from debug_manager import debug


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

        # 공격 시작 로그
        debug.attack(
            f"ATTACK ENTER: type={self.attack_type}, "
            f"event={e}, total_frames={self.total_frames}"
        )

    def exit(self, e):
        # 공격 상태 종료
        debug.attack(
            f"ATTACK EXIT: type={self.attack_type}, event={e}"
        )

        self.boxer.current_attack_type = None
        self.boxer.is_attacking = False  # 공격 상태 종료

        # 공격키는 공격이 끝나면 무조건 눌리지 않은 것으로 간주
        for k in self.boxer.attack_key_down:
            self.boxer.attack_key_down[k] = False

        # 공격 이후 이동 재개
        self.boxer.resume_move_after_action()

    def do(self):
        if self.done:
            return

        # ★ 공격별 속도 적용
        attack_speed = self.boxer.cfg[self.attack_type].get("speed", 20)
        frame_speed = attack_speed * game_framework.frame_time

        # 프레임 증가
        prev_frame = int(self.boxer.frame)
        self.boxer.frame += frame_speed
        cur_frame = int(self.boxer.frame)

        # verbose 프레임 로그
        debug.attack(
            f"ATTACK DO: type={self.attack_type}, frame={cur_frame}, prev_frame={prev_frame}, "
            f"speed={attack_speed}",
            verbose=True
        )

        # === 히트박스 처리 ===
        hitbox_info = HITBOX_DATA[self.boxer.controls][self.attack_type]

        if cur_frame in hitbox_info and cur_frame not in self.spawned_frames:
            debug.hitbox(
                f"HITBOX SPAWN: type={self.attack_type}, frame={cur_frame}"
            )
            self.boxer.spawn_hitbox()
            self.spawned_frames.add(cur_frame)

        # === 전진 이동 ===
        forward_data = self.boxer.cfg[self.attack_type].get("forward_movement", {})
        if cur_frame in forward_data:
            move = forward_data[cur_frame]
            old_x = self.boxer.x
            self.boxer.x += move * self.boxer.face_dir

            debug.attack(
                f"ATTACK MOVE: type={self.attack_type}, frame={cur_frame}, "
                f"x={old_x:.2f}→{self.boxer.x:.2f}, move={move}, face_dir={self.boxer.face_dir}"
            )

        # === 공격 종료 ===
        if cur_frame >= self.total_frames:
            self.done = True
            debug.attack(
                f"ATTACK FINISH: type={self.attack_type}, final_frame={cur_frame}"
            )

            # 1) 버퍼에 공격이 남아 있으면 바로 다음 공격 실행 (Idle 금지)
            if self.boxer.input_buffer:
                now = get_time()
                if now - self.boxer.last_input_time <= self.boxer.buffer_time:
                    next_attack = self.boxer.input_buffer.pop(0)
                    debug.buffer(
                        f"BUFFERED ATTACK: from={self.attack_type} → next={next_attack}"
                    )
                    self.boxer.state_machine.handle_state_event(('ATTACK', next_attack))
                    return
                else:
                    # 버퍼 있지만 시간 초과
                    debug.buffer(
                        f"BUFFER EXPIRED: type={self.attack_type}, "
                        f"now={now:.3f}, last={self.boxer.last_input_time:.3f}, "
                        f"buffer_time={self.boxer.buffer_time}"
                    )

            # 2) 이동키도 없으면 Idle로 이동 (FSM에 공격 종료 알림)
            debug.attack(
                f"ATTACK_END EVENT SEND: type={self.attack_type}"
            )
            self.boxer.state_machine.handle_state_event(('ATTACK_END', None))
            return

    def draw(self):
        self.boxer.draw_current()
