import motor.api as motor
from motor.tilemap.auto_tilemap import AutoTilemap
from motor.tilemap.auto_tilemap import AutoTilemapBinding
from motor.tilemap.tileset import Tileset

class MainTilemap(AutoTilemap):
    def __init__(self):
        tileset = Tileset()
        tileset.add_tile(1, 0 , 0)
        tileset.add_tile(2, 16, 0)
        tileset.add_tile(3, 32, 0)
        tileset.add_tile(4, 48, 0)
        tileset.add_tile(5, 0 , 16)
        tileset.add_tile(6, 16, 16)
        tileset.add_tile(7, 32, 16)
        tileset.add_tile(9,  0,  32)
        tileset.add_tile(10,  16, 32)
        tileset.add_tile(11, 32, 32)
        tileset.add_tile(12, 48, 32)

        binding = [
            
            AutoTilemapBinding(4, False, False, False, False),
            AutoTilemapBinding(11, False, False, False, True),
            AutoTilemapBinding(9, False, False, True, False),
            AutoTilemapBinding(1, False, False, True, True),
            AutoTilemapBinding(10, False, True, False, False),
            AutoTilemapBinding(3, False, True, False, True),
            AutoTilemapBinding(6, False, True, True, False),
            AutoTilemapBinding(2, False, True, True, True),
            AutoTilemapBinding(12, True, False, False, False),
            AutoTilemapBinding(2, True, False, False, True),
            AutoTilemapBinding(5, True, False, True, False),
            AutoTilemapBinding(2, True, False, True, True),
            AutoTilemapBinding(7, True, True, False, False),
            AutoTilemapBinding(2, True, True, False, True),
            AutoTilemapBinding(6, True, True, True, False),
            AutoTilemapBinding(2, True, True, True, True),

        ]

        super().__init__(
            "main-tilemap", 5,
            0, 0,
            6400, 6400,
            "assets/images/grass-tileset.png",
            16,
            tileset,
            motor.read_level_data("data/levels/main-level.csv"),
            binding
        )
        
        self.auto_tile()
        