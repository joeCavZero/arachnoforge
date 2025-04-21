import game
import game.characters
import game.characters.character
import pygame as pg
import game.characters.enemy
import game.misc.enemy_explosion
import motor.animation
import motor.api
import motor.camera
import motor.math
from typing import TYPE_CHECKING

import motor.timer
if TYPE_CHECKING:
    import game.characters.spider
    import game.misc.web_string


STOP_DISTANCE = 15
ATTACK_DISTANCE = 128
ATTACK_DELAY = 1.5
class Fly(game.characters.enemy.Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(
            "fly",
            10,
            x, y,
            64, 64,
            0,
            16, 16, 32, 32,
            health=3, speed=100,
            tags=["enemy", "solid"],
            z_index_y_offset=64,
        )
        self.attack_timer = motor.timer.Timer()
    def init(self):
        self.load_texture("assets/images/fly-sheet.png")
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0),
                pg.Vector2(64, 0),
            ],
            10,
            loop=True
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")
    
    def update(self, delta_time):
        self.set_motion_to_closest_ally(min_distance=STOP_DISTANCE)

        
        if self.motion.length() > 0:
            if self.motion.x < 0:
                self.mirrored = True
            else:
                self.mirrored = False
            self.angle = pg.math.lerp(self.angle, self.motion.x * 30, 0.1)
        else:
            self.angle = pg.math.lerp(self.angle, 0, 0.1)
        
        if self.attack_timer.is_finished():
            closest_ally = self.get_closest_ally()
            if closest_ally and self.get_center_position().distance_to(closest_ally.get_center_position()) <= ATTACK_DISTANCE:
                new_enemy_explosion = game.misc.enemy_explosion.EnemyExplosion(
                    self.get_center_position().x,
                    self.get_center_position().y
                )
                motor.api.get_scene().add_object(new_enemy_explosion)
                self.attack_timer.restart(ATTACK_DELAY)
        
        self.move_and_collide_with_enemies()
        self.attack_timer.update(delta_time)
        self.trapped_timer.update(delta_time)
        self.animation.update(delta_time)
    
    def damage(self, damage):
        self.health -= damage
        self.kill_if_health_is_zero()
