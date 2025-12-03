from pico2d import *
import game_world


class HitBox:
    def __init__(self, owner, frame_offsets, duration=0.15):
        self.owner = owner
        self.frame_offsets = frame_offsets    # {frame: (ox, oy, w, h)}
        self.end_time = get_time() + duration

    def update(self):
        # 히트박스 지속시간 지나면 제거
        if get_time() > self.end_time:
            game_world.remove_collision_object(self)

    def draw(self):
        print("HITBOX DRAW")
        draw_rectangle(*self.get_bb())

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
        pass
