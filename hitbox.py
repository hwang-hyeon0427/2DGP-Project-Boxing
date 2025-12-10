# hitbox.py — DebugManager 적용 버전

from pico2d import *
import game_world
import report_manager
from debug_manager import debug  # ★ DebugManager 사용

_DEBUG_FONT = None


class HitBox:
    def __init__(self, owner, frame_offsets, duration=0.15):
        # 기본 정보 저장
        self.owner = owner
        self.frame_offsets = frame_offsets  # {frame:(ox,oy,w,h)}
        self.end_time = get_time() + duration

        attack_name = getattr(owner, "current_attack_type", None)
        frame_idx = int(getattr(owner, "frame", -1))

        # Debug: 히트박스 생성 정보
        debug.hitbox(
            f"HITBOX INIT: owner={owner.controls if hasattr(owner, 'controls') else None}, "
            f"attack={attack_name}, frame={frame_idx}"
        )

        # 공격 상태가 아닌 경우 기록하지 않음
        if attack_name is None or frame_idx < 0:
            return

        # P1/P2 여부 확인
        player_id = getattr(owner, "config_id", "").strip()
        if player_id not in ("P1", "P2"):
            return

        # Debug: 프레임 체크
        debug.hitbox(
            f"FRAME CHECK: attack={attack_name}, frame={frame_idx}, "
            f"offset_keys={list(frame_offsets.keys()) if frame_offsets else None}"
        )

        # 해당 프레임에 대한 히트박스 데이터가 있는 경우
        if frame_offsets and frame_idx in frame_offsets:
            ox, oy, w, h = frame_offsets[frame_idx]
            scale = getattr(owner, "scale", 1.0)
            face = getattr(owner, "face_dir", 1)

            # 스케일과 방향 적용
            ox *= scale
            oy *= scale

            hb_x = owner.x + ox * face
            distance = abs(hb_x - owner.x)

            # 기록
            report_manager.record_hitbox(attack_name, frame_idx, player_id, distance)

            debug.hitbox(
                f"RECORD HITBOX: attack={attack_name}, frame={frame_idx}, "
                f"player={player_id}, distance={distance}"
            )

    # ----------------------------
    # 매 프레임 업데이트
    # ----------------------------
    def update(self):
        # 지속시간이 끝나면 제거
        if get_time() > self.end_time:
            debug.hitbox("HITBOX EXPIRED → removing hitbox")
            game_world.remove_collision_object(self)

    # ----------------------------
    # 히트박스 렌더링
    # ----------------------------
    def draw(self):
        l, b, r, t = self.get_bb()
        # draw_rectangle(l, b, r, t)

        owner_x = self.owner.x
        owner_y = self.owner.y

        hb_center_x = (l + r) / 2
        hb_center_y = (b + t) / 2

        draw_line(owner_x, owner_y, hb_center_x, hb_center_y)

        global _DEBUG_FONT
        if _DEBUG_FONT is None:
            _DEBUG_FONT = load_font('ENCR10B.TTF', 20)

        attack_name = getattr(self.owner, "current_attack_type", "None")
        frame_idx = int(getattr(self.owner, "frame", 0))

        debug_text = f"{attack_name} | frame {frame_idx}"
        _DEBUG_FONT.draw(hb_center_x + 10, hb_center_y + 10, debug_text, (255, 0, 0))

    # ----------------------------
    # 히트박스 좌표 계산
    # ----------------------------
    def get_bb(self):
        scale = getattr(self.owner, "scale", 1.0)
        face = getattr(self.owner, "face_dir", 1)
        frame = int(self.owner.frame)

        if self.frame_offsets and frame in self.frame_offsets:
            ox, oy, w, h = self.frame_offsets[frame]

            ox *= scale
            oy *= scale
            w *= scale
            h *= scale

            x = self.owner.x + ox * face
            y = self.owner.y + oy

            return (
                x - w / 2,
                y - h / 2,
                x + w / 2,
                y + h / 2
            )

        return (self.owner.x, self.owner.y, self.owner.x, self.owner.y)

    # ----------------------------
    # 충돌 처리 (상대쪽 캐릭터로 위임)
    # ----------------------------
    def handle_collision(self, group, other):
        debug.collision(
            f"HITBOX COLLISION: group={group}, other={other}"
        )
        other.handle_collision(group, self)
