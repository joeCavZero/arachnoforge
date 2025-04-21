import pygame as pg

class Animation:
    def __init__(self, name: str, frames: list[pg.Vector2], speed: float, loop: bool = True):
        self.name = name
        self.frames = frames
        self.speed = speed
        self.current_frame: float = 0
        self.loop = loop
    
    def update(self, delta_time: float):
        self.current_frame += self.speed * delta_time
        if self.loop == True and self.current_frame >= len(self.frames):
            self.current_frame = 0
    
    def get_frame(self) -> int:
        return int(self.current_frame)
    
    def get_actual_frame_rect(self, width: int, height: int) -> pg.Rect:
        frame = self.frames[self.get_frame()]
        return pg.Rect(
            frame.x,
            frame.y,
            width,
            height
        )