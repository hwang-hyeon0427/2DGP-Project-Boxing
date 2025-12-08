class AttackRouter:
    def __init__(self, boxer):
        self.boxer = boxer

    def route(self, attack_name):
        """attack_name에 맞는 AttackState를 반환"""
        if attack_name == 'front_hand':
            return self.boxer.FRONT_HAND
        elif attack_name == 'rear_hand':
            return self.boxer.REAR_HAND
        elif attack_name == 'uppercut':
            return self.boxer.UPPERCUT

        print("[AttackRouter] Unknown attack:", attack_name)
        return None
