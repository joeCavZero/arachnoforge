import numpy as np
import numba
from motor.tilemap.tilemap import Tilemap
from motor.tilemap.tileset import Tileset

class AutoTilemapBinding:
    def __init__(self, tile_id: int, top: bool, left: bool, right: bool, bottom: bool):
        self.tile_id = tile_id
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom

class AutoTilemap(Tilemap):
    def __init__(self, name: str, layer: int, x: float, y: float, width: float, height: float, texture_path: str, tile_size: int, tileset: Tileset, data: np.typing.NDArray[np.int32], auto_tile_bindings: list[AutoTilemapBinding]):
        super().__init__(name, layer, x, y, width, height, texture_path, tile_size, tileset, data)
        self.auto_tile_bindings: list[AutoTilemapBinding] = auto_tile_bindings
    
    def get_tile_by_position_or(self, x: int, y: int, nil=None) -> int:
        if x < 0 or x >= self.data.shape[1] or y < 0 or y >= self.data.shape[0]:
            return nil
        
        return self.data[y, x]
    
    def auto_tile(self):
        new_data = self.data.copy()
        for y, x in np.ndindex(self.data.shape):
            value = self.data[y, x]
            if value == 0:
                continue

            top_tile = self.get_tile_by_position_or(x, y - 1, 1)
            left_tile = self.get_tile_by_position_or(x - 1, y, 1)
            right_tile = self.get_tile_by_position_or(x + 1, y, 1)
            bottom_tile = self.get_tile_by_position_or(x, y + 1, 1)

            has_top = top_tile != 0
            has_left = left_tile != 0
            has_right = right_tile != 0
            has_bottom = bottom_tile != 0

            for binding in self.auto_tile_bindings:
                if (
                    binding.top == has_top and
                    binding.left == has_left and
                    binding.right == has_right and
                    binding.bottom == has_bottom
                ):
                    new_data[y, x] = binding.tile_id
                    break
        self.data = new_data