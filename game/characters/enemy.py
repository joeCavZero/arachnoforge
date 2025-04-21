import game
import game.characters
import game.characters.character
import pygame as pg
import game.effects
import game.effects.particle
import game.misc.coin
import motor.entity
import motor.api
import motor.math
from typing import TYPE_CHECKING

import motor.timer
if TYPE_CHECKING:
    import game.characters.spider
    import game.misc.web_string
class Enemy(game.characters.character.Character):
    def __init__(self, name: str, layer: int, x: int, y: int,  
                 width: int, height: int, angle: float,
                 col_rect_x: int, col_rect_y: int, col_rect_width: int, col_rect_height: int,
                 health: int, speed: float,
                 tags: list[str] = None,
                 z_index_y_offset: float = 0.0,
                 personal_region_x: float = 0.0,
                personal_region_y: float = 0.0,
                personal_region_width: float = 0.0,
                personal_region_height: float = 0.0,
                ):
        super().__init__(
            name, layer,
            x, y,
            width, height,
            angle,
            col_rect_x, col_rect_y, col_rect_width, col_rect_height,
            health, speed,
            tags=tags,
            z_index_y_offset=z_index_y_offset,
        )
        self.trapped_timer = motor.timer.Timer()
    
    def set_motion_to_closest_ally(self, min_distance: float = 0):
        closest_ally = self.get_closest_ally()
        distance = self.get_center_position().distance_to(closest_ally.get_center_position())
        if closest_ally and distance > min_distance and self.trapped_timer.is_finished():
            self.motion = motor.math.vector2_direction_to_vector2(
                self.get_center_position(),
                closest_ally.get_center_position()
            )
        else:
            self.motion = pg.Vector2(0, 0)
    def kill_if_health_is_zero(self):
        if self.health <= 0:
            new_particle = game.effects.particle.Particle(
                self.get_center_position().x,
                self.get_center_position().y,
                lifetime=2,
                particle_quantity=10,
            )
            self.spawn_coin()
            self.destroy()

    def spawn_coin(self):
        new_coin = game.misc.coin.Coin(0,0)
        new_coin.center_position_by_position(self.get_center_position())
        motor.api.get_scene().add_object(new_coin)

    def get_closest_ally(self) -> motor.entity.Entity | None:
        ally_list: list[motor.entity.Entity] = motor.api.get_scene().get_all_objects_by_tag("ally")
        closest_ally: motor.entity.Entity | None = None
        for ally in ally_list:
            if closest_ally is None:
                closest_ally = ally
            
            weighted_distance = self.get_center_position().distance_to( ally.get_center_position() )
            if ally.name == "flower":
                weighted_distance /= 4
            if weighted_distance   <   self.get_center_position().distance_to(closest_ally.get_center_position()):
                closest_ally = ally
        return closest_ally
    def move_and_collide_with_enemies(self):
        main_tilemap = motor.api.get_scene().get_object_by_name("main-tilemap")
        if main_tilemap:
            enemy_list = motor.api.get_scene().get_all_objects_by_tag("enemy")
            self.move_and_collide(self.motion, main_tilemap, entities=enemy_list)
    
