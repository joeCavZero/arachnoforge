
import pygame as pg
class TextureManager:
    def __init__(self):
        self.textures: dict[str, pg.Surface] = {}
    
    def load_texture(self, path: str):
        if path not in self.textures:
            try:
                texture = pg.image.load(path).convert_alpha()
                self.textures[path] = texture
            except Exception as e:
                raise ValueError(f"Failed to load texture from {path}")
    
    def get_texture(self, path: str) -> pg.Surface | None:
        return self.textures.get(path, None)