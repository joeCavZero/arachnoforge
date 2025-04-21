import motor.api
import motor.object
import pygame as pg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import game.characters.spider

class EnemyExplosion(motor.object.Object):
    def __init__(self, x: int, y: int):
        super().__init__("Explosion", 7, x, y, 0, 0)
        self.radius: float = 0
        self.can_damage = True
    def init(self):
        if self.is_on_screen() or True:

            player: 'game.characters.spider.Spider' = motor.api.get_scene().get_object_by_name("player")
            if player:
                vol = max(0.3 - player.get_center_position().distance_to(self.position) / 1000, 0)
                motor.api.play_sound("assets/sounds/explosion.wav", volume=vol)
    def update(self, delta_time):
        self.radius += 200 * delta_time
        if self.radius > 50:
            self.destroy()
        if self.can_damage == True:
            ally_list = motor.api.get_scene().get_all_objects_by_tag("ally")
            for ally in ally_list:
                if self.position.distance_to(ally.get_center_position())  <  self.radius:
                    self.can_damage = False
                    ally.damage(1)
    def render(self, canvas, camera):
        pg.draw.circle(
            canvas,
            (255, 0, 77),
            camera.get_relative_position(self.position.x, self.position.y),
            self.radius*camera.zoom,
            width= 4
        )
    
    def is_on_screen(self) -> bool:
        return motor.api.get_camera().is_point_on_screen(self.position.x, self.position.y)