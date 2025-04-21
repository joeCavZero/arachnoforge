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

ATTACK_DISTANCE = 115
ATTACK_DELAY = 2
class Bee(game.characters.enemy.Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(
            "bee",
            10,
            x, y,
            64, 64,
            0,
            16, 16, 32, 32,
            health=2, speed=100,
            tags=["enemy", "solid"],
            z_index_y_offset=64,
        )
        self.attack_timer = motor.timer.Timer()
    def init(self):
        self.load_texture("assets/images/bee-sheet.png")
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0),
                pg.Vector2(64, 0),
            ],
            6,
            loop=True
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")
    
    def update(self, delta_time):
        self.set_motion_to_closest_ally(min_distance=ATTACK_DISTANCE)
        
        closest_ally = self.get_closest_ally()
        if closest_ally and self.attack_timer.is_finished():
            distance = self.get_center_position().distance_to(closest_ally.get_center_position())
            if distance  <=  ATTACK_DISTANCE:
                new_bee_shoot = game.misc.bee_shoot.BeeShoot(
                    self.get_center_position().x,
                    self.get_center_position().y,
                    math.degrees(math.atan2(
                        closest_ally.get_center_position().y - self.position.y - self.size.y / 2,
                        closest_ally.get_center_position().x - self.position.x - self.size.x / 2
                    ))
                )
                motor.api.get_scene().add_object(new_bee_shoot)
                self.attack_timer.restart(ATTACK_DELAY)
        if self.motion.length() > 0:
            if self.motion.x < 0:
                self.mirrored = True
            else:
                self.mirrored = False
            self.angle = pg.math.lerp(self.angle, self.motion.x * 30, 0.1)
        else:
            self.angle = pg.math.lerp(self.angle, 0, 0.1)
        self.move_and_collide_with_enemies()
        self.attack_timer.update(delta_time)
        self.trapped_timer.update(delta_time)
        self.animation.update(delta_time)

    def damage(self, damage):
        self.health -= damage
        self.kill_if_health_is_zero()