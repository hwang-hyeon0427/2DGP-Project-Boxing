from pico2d import *
import game_world

class HitBox:
    def __init__(self, owner, offset_x, offset_y, w, h, duration):
        self.owner = owner          # 히트박스를 만든 주체(공격자)
        self.offset_x = offset_x    # x 오프셋(얼굴 방향 따라 +/-)
        self.offset_y = offset_y    # y 오프셋
        self.w = w                  # 히트박스 너비
        self.h = h                  # 히트박스 높이
        self.end_time = get_time() + duration  # 일정 시간 지나면 제거됨

    def draw(self):
        # 디버그용 바운딩박스
        draw_rectangle(*self.get_bb())

    def update(self):
        # 일정 시간이 지나면 자동 삭제
        if get_time() > self.end_time:
            game_world.remove_collision_object(self)

    def get_bb(self):
        # owner의 위치 + 오프셋 적용
        x = self.owner.x + self.offset_x
        y = self.owner.y + self.offset_y
        return (
            x - self.w / 2,
            y - self.h / 2,
            x + self.w / 2,
            y + self.h / 2
        )

    def handle_collision(self, group, other):
        # 충돌 시 HitBox 자체는 특별한 로직 없음
        # 피해 계산은 Boxer.handle_collision에서 처리함
        pass
