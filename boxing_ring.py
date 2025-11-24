from pico2d import *
import random
import game_framework  # ← frame_time 쓰려고

class BoxingRing:
    FRAME_W = 317
    FRAME_H = 128
    TOTAL_FRAMES = 4

    def __init__(self):
        bg_list = [
            'background/Boxing_Ring_Blue.png',
            'background/Boxing_Ring_Green.png',
            'background/Boxing_Ring_Orange.png',
            'background/Boxing_Ring_Purple.png'
        ]
        self.image = load_image(random.choice(bg_list))

        self.frame = 0.0
        # 1초에 몇 프레임 진행할지 (느리게: 1~4 정도 추천)
        self.frames_per_second = 4.0

    def update(self):
        # frame_time 기반으로 부드럽게
        self.frame += self.frames_per_second * game_framework.frame_time
        self.frame %= BoxingRing.TOTAL_FRAMES

    def draw(self):
        # 현재 프레임 인덱스는 int로
        src_x = int(self.frame) * BoxingRing.FRAME_W

        w, h = get_canvas_width(), get_canvas_height()
        self.image.clip_draw(
            src_x, 0,
            BoxingRing.FRAME_W, BoxingRing.FRAME_H,
            w // 2, h // 2,
            w, h
        )

    def get_bb(self):
        return 0, 0, get_canvas_width(), get_canvas_height()

    def handle_collision(self, group, other):
        pass
