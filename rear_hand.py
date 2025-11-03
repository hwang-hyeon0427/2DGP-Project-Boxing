class RearHand:
    def __init__(self, boxer):
        self.b = boxer             # Boxer 인스턴스 참조
        self.done = False         # 애니메이션 완료여부

    def enter(self, e):
        # 상태에 집입할 때 실행되는 함수
        # e :  상태 전환의 원인이 된 이벤트

        # 'rear_hand' 시트가 설정에 있으면 사용, 없으면 'idle' 시트 사용
        if 'rear_hand' in self.b.cfg:
            sheet = self.b.cfg['rear_hand']
        else:
            sheet = self.b.cfg['idle']
        self.b.use_sheet(sheet)             # 선택된 시트를 boxer 객체에 적용
        self.b.frame = 0                    # 프레임 인덱스 0으로 초기화
        self.done = False                   # 애니메이션 완료여부 초기화

    def exit(self, e):
        # 상태에서 빠져나갈 때 호출됨 (Exit action)
        # 현재는 특별한 정리 작업이 필요 없어서 pass 처리
        pass

    def do(self):
        # 상태에 머무르는 동안 매 프레임마다 반복 실행 (Do activity)
        if not self.done:
            # 1️⃣ 다음 프레임으로 이동
            self.b.frame += 1
            # 마지막 프레임까지 도달하면 애니메이션 종료
            if self.b.frame >= self.b.cols:
                self.done = True
                # 애니메이션 종료 이벤트를 상태 머신에 전달
                self.b.state_machine.handle_state_event(('ANIMATION_END', None))

    def draw(self):
        # 현재 프레임을 실제로 화면에 그리는 함수
        # Boxer 클래스의 draw_current()는 현재 시트, 프레임, 방향(face)에 따라 이미지 클리핑을 수행함
        self.b.draw_current()
