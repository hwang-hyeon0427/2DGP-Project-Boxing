from pico2d import load_image, get_canvas_width, get_canvas_height

class RoundIntro:
    SHOW_GIRL = 0    # 라운드 걸 보여주기
    SHOW_FINAL = 1   # 파이널 라운드 보여주기
    SHOW_FIGHT = 2   # 파이트 이미지 보여주기
    DONE = 3         # 완료 상태

    def __init__(self, scale=0.5):
        self.round_girl = load_image('resource/image/round_girl.png')
        self.final_round_img = load_image('resource/image/final_round.png')
        self.fight_img = load_image('resource/image/Street_Fighter_fight.png')
        self.number_images = {
            1: load_image('resource/image/number_one.png'),
            2: load_image('resource/image/number_two.png')
        }

        self.number_scale = 5 # 숫자 이미지 스케일 (기본값 1.0)
        self.fight_scale = 10  # FIGHT 이미지 스케일 (기본값 1.0)
        self.final_scale = 10  # FINAL ROUND 이미지 스케일 (기본값 1.0)

        # Layout
        self.scale = scale # 전체 이미지 축소 비율
        self.girl_w = int(512 * self.scale)
        self.girl_h = int(1685 * self.scale)

        w, h = get_canvas_width(), get_canvas_height()
        self.center_x = w // 2
        self.center_y = h // 2

        # Runtime values
        self.state = self.DONE
        self.timer = 0
        self.round_number = 1
        self.is_final_round = False   # 외부에서 전달됨

    def start(self, round_number, is_final=False):
        self.round_number = round_number
        self.is_final_round = is_final
        self.timer = 0

        if self.is_final_round:
            self.state = self.SHOW_FINAL
        else:
            self.state = self.SHOW_GIRL

    def update(self, frame_time):
        if self.state == self.DONE:
            return

        self.timer += frame_time

        if self.state == self.SHOW_GIRL:
            if self.timer >= 1.5:
                self.state = self.SHOW_FIGHT
                self.timer = 0

        elif self.state == self.SHOW_FINAL:
            if self.timer >= 1.5:
                self.state = self.SHOW_FIGHT
                self.timer = 0

        elif self.state == self.SHOW_FIGHT:
            if self.timer >= 0.8:
                self.state = self.DONE

    def draw(self):
        if self.state == self.DONE:
            return

        cx = self.center_x
        cy = self.center_y

        if self.state == self.SHOW_GIRL:
            # 1) 라운드 걸 그리기 (축소)
            self.round_girl.draw(cx, cy, self.girl_w, self.girl_h)

            # 2) 숫자 그리기 (너가 직접 위치 수정하면 됨)
            if self.round_number in self.number_images:
                num_img = self.number_images[self.round_number]
                # 아래 좌표는 너가 원하는 대로 수정하면 됨
                num_x = cx
                num_y = cy + 315
                # 숫자 이미지 크기 적용
                w = int(num_img.w * self.number_scale)
                h = int(num_img.h * self.number_scale)

                num_img.draw(num_x, num_y, w, h)


        elif self.state == self.SHOW_FINAL:
            fw = int(self.final_round_img.w * self.final_scale)
            fh = int(self.final_round_img.h * self.final_scale)

            self.final_round_img.draw(cx, cy, fw, fh)

        elif self.state == self.SHOW_FIGHT:
            fw = int(self.fight_img.w * self.fight_scale)
            fh = int(self.fight_img.h * self.fight_scale)

            self.fight_img.draw(cx, cy, fw, fh)

    def is_done(self):
        return self.state == self.DONE
