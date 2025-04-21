
import pygame as pg
class TextureManager:
    def __init__(self):
        self.textures: dict[str, pg.Surface] = {}
    
    def load_texture(self, path: str):
        if path not in self.textures:
            texture = pg.image.load(path).convert_alpha()
            self.textures[path] = texture
    
    def get_texture(self, path: str) -> pg.Surface | None:
        return self.textures.get(path, None)