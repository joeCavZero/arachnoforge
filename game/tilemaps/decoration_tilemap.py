import motor.api
import motor.tilemap.tilemap
import motor
import motor.tilemap.tileset
import numpy as np
import random

class DecorationTilemap(motor.tilemap.tilemap.Tilemap):
    def __init__(self):
        tileset = motor.tilemap.tileset.Tileset()
        tileset.add_tile(1, 0 , 0)
        tileset.add_tile(2, 16, 0)
        tileset.add_tile(3, 32, 0)
        tileset.add_tile(4, 48, 0)
        tileset.add_tile(5, 64, 0)
        tileset.add_tile(6, 80, 0)

        source_data = motor.api.read_level_data("data/levels/main-level.csv")
        data = np.zeros((source_data.shape[0], source_data.shape[1]), dtype=np.uint32)
        
        choices = []
        for _ in range(200):
            choices.append(0)
        for _ in range(5):
            choices.append(1)
        for _ in range(5):
            choices.append(2)
        for _ in range(5):
            choices.append(3)
        for _ in range(5):
            choices.append(4)
        for _ in range(5):
            choices.append(5)
        for _ in range(5):
            choices.append(6)
        
        for y, x in np.ndindex(source_data.shape):
            v = source_data[y, x]
            if v == 0:
                data[y, x] = random.choice(choices)

        super().__init__(
            "decoration-tilemap", 6,
            0, 0,
            6400, 6400,
            "assets/images/decoration.png",
            16,
            tileset,
            data
        )

        