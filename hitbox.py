# hitbox.py — DebugManager 개선 + 구조 정리 버전

from pico2d import *
import game_world
import report_manager
from debug_manager import debug   # DebugManager 사용

_DEBUG_FONT = None

# -------------------------------------
# Debug 시각화 옵션 (원하면 켜서 사용)
# -------------------------------------
DEBUG_DRAW_HITBOX = False      # 히트박스 사각형 표시
DEBUG_DRAW_LABEL = False       # 공격명/프레임 텍스트 표시


class HitBox:
    def __init__(self, owner, frame_offsets, duration=0.15):
        self.owner = owner
        self.frame_offsets = frame_offsets      # {frame:(ox,oy,w,h)}
        self.end_time = get_time() + duration

        attack = getattr(owner, "current_attack_type", None)
        frame = int(getattr(owner, "frame", -1))

        # Debug: 생성 로그
        debug.hitbox(
            f"INIT | owner={getattr(owner, 'controls', None)}, "
            f"attack={attack}, frame={frame}"
        )

        # 공격 상태 아님 → 기록 X
        if attack is None or frame < 0:
            return

        # P1/P2 여부
        player_id = getattr(owner, "config_id", "").strip()
        if player_id not in ("P1", "P2"):
            return

        # 현재 프레임에 hitbox 정보가 존재할 때만 기록
        if frame_offsets and frame in frame_offsets:
            ox, oy, w, h = frame_offsets[frame]

            scale = owner.scale
            face = owner.face_dir

            # hitbox 중심 x 좌표 (거리 계산용)
            hb_x = owner.x + (ox * scale * face)
            distance = abs(hb_x - owner.x)

            report_manager.record_hitbox(attack, frame, player_id, distance)

            debug.hitbox(
                f"RECORD | attack={attack}, frame={frame}, "
                f"player={player_id}, distance={distance}"
            )

    # ----------------------------
    # 생존 시간 체크
    # ----------------------------
    def update(self):
        if get_time() > self.end_time:
            debug.hitbox("EXPIRE → removing hitbox")
            game_world.remove_collision_object(self)

    # ----------------------------
    # Debug 전용 draw()
    # ----------------------------
    def draw(self):
        if not (DEBUG_DRAW_HITBOX or DEBUG_DRAW_LABEL):
            return  # 시각화 비활성화 시 완전 무시

        l, b, r, t = self.get_bb()

        # 히트박스 사각형
        if DEBUG_DRAW_HITBOX:
            draw_rectangle(l, b, r, t)

        # 텍스트 (공격명 / 프레임)
        if DEBUG_DRAW_LABEL:
            global _DEBUG_FONT
            if _DEBUG_FONT is None:
                _DEBUG_FONT = load_font('ENCR10B.TTF', 20)

            attack = getattr(self.owner, "current_attack_type", "None")
            frame = int(getattr(self.owner, "frame", 0))

            cx = (l + r) / 2
            cy = (b + t) / 2
            _DEBUG_FONT.draw(cx + 10, cy + 10, f"{attack} | {frame}", (255, 0, 0))

    # ----------------------------
    # 히트박스 좌표 계산
    # ----------------------------
    def get_bb(self):
        frame = int(self.owner.frame)
        scale = self.owner.scale
        face = self.owner.face_dir

        if self.frame_offsets and frame in self.frame_offsets:
            ox, oy, w, h = self.frame_offsets[frame]

            ox *= scale
            oy *= scale
            w *= scale
            h *= scale

            cx = self.owner.x + ox * face
            cy = self.owner.y + oy

            return (
                cx - w / 2,
                cy - h / 2,
                cx + w / 2,
                cy + h / 2
            )

        # 기본값 (프레임에 hitbox 없을 때)
        return (self.owner.x, self.owner.y, self.owner.x, self.owner.y)

    # ----------------------------
    # 충돌 처리 (상대에게 전달)
    # ----------------------------
    def handle_collision(self, group, other):
        debug.collision(
            f"HITBOX COLLISION | group={group}, "
            f"self_owner={getattr(self.owner,'config_id',None)}, "
            f"other_owner={getattr(other,'config_id',None)}"
        )
        other.handle_collision(group, self)
