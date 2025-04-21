import game
import game.characters
import game.characters.character
import pygame as pg
import motor.animation
import motor.api
import motor.math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import game.characters.spider
class Flower(game.characters.character.Character):
    def __init__(self, x: int, y: int):
        super().__init__(
            "flower",
            10,
            x, y,
            64, 64,
            0,
            16, 16, 32, 32,
            health=20, speed=100,
            z_index_y_offset=64,
            anchored=True,
            tags=["ally"]
        )
    
    def init(self):
        self.load_texture("assets/images/flower.png")
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0),
            ],
            10,
            loop=True
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")
    
    def update(self, delta_time):
        if self.health <= 0:
            self.destroy()