import os
from pico2d import load_wav, load_music
from Sound_Files import SOUND_FILES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.sounds = {}
        return cls._instance

    def load_all(self):
        """Try to load each sound as music (streamed) to allow stop().
        If load_music fails, fall back to load_wav.
        """
        for name, path in SOUND_FILES.items():
            full_path = os.path.join(BASE_DIR, path)
            if name in self.sounds:
                continue
            try:
                m = load_music(full_path)
                self.sounds[name] = m
            except Exception:
                try:
                    s = load_wav(full_path)
                    self.sounds[name] = s
                except Exception as e:
                    print(f"SoundManager: failed to load {full_path}: {e}")

    def play(self, name, loop=False, volume=64):
        """Play the named resource. For music objects you can request loop=True.
        Sets volume when supported.
        """
        if name not in self.sounds:
            return
        obj = self.sounds[name]
        try:
            if hasattr(obj, 'set_volume'):
                obj.set_volume(volume)

            # music objects in pico2d expose play() and repeat_play(); wavs expose play()
            if loop and hasattr(obj, 'repeat_play'):
                obj.repeat_play()
            else:
                obj.play()
        except Exception as e:
            print(f"SoundManager.play error for {name}: {e}")

    def stop(self, name):
        if name not in self.sounds:
            return
        obj = self.sounds[name]
        try:
            if hasattr(obj, 'stop'):
                obj.stop()
        except Exception as e:
            print(f"SoundManager.stop error for {name}: {e}")

    def stop_all(self):
        for name, obj in self.sounds.items():
            try:
                if hasattr(obj, 'stop'):
                    obj.stop()
            except Exception:
                pass

sound_manager = SoundManager()