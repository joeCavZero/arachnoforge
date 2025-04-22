import game.characters
import game.characters.character
import game.effects
import game.effects.explosion
import game.tilemaps
import game.tilemaps.main_tilemap
import motor
import game
import motor.animation
import motor.api
import motor.camera
import motor.entity
import math
import pygame as pg
class BeeShoot(motor.entity.Entity):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            name="bee-shoot",
            layer=10,
            x=x, y=y,
            width=16, height=16,
            angle=angle,
            col_rect_x=0, col_rect_y=0, col_rect_width=16, col_rect_height=16,
            tags=["bee-shoot", "shoot"],
            z_index_y_offset=16
        )
        self.speed = 200
        self.motion.x = math.cos(math.radians(self.angle))
        self.motion.y = math.sin(math.radians(self.angle))
    
    def init(self):
        self.load_texture("assets/images/bee-shoot.png")
        idle_animation = motor.animation.Animation(
            "idle",
            [
                pg.Vector2(0, 0),
            ],
            0,
            loop=False
        )
        self.add_animation(idle_animation)
        self.set_animation_by_name("idle")
    
    def update(self, delta_time):
        main_tilemap: 'game.tilemaps.main_tilemap.MainTilemap' = motor.api.get_scene().get_object_by_name("main-tilemap")
        if main_tilemap:
            if main_tilemap.is_colliding_with_rect(self.get_collision_rect()):
                self.destroy()
        ally_list: list['game.characters.character.Character'] = motor.api.get_scene().get_all_objects_by_tag("ally")
        for ally in ally_list:
            if ally.is_colliding_with_rect(self.get_collision_rect()):
                ally.damage(1)
                self.destroy()
        self.position += self.motion*delta_time*self.speed
    def destroy(self):
        new_explosion = game.effects.explosion.Explosion(
            self.get_center_position().x,
            self.get_center_position().y,
            max_radius=16
        )
        motor.api.get_scene().add_object(new_explosion)
        motor.api.get_scene().delete_object_by_uid(self.uid)