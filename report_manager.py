# 전체 공격 사거리 자동 기록 & 보고서 출력 기능

# 공격 사거리 저장소:
# { (attack_name, frame): { "P1": distance, "P2": distance } }
report_buffer = {}

# ---------------------------------------
#  리포트 ON/OFF 전역 스위치
# ---------------------------------------
_REPORT_ENABLED = False  # 기본값: 끔(False)

def enable():
    """리포트 기록 기능 켜기"""
    global _REPORT_ENABLED
    _REPORT_ENABLED = True
    print("[REPORT] Hitbox report ENABLED")

def disable():
    """리포트 기록 기능 끄기"""
    global _REPORT_ENABLED
    _REPORT_ENABLED = False
    print("[REPORT] Hitbox report DISABLED")

def toggle():
    """리포트 기능 토글 (켜져 있으면 끄고, 꺼져 있으면 켜기)"""
    global _REPORT_ENABLED
    _REPORT_ENABLED = not _REPORT_ENABLED
    print(f"[REPORT] Hitbox report TOGGLED → now = {_REPORT_ENABLED}")

def is_enabled():
    """현재 리포트 기능이 켜져 있는지 확인용 (True/False 반환)"""
    return _REPORT_ENABLED

def record_hitbox(attack, frame, player_id, distance):
    if not is_enabled():
        return
    """P1/P2 사거리 기록. 최근값으로 덮어씀."""
    key = (attack, frame)

    if key not in report_buffer:
        report_buffer[key] = {}

    report_buffer[key][player_id] = distance

def print_report():
    """F10 입력 시 전체 공격 사거리 보고서 출력"""
    print("\n========================================")
    print("        ATTACK RANGE REPORT")
    print("========================================\n")

    # 공격 그룹별 정렬
    sorted_keys = sorted(report_buffer.keys(), key=lambda x: (x[0], x[1]))

    current_attack = None

    for (attack, frame) in sorted_keys:
        # 공격 이름이 바뀌면 섹션 헤더 출력
        if current_attack != attack:
            current_attack = attack
            print(f"[{attack}]")

        data = report_buffer[(attack, frame)]
        p1 = data.get("P1", None)
        p2 = data.get("P2", None)

        if p1 is None or p2 is None:
            print(f"  frame {frame}: (데이터 부족)")
            continue

        diff = p2 - p1
        diff_text = f"{diff:+.1f}"

        print(f"  frame {frame}: P1={p1:.1f} | P2={p2:.1f}  diff={diff_text}")

    print("\n============== END REPORT ==============\n")
