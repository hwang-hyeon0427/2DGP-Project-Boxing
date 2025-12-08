from pico2d import load_wav, load_music

sounds = {}
bgm = {}

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
    bgm["lobby"] = load_music("resource/sound/Boxing_bgm/MP_physical_challenge.mp3")
    # bgm["ingame"] = load_music("resource/music/bgm_ingame.mp3")

    print("[SoundManager] All sounds loaded.")

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
