import game
import game.characters
import pygame as pg
import game.characters.enemy
import game.misc.bee_shoot
import math
import motor.animation
import motor.api
import motor.math
from typing import TYPE_CHECKING

import motor.timer
if TYPE_CHECKING:
    import game.characters.spider
    import game.misc.web_string

ATTACK_DISTANCE = 15
ATTACK_DELAY = 2
class Beetle(game.characters.enemy.Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(
            "beetle",
            10,
            x, y,
            64, 32,
            0,
            16, 8, 32, 16,
            health=5, speed=100,
            tags=["enemy", "solid"],
            z_index_y_offset=32,
        )
        self.attack_timer = motor.timer.Timer()
    def init(self):
        self.load_texture("assets/images/beetle-sheet.png")
        walking_animation = motor.animation.Animation(
            "walking",
            [
                pg.Vector2(64, 0),
                pg.Vector2(128, 0),
            ],
            6,
            loop=True
        )
        self.add_animation(walking_animation)
        self.set_animation_by_name("walking")
    
    def update(self, delta_time):
        self.set_motion_to_closest_ally(min_distance=ATTACK_DISTANCE)
        
        
        if self.motion.length() > 0:
            if self.motion.x < 0:
                self.mirrored = True
            else:
                self.mirrored = False
        self.move_and_collide_with_enemies()
        self.attack_timer.update(delta_time)
        self.trapped_timer.update(delta_time)
        self.animation.update(delta_time)

    def damage(self, damage):
        self.health -= damage
        self.kill_if_health_is_zero()