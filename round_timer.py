from pico2d import load_image, get_canvas_width, get_canvas_height


class RoundTimer:
    ROUND_SECONDS = 180.0  # 3분 = 180초

    def __init__(self):

        self.timer_bg = load_image('resource/image/Timer.png')  # 타이머 배경
        self.timer_nums = load_image('resource/image/Timer_Numbers.png')  # 숫자 스프라이트
        self.time_over_image = load_image('resource/image/time_over.png')  # 시간초과 연출용 이미지

        self.digit_w = 13 # 숫자 스프라이트 크기
        self.digit_h = 25      # 숫자 스프라이트 크기

        self.time_left = self.ROUND_SECONDS
        self.time_over = False

        w, h = get_canvas_width(), get_canvas_height()
        self.timer_x = w // 2          # 배경의 그릴 X
        self.timer_y = h * 0.85        # 배경의 그릴 Y (상단에서 조금 내림)

        # TIME OVER 출력을 위한 중앙 좌표
        self.center_x = w // 2
        self.center_y = h // 2

        self.number_offset_x = -26   # 숫자4개가 들어갈 전체 영역의 시작점
        self.number_offset_y = -2    # 숫자 Y 보정값

    def reset(self):
        self.time_left = self.ROUND_SECONDS
        self.time_over = False

    def update(self, frame_time: float):
        if self.time_over:
            return

        self.time_left -= frame_time
        if self.time_left <= 0:
            self.time_left = 0
            self.time_over = True

    def draw(self):
        scale = 2.0
        bg_w = self.timer_bg.w * scale
        bg_h = self.timer_bg.h * scale

        self.timer_bg.draw(self.timer_x, self.timer_y, bg_w, bg_h)

        # 2) 남은 시간을 MM:SS → "MM SS" 형태로 문자열화
        total = int(self.time_left)
        minutes = total // 60
        seconds = total % 60
        time_str = f"{minutes:02d} {seconds:02d}"

        digit_w_scaled = self.digit_w * scale # 숫자 스케일 적용
        digit_h_scaled = self.digit_h * scale

        number_gap = 30  # 숫자 간격
        space_gap = 15  # 공백 간격
        num_index = 0  # 그릴 숫자의 인덱스

        base_x = self.timer_x - digit_w_scaled * 2
        base_y = self.timer_y

        for ch in time_str:
            # 공백이면 숫자 자리만큼 건너뛰기 (num_index 증가 X)
            if ch == " ":
                base_x += space_gap
                continue

            dst_x = base_x + num_index * number_gap
            dst_y = base_y

            idx = int(ch) # 숫자에 해당하는 인덱스
            src_x = idx * (self.digit_w + 2)

            self.timer_nums.clip_draw(
                src_x, 0,                         # 어디서 자르기 시작할지
                self.digit_w, self.digit_h,       # 자르는 크기
                dst_x, dst_y,                     # 그릴 위치
                digit_w_scaled, digit_h_scaled    # 스케일 적용
            )

            # 숫자를 하나 그렸으니 num_index 증가
            num_index += 1

            # TIME OVER 표시
        if self.time_over:
            self.time_over_image.draw(self.center_x, self.center_y)

    def is_time_over(self):
        return self.time_over

    def get_time_ratio(self):
        return self.time_left / self.ROUND_SECONDS
