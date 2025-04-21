import pygame as pg
class Tileset:
    def __init__(self):
        self.tiles: dict[int, pg.Vector2] = {}
    
    def add_tile(self, tile_id: int, x: int, y: int):
        self.tiles[tile_id] = pg.Vector2(x, y)
    
    def get_tile_texture_position(self, tile_id: int) -> pg.Vector2:
        return self.tiles.get(tile_id, None)

    def get_tile_position(self, tile_id: int) -> pg.Vector2:
        return self.tiles.get(tile_id, None)