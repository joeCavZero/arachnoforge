import pygame as pg
from typing import TYPE_CHECKING

import motor.api
if TYPE_CHECKING:
    import motor.camera

class Object:
    def __init__(self, name: str, layer: int, x: float, y: float, width: float, height: float, tags: list[str] = None, z_index_y_offset: float = 0.0):
        self.name = name
        self.layer = layer
        self.uid: int = 0
        self.position = pg.Vector2(x, y)
        self.size = pg.Vector2(width, height)
        self.tags: list[str] = tags if tags is not None else []

        self.z_index_y_offset: float = z_index_y_offset

    def init(self):
        pass

    def update(self, delta_time: float):
        pass

    def render(self, canvas: pg.Surface, camera: 'motor.camera.Camera'):
        pass

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
    
    def get_rect(self) -> pg.FRect:
        return pg.FRect(
            self.position.x,
            self.position.y,
            self.size.x,
            self.size.y
        )

    def get_center_position(self) -> pg.Vector2:
        return pg.Vector2(
            self.position.x + (self.size.x / 2),
            self.position.y + (self.size.y / 2)
        )
    def center_position(self, x: float, y: float):
        self.position.x = x - (self.size.x / 2)
        self.position.y = y - (self.size.y / 2)
    
    def center_position_by_position(self, position: pg.Vector2 | tuple[float, float]):
        position = pg.Vector2(position) if isinstance(position, tuple) else position
        self.center_position(position.x, position.y)
    
    def destroy(self):
        motor.api.get_scene().delete_object_by_uid(self.uid)