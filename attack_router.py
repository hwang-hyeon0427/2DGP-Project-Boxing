class AttackRouter:
    def __init__(self, boxer):
        self.boxer = boxer

    def enter(self, e):
        # e = ('ATTACK', attack_name)
        attack_name = e[1]

        # 어떤 공격인지 분기
        if attack_name == 'front_hand':
            next_state = self.boxer.FRONT_HAND
        elif attack_name == 'rear_hand':
            next_state = self.boxer.REAR_HAND
        elif attack_name == 'uppercut':
            next_state = self.boxer.UPPERCUT
        else:
            print("[AttackRouter] Unknown attack:", attack_name)
            return

        # 현재 상태 종료
        self.boxer.state_machine.cur_state.exit(e)

        # 바로 다음 공격 상태로 전환
        next_state.enter(e)
        self.boxer.state_machine.cur_state = next_state

    def exit(self, e): pass
    def do(self):pass
    def draw(self):pass
