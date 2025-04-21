import pygame as pg
class SoundManager:
    def __init__(self):
        self.sounds: dict[str, pg.mixer.Sound] = {}
    
    def load_sound(self, path: str):
        if path not in self.sounds:
            sound = pg.mixer.Sound(path)
            self.sounds[path] = sound
    
    def get_sound(self, path: str) -> pg.mixer.Sound | None:
        return self.sounds.get(path, None)
    
    def play_sound(self, path: str, volume: float= 1.0, loops: int = 0, maxtime: int = 0, fade_ms: int = 0):
        sound = self.get_sound(path)
        if sound:
            channel = sound.play(loops=loops, maxtime=maxtime, fade_ms=fade_ms)
            if channel:
                channel.set_volume(volume)