from pico2d import load_wav, load_music

sounds = {}
bgm = {}

def load():
    global sounds, bgm

    # 클릭 사운드
    sounds["click"] = load_wav("resource/sound/click.wav")
    # 공격 사운드
    sounds["front_hand"] = load_wav("resource/sound/boxing_Sound_Effect/MP_punch(light).wav")
    sounds["rear_hand"] = load_wav("resource/sound/boxing_Sound_Effect/MP_Right_Cross.wav")
    sounds["uppercut"] = load_wav("resource/sound/boxing_Sound_Effect/MP_Upper_Cut.wav")
    # 가드 사운드
    sounds["block"] = load_wav("resource/sound/block.wav")
    # 배경음악
    bgm["title"] = load_music("resource/music/bgm_title.mp3")
    bgm["ingame"] = load_music("resource/music/bgm_ingame.mp3")

    print("[SoundManager] All sounds loaded.")

def play(name):
    sound = sounds.get(name, None)
    if sound:
        sound.play()
    else:
        print(f"[SoundManager] Sound '{name}' not found.")

def get_attack_sound(attack_type):
    # attack_type: "front_hand", "rear_hand", "uppercut"
    return sounds.get(attack_type, None)