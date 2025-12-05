from pico2d import *
import random
import game_framework  # frame_time

class BoxingRing:
    FRAME_W = 317
    FRAME_H = 128
    TOTAL_FRAMES = 4

    # -----------------------------
    # 이미지 캐싱 (공용 저장소)
    # -----------------------------
    image_cache = {}   # { "path": image_object }

    def __init__(self):
        # 사용할 이미지 리스트
        bg_list = [
            'resource/background/Boxing_Ring_Blue.png',
            'resource/background/Boxing_Ring_Green.png',
            'resource/background/Boxing_Ring_Orange.png',
            'resource/background/Boxing_Ring_Purple.png'
        ]

        # 랜덤 선택된 이미지 경로
        chosen_path = random.choice(bg_list)

        # -----------------------------
        # 캐시 확인 → 없으면 로드
        # -----------------------------
        if chosen_path not in BoxingRing.image_cache:
            print(f"[BoxingRing] loading image: {chosen_path}")
            BoxingRing.image_cache[chosen_path] = load_image(chosen_path)
        else:
            print(f"[BoxingRing] use cached image: {chosen_path}")

        # 캐싱된 이미지 객체 참조
        self.image = BoxingRing.image_cache[chosen_path]

        # 인스턴스 상태 (개별 프레임)
        self.frame = 0.0
        self.frames_per_second = 4.0

    def update(self):
        self.frame += self.frames_per_second * game_framework.frame_time
        self.frame %= BoxingRing.TOTAL_FRAMES

    def draw(self):
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
