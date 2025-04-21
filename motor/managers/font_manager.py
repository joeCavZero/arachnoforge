
import pygame as pg
class FontManager:
    def __init__(self):
        self.fonts: dict[str, pg.Font] = {}
    
    def load_font(self, path: str, size: int):
        if path not in self.fonts:
            font = pg.font.Font(path, size)
            self.fonts[path] = font
        else:
            font = self.fonts[path]
            font.size = size
    
    def get_font(self, path: str) -> pg.Font | None:
        return self.fonts.get(path, None)