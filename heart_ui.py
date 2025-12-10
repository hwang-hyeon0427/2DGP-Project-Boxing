from pico2d import *


class HeartUI:
    """
    idle.png, brake.png 모두 '세로 스프라이트' 구조.
    프레임 사이 간격: 2px
    TIME_PER_ACTION 기반 애니 구현
    """

    def __init__(self, x_p1, y_p1, x_p2, y_p2, scale=3.0):

        # 위치
        self.x_p1 = x_p1 + 160
        self.y_p1 = y_p1 + 770
        self.x_p2 = x_p2 + 40
        self.y_p2 = y_p2 + 770

        # 크기(scale)
        self.heart_scale = scale

        # ================================================
        # 이미지 로드
        # ================================================
        self.idle_img = load_image('resource/image/Heart_idle.png')
        self.brake_img = load_image('resource/image/Heart_brake.png')

        # ================================================
        # 프레임 간격 및 프레임 수 정의
        # ================================================
        self.frame_gap = 2

        self.idle_frame_count = 4      # idle PNG 프레임 수
        self.brake_frame_count = 12     # brake PNG 프레임 수 (필요시 조정)

        # ================================================
        # idle 프레임 자동 계산
        # ================================================
        total_idle_h = self.idle_img.h
        idle_frames = self.idle_frame_count

        self.idle_frame_h = (total_idle_h - self.frame_gap * (idle_frames - 1)) // idle_frames
        self.idle_frame_w = self.idle_img.w

        # ================================================
        # brake 프레임 자동 계산
        # ================================================
        total_brake_h = self.brake_img.h
        brake_frames = self.brake_frame_count

        self.brake_frame_h = (total_brake_h - self.frame_gap * (brake_frames - 1)) // brake_frames
        self.brake_frame_w = self.brake_img.w

        # ================================================
        # Idle 애니메이션 시간 기반 세팅
        # TIME_PER_IDLE_ACTION = idle 전체 프레임 1바퀴 도는 데 걸리는 시간
        # ================================================
        self.TIME_PER_IDLE_ACTION = 0.4  # idle 전체 사이클 0.4초 (조정 가능)
        self.IDLE_ACTION_PER_TIME = 1.0 / self.TIME_PER_IDLE_ACTION
        self.FRAMES_PER_IDLE_ACTION = self.idle_frame_count

        self.idle_frame = 0.0  # idle 현재 프레임 float 누적

        # ================================================
        # brake 애니메이션 시간 기반
        # ================================================
        self.TIME_PER_BREAK_ACTION = 0.6  # 깨짐 전체 0.6초 (조정 가능)
        self.BREAK_ACTION_PER_TIME = 1.0 / self.TIME_PER_BREAK_ACTION
        self.FRAMES_PER_BREAK_ACTION = self.brake_frame_count

        # ================================================
        # 하트 개수
        # ================================================
        self.p1_hearts = 2
        self.p2_hearts = 2

        # 깨짐 애니 실행 리스트
        # 각 항목: { x, y, time, frame }
        self.p1_break_list = []
        self.p2_break_list = []


    # =====================================================
    # 외부에서 하트 감소가 반영되는 함수
    # =====================================================
    def set_hearts(self, p1_new, p2_new):

        # --------------------------
        # P1 하트 줄어듦?
        # --------------------------
        if p1_new < self.p1_hearts:
            lost = self.p1_hearts - p1_new
            for i in range(lost):
                bx = self.x_p1 + (self.p1_hearts - 1 - i) * (self.idle_frame_w * self.heart_scale + 10)
                by = self.y_p1
                self.p1_break_list.append({
                    "x": bx,
                    "y": by,
                    "time": 0.0,
                    "frame": 0
                })
        self.p1_hearts = p1_new

        # --------------------------
        # P2 하트 줄어듦?
        # --------------------------
        if p2_new < self.p2_hearts:
            lost = self.p2_hearts - p2_new
            for i in range(lost):
                bx = self.x_p2 - (self.p2_hearts - 1 - i) * (self.idle_frame_w * self.heart_scale + 10)
                by = self.y_p2
                self.p2_break_list.append({
                    "x": bx,
                    "y": by,
                    "time": 0.0,
                    "frame": 0
                })
        self.p2_hearts = p2_new


    # =====================================================
    # update() — idle 애니 / break 애니 모두 시간 기반 진행
    # =====================================================
    def update(self, frame_time):

        # ------------------------------------
        # Idle 애니메이션 TIME_PER_ACTION 기반
        # ------------------------------------
        self.idle_frame += self.FRAMES_PER_IDLE_ACTION * self.IDLE_ACTION_PER_TIME * frame_time
        self.idle_frame %= self.idle_frame_count

        # ------------------------------------
        # P1 깨짐 애니 진행
        # ------------------------------------
        finished = []
        for idx, b in enumerate(self.p1_break_list):
            b["time"] += frame_time
            b["frame"] = int(
                self.FRAMES_PER_BREAK_ACTION * self.BREAK_ACTION_PER_TIME * b["time"]
            )

            if b["frame"] >= self.brake_frame_count:
                finished.append(idx)

        for idx in reversed(finished):
            del self.p1_break_list[idx]

        # ------------------------------------
        # P2 깨짐 애니 진행
        # ------------------------------------
        finished = []
        for idx, b in enumerate(self.p2_break_list):
            b["time"] += frame_time
            b["frame"] = int(
                self.FRAMES_PER_BREAK_ACTION * self.BREAK_ACTION_PER_TIME * b["time"]
            )

            if b["frame"] >= self.brake_frame_count:
                finished.append(idx)

        for idx in reversed(finished):
            del self.p2_break_list[idx]


    # =====================================================
    # 그리기
    # =====================================================
    def draw_idle_heart(self, x, y):
        frame = int(self.idle_frame)
        src_y = frame * (self.idle_frame_h + self.frame_gap)

        self.idle_img.clip_draw(
            0, src_y,
            self.idle_frame_w, self.idle_frame_h,
            x, y,
            self.idle_frame_w * self.heart_scale,
            self.idle_frame_h * self.heart_scale
        )

    def draw_brake_heart(self, x, y, frame):
        src_y = frame * (self.brake_frame_h + self.frame_gap)

        self.brake_img.clip_draw(
            0, src_y,
            self.brake_frame_w, self.brake_frame_h,
            x, y,
            self.brake_frame_w * self.heart_scale,
            self.brake_frame_h * self.heart_scale
        )

    # =====================================================
    # 전체 그리기
    # =====================================================
    def draw(self):

        # ------------------------
        # P1 idle hearts
        # ------------------------
        for i in range(self.p1_hearts):
            x = self.x_p1 + i * (self.idle_frame_w * self.heart_scale + 10)
            self.draw_idle_heart(x, self.y_p1)

        # ------------------------
        # P2 idle hearts
        # ------------------------
        for i in range(self.p2_hearts):
            x = self.x_p2 - i * (self.idle_frame_w * self.heart_scale + 10)
            self.draw_idle_heart(x, self.y_p2)

        # ------------------------
        # 깨지는 애니메이션 P1
        # ------------------------
        for b in self.p1_break_list:
            self.draw_brake_heart(b["x"], b["y"], b["frame"])

        # ------------------------
        # 깨지는 애니메이션 P2
        # ------------------------
        for b in self.p2_break_list:
            self.draw_brake_heart(b["x"], b["y"], b["frame"])

