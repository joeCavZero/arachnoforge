import pygame as pg
import motor.api
from typing import Union, Tuple
class Camera:
    def __init__(self, x: float, y: float, zoom: float, width: int, height: int):
        self.position = pg.Vector2(x, y)
        self.zoom = zoom
        self.border = pg.Vector2(width, height)
    def center_position(self, x: float, y: float):
        m = motor.api.get_motor()
        zoom = self.zoom
        pixel_scale = m.pixel_scale
        canvas_size = m.canvas_size

        offset_x = (canvas_size.x / zoom / pixel_scale) / 2
        offset_y = (canvas_size.y / zoom / pixel_scale) / 2
        camera_x = x - offset_x
        camera_y = y - offset_y

        max_width = self.border.x - (canvas_size.x / zoom / pixel_scale)
        max_height = self.border.y - (canvas_size.y / zoom / pixel_scale)

        max_width = max(0, max_width)
        max_height = max(0, max_height)

        self.position.x = max(min(camera_x, max_width), 0)
        self.position.y = max(min(camera_y, max_height), 0)
        
    def get_relative_position(self, x: float, y: float) -> pg.Vector2:
        pixel_scale = motor.api.get_motor().pixel_scale
        return pg.Vector2(
            (x - self.position.x) * self.zoom*pixel_scale,
            (y - self.position.y) * self.zoom*pixel_scale
        )
    def get_relative_size(self, width: float, height: float) -> pg.Vector2:
        pixel_scale = motor.api.get_motor().pixel_scale
        return pg.Vector2(
            width * self.zoom * pixel_scale,
            height * self.zoom * pixel_scale
        )

    def get_relative_size_by_vector2(self, vector: Union[pg.Vector2, Tuple[float, float]]) -> pg.Vector2:
        vector = pg.Vector2(vector) if isinstance(vector, tuple) else vector
        return self.get_relative_size(vector.x, vector.y)

    def get_relative_position_by_vector2(self, vector: Union[pg.Vector2, Tuple[float, float]]) -> pg.Vector2:
        vector = pg.Vector2(vector) if isinstance(vector, tuple) else vector
        return self.get_relative_position(vector.x, vector.y)
    
    def get_relative_rect(self, x: float, y: float, width: float, height: float) -> pg.FRect:
        relative_position = self.get_relative_position(x, y)
        relative_size = self.get_relative_size(width, height)
        return pg.FRect(
            relative_position.x,
            relative_position.y,
            relative_size.x,
            relative_size.y
        )
    def get_relative_rect_by_rect(self, rect: pg.FRect) -> pg.FRect:
        return self.get_relative_rect(rect.x, rect.y, rect.width, rect.height)

    def is_rect_on_screen(self, x: float, y: float, width: float, height: float) -> bool:
        relative_position = self.get_relative_position(x, y)
        relative_size = self.get_relative_size(width, height)
        return (
            relative_position.x + relative_size.x >= 0 and
            relative_position.x <= self.border.x and
            relative_position.y + relative_size.y >= 0 and
            relative_position.y <= self.border.y
        )
    def is_rect_on_screen_by_rect(self, rect: pg.FRect) -> bool:
        return self.is_rect_on_screen(rect.x, rect.y, rect.width, rect.height)

    def is_point_on_screen(self, x: float, y: float) -> bool:
        relative_position = self.get_relative_position(x, y)
        return (
            relative_position.x >= 0 and
            relative_position.x <= self.border.x and
            relative_position.y >= 0 and
            relative_position.y <= self.border.y
        )
    
    def get_relative_scalar(self, scalar: float) -> float:
        pixel_scale = motor.api.get_motor().pixel_scale
        return scalar * self.zoom * pixel_scale