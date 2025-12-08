from pico2d import load_wav, load_music

sounds = {}
bgm = {}
sfx_volume = 128   # 기본값 (0~128)


def load():
    global sounds, bgm

    # 클릭 사운드
    sounds["click"] = load_wav("resource/sound/Boxing_UI_sound/WAV_mouse-click.wav")
    # 호버 사운드
    sounds["hover"] = load_wav("resource/sound/Boxing_UI_sound/WAV_hover-button.wav")
    # 공격 사운드
    sounds["front_hand"] = load_wav("resource/sound/boxing_Sound_Effects/WAV_punch_light.wav")
    sounds["rear_hand"] = load_wav("resource/sound/boxing_Sound_Effects/WAV_Right_Cross.wav")
    sounds["uppercut"] = load_wav("resource/sound/boxing_Sound_Effects/WAV_Upper_Cut.wav")
    # 가드 사운드
    sounds["blocking"] = load_wav("resource/sound/boxing_Sound_Effects/WAV_blocking-arm-with-hand.wav")
    # 배경음악
    bgm["hip-hop_music"] = load_music("resource/sound/Boxing_bgm/MP_physical_challenge.mp3")
    # bgm["ingame"] = load_music("resource/music/bgm_ingame.mp3")

    print("[SoundManager] All sounds loaded.")

    for s in sounds.values():
        s.set_volume(sfx_volume)

def play(name):
    sound = sounds.get(name, None)
    if sound:
        sound.play()
    else:
        print(f"[SoundManager] Sound '{name}' not found.")

def get_attack_sound(attack_type):
    return sounds.get(attack_type, None)

def play_bgm(name):
    if name in bgm:
        bgm[name].repeat_play()

def stop_bgm(name):
    if name in bgm:
        bgm[name].stop()

def set_sfx_volume(level):
    global sfx_volume

    # level → 0/1/2/3을 실제 0~128 볼륨으로 변환
    volume_map = {
        0: 0,
        1: 42,
        2: 85,
        3: 128
    }

    sfx_volume = volume_map.get(level, 128)

    # 모든 효과음에 반영
    for s in sounds.values():
        s.set_volume(sfx_volume)
