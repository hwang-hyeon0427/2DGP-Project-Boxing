from pico2d import *
from boxer import Ko

class HpUi:
    # 고정된 소스 좌표 (절대 변경 X)
    P1_SRC_X = 0
    P1_SRC_W = 144      # P1 HP 바 길이

    KO_SRC_X = 145
    KO_SRC_W = 31       # KO 중앙

    P2_SRC_X = 177
    P2_SRC_W = (321 - 177 + 1)   # P2 HP 바 길이 = 145px

    SRC_H = 16          # 이미지 높이

    def __init__(self, p1, p2, x, y, scale=1.0):
        # p1, p2 직접 참조
        self.p1 = p1
        self.p2 = p2

        # KO 중심 좌표
        self.x = x
        self.y = y
        self.scale = scale

        # 이미지 로드
        self.img_red = load_image('resource/health/hp_red.png')
        self.img_yellow = load_image('resource/health/hp_yellow.png')

        # HP 최대값은 p1.hp_max 로 가져감 (둘이 같다고 가정)
        self.max_hp = p1.max_hp

    def update(self):
        # 즉시 반영 방식 → update 는 아무것도 안 함
        pass

    def draw(self):
        # =============================================
        # KO 중심 기준 위치 계산
        # =============================================
        ko_center_x = self.x
        ko_left_x   = ko_center_x - (HpUi.KO_SRC_W * 0.5 * self.scale)
        ko_right_x  = ko_center_x + (HpUi.KO_SRC_W * 0.5 * self.scale)

        # P1 전체 red bar
        p1_red_center = ko_left_x - (HpUi.P1_SRC_W * 0.5 * self.scale)
        self.img_red.clip_draw(
            HpUi.P1_SRC_X, 0, HpUi.P1_SRC_W, HpUi.SRC_H,
            p1_red_center, self.y,
            HpUi.P1_SRC_W * self.scale, HpUi.SRC_H * self.scale
        )

        # P2 전체 red bar
        p2_red_center = ko_right_x + (HpUi.P2_SRC_W * 0.5 * self.scale)
        self.img_red.clip_draw(
            HpUi.P2_SRC_X, 0, HpUi.P2_SRC_W, HpUi.SRC_H,
            p2_red_center, self.y,
            HpUi.P2_SRC_W * self.scale, HpUi.SRC_H * self.scale
        )

        # ==========================
        # KO 글자 이미지 선택
        # ==========================
        p1_ko = isinstance(self.p1.state_machine.cur_state, Ko)
        p2_ko = isinstance(self.p2.state_machine.cur_state, Ko)

        if p1_ko or p2_ko:
            ko_img = self.img_red  # KO 시 = 빨간색 KO
        else:
            ko_img = self.img_yellow  # 평상시 = 노란색 KO

        # ==========================
        # KO 그리기
        # ==========================
        ko_img.clip_draw(
            HpUi.KO_SRC_X, 0, HpUi.KO_SRC_W, HpUi.SRC_H,
            ko_center_x, self.y,
            HpUi.KO_SRC_W * self.scale, HpUi.SRC_H * self.scale
        )

        # =============================================
        # 3) P1 HP BAR (왼쪽)
        # =============================================
        p1_hp_ratio = max(0.001, self.p1.hp / self.max_hp)  # 최소 0.1% 유지
        p1_hp_w = int(HpUi.P1_SRC_W * p1_hp_ratio)

        # 오른쪽 anchor 고정 → P1은 KO 왼쪽을 anchor
        p1_src_x = HpUi.P1_SRC_W - p1_hp_w
        p1_hp_center = ko_left_x - (p1_hp_w * 0.5 * self.scale)

        self.img_yellow.clip_draw(
            HpUi.P1_SRC_X + p1_src_x, 0, p1_hp_w, HpUi.SRC_H,
            p1_hp_center, self.y,
            p1_hp_w * self.scale, HpUi.SRC_H * self.scale
        )

        # =============================================
        # 4) P2 HP BAR (오른쪽)
        # =============================================
        p2_hp_ratio = max(0.001, self.p2.hp / self.max_hp)
        p2_hp_w = int(HpUi.P2_SRC_W * p2_hp_ratio)

        # 왼쪽 anchor 고정 → P2는 KO 오른쪽을 anchor
        p2_hp_center = ko_right_x + (p2_hp_w * 0.5 * self.scale)

        self.img_yellow.clip_draw(
            HpUi.P2_SRC_X, 0, p2_hp_w, HpUi.SRC_H,
            p2_hp_center, self.y,
            p2_hp_w * self.scale, HpUi.SRC_H * self.scale
        )
