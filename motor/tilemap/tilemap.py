import numpy as np
import pygame as pg
import motor.api
import motor.camera
from motor.tilemap.tileset import Tileset
from motor.object import Object
import math


class Tilemap(Object):
    def __init__(self, name: str, layer: int, x: float, y: float, width: float, height: float, texture_path: str, tile_size: int, tileset: Tileset, data: np.typing.NDArray[np.uint32]):
        super().__init__(name, layer, x, y, width, height)
        self.texture_path = texture_path
        self.tile_size = tile_size
        self.tiles_per_row = int(width / tile_size)  # Ainda válido, mas pode ser data.shape[1] se o CSV definir as colunas
        self.data = data

        self.tileset: Tileset = tileset
        self.texture: pg.Surface = None
    
    def init(self):
        self.texture = motor.api.get_texture(self.texture_path)
    
    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        pixel_scale = motor.api.get_motor().pixel_scale
        canvas_size = motor.api.get_motor().canvas_size.copy()
        
        camera_pos = camera.position
        camera_size = canvas_size

        camera_size.x /= camera.zoom
        camera_size.y /= camera.zoom
        tile_size = self.tile_size
        start_x = max(0, int(camera_pos.x // tile_size))
        start_y = max(0, int(camera_pos.y // tile_size))
        end_x = min(self.data.shape[1], int((camera_pos.x + camera_size.x) // tile_size) + 1)
        end_y = min(self.data.shape[0], int((camera_pos.y + camera_size.y) // tile_size) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                value = self.data[y, x]
                if value == 0:
                    continue
                
                tile_x = x * tile_size
                tile_y = y * tile_size

                tile = self.tileset.get_tile_texture_position(value)
                if tile is not None:
                    scaled_texture = pg.transform.scale(
                        self.texture.subsurface(
                            tile.x,
                            tile.y,
                            tile_size,
                            tile_size
                        ),
                        (math.ceil(tile_size * camera.zoom * pixel_scale), math.ceil(tile_size * camera.zoom * pixel_scale))
                    )
                    canvas.blit(
                        scaled_texture,
                        camera.get_relative_position(
                            tile_x,
                            tile_y,
                        )
                    )

    def is_colliding_with(self, entity_position_x: float, entity_position_y: float, entity_width: float, entity_height: float) -> bool:
        entity_rect = pg.FRect(
            entity_position_x,
            entity_position_y,
            entity_width,
            entity_height
        )

        # Calcular os índices mínimo e máximo dos tiles cobertos pela entidade
        min_x_index = int((entity_rect.left - self.position.x) // self.tile_size)
        max_x_index = int((entity_rect.right - self.position.x) // self.tile_size)
        min_y_index = int((entity_rect.top - self.position.y) // self.tile_size)
        max_y_index = int((entity_rect.bottom - self.position.y) // self.tile_size)

        # Limitar os índices às dimensões do array 2D
        min_x_index = max(0, min_x_index)
        max_x_index = min(self.data.shape[1] - 1, max_x_index)
        min_y_index = max(0, min_y_index)
        max_y_index = min(self.data.shape[0] - 1, max_y_index)

        # Iterar sobre todos os tiles no intervalo
        for y_index in range(min_y_index, max_y_index + 1):
            for x_index in range(min_x_index, max_x_index + 1):
                tile = self.data[y_index, x_index]
                if tile == 0:
                    continue

                tile_x = x_index * self.tile_size + self.position.x
                tile_y = y_index * self.tile_size + self.position.y
                tile_rect = pg.FRect(tile_x, tile_y, self.tile_size, self.tile_size)

                if tile_rect.colliderect(entity_rect):
                    return True

        return False
    
    def is_colliding_with_rect(self, rect: pg.FRect) -> bool:
        return self.is_colliding_with(
            rect.x,
            rect.y,
            rect.width,
            rect.height
        )
    
    def get_tile_at_position(self, x: int, y: int) -> int:
        x_index = int((x - self.position.x) // self.tile_size)
        y_index = int((y - self.position.y) // self.tile_size)
        
        # Verificar se os índices estão dentro dos limites do array 2D
        if (x_index < 0 or x_index >= self.data.shape[1] or 
            y_index < 0 or y_index >= self.data.shape[0]):
            return 0
        return self.data[y_index, x_index]