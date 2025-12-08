from pico2d import *
import game_world
import report_manager

_DEBUG_FONT = None
compare_buffer = {}   # 예: { ("front_hand", 4): {"P1": 거리값, "P2": 거리값} }

class HitBox:
    def __init__(self, owner, frame_offsets, duration=0.15):
        print("[DEBUG HITBOX OWNER]", owner, "config_id=", getattr(owner, "config_id", None),
              "controls=", owner.controls if hasattr(owner, "controls") else None)

        self.owner = owner
        self.frame_offsets = frame_offsets    # {frame: (ox, oy, w, h)}
        self.end_time = get_time() + duration

        attack_name = getattr(owner, "current_attack_type", None)
        frame_idx = int(getattr(owner, "frame", -1))

        if attack_name is None or frame_idx < 0:
            return  # 공격이 아닌 프레임은 기록하지 않음

        player_id = getattr(owner, "config_id", "")
        player_id = player_id.strip()  # ★ 공백 제거

        if player_id not in ("P1", "P2"):
            return

        print("[DEBUG FRAME CHECK]", "attack =", attack_name, "frame_idx =", frame_idx, "offset keys =",
              list(frame_offsets.keys()) if frame_offsets else None)

        # 히트박스 데이터 존재 여부
        if frame_offsets and frame_idx in frame_offsets:
            ox, oy, w, h = frame_offsets[frame_idx]
            scale = getattr(owner, "scale", 1.0)
            face = getattr(owner, "face_dir", 1)

            # 스케일 적용
            ox *= scale
            oy *= scale

            # 실제 중심 계산
            hb_x = owner.x + ox * face
            distance = abs(hb_x - owner.x)

            # 기록
            report_manager.record_hitbox(attack_name, frame_idx, player_id, distance)

    def update(self):
        # 히트박스 지속시간 지나면 제거
        if get_time() > self.end_time:
            game_world.remove_collision_object(self)

    def draw(self):
        l, b, r, t = self.get_bb()
        draw_rectangle(l, b, r, t)

        owner_x = self.owner.x
        owner_y = self.owner.y

        hb_center_x = (l + r) / 2
        hb_center_y = (b + t) / 2

        draw_line(owner_x, owner_y, hb_center_x, hb_center_y)

        global _DEBUG_FONT
        if _DEBUG_FONT is None:
            _DEBUG_FONT = load_font('ENCR10B.TTF', 20)  # 존재하는 폰트 사용

        attack_name = getattr(self.owner, "current_attack_type", "None")
        frame_idx = int(getattr(self.owner, "frame", 0))

        debug_text = f"{attack_name} | frame {frame_idx}"
        _DEBUG_FONT.draw(hb_center_x + 10, hb_center_y + 10, debug_text, (255, 0, 0))

    def get_bb(self):
        scale = getattr(self.owner, "scale", 1.0)
        face = getattr(self.owner, "face_dir", 1)

        frame = int(self.owner.frame)

        if self.frame_offsets and frame in self.frame_offsets:
            ox, oy, w, h = self.frame_offsets[frame]

            # 스케일 적용
            ox *= scale
            oy *= scale
            w *= scale
            h *= scale

            # 방향 반전 적용
            x = self.owner.x + ox * face
            y = self.owner.y + oy

            return (
                x - w / 2,
                y - h / 2,
                x + w / 2,
                y + h / 2
            )

        # 프레임 데이터가 없다면 기본 0(있을 일 거의 없음)
        return (self.owner.x, self.owner.y, self.owner.x, self.owner.y)

    def handle_collision(self, group, other):
        other.handle_collision(group, self)
