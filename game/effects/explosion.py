import motor.api
import motor.object
import pygame as pg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import game.characters.spider

class Explosion(motor.object.Object):
    def __init__(self, x: int, y: int, max_radius: int = 50, explosion_sound_path: str = "assets/sounds/explosion.wav"):
        super().__init__("Explosion", 15, x, y, 0, 0)
        self.radius: float = 0
        self.max_radius = max_radius
        self.explosion_sound_path = explosion_sound_path
    def init(self):
        if self.is_on_screen() or True:

            player: 'game.characters.spider.Spider' = motor.api.get_scene().get_object_by_name("player")
            if player:
                vol = max(0.3 - player.get_center_position().distance_to(self.position) / 1000, 0)
                motor.api.play_sound(self.explosion_sound_path, volume=vol)
    def update(self, delta_time):
        self.radius += 200 * delta_time
        if self.radius > self.max_radius:
            self.destroy()
    def render(self, canvas, camera):
        pg.draw.circle(
            canvas,
            (255, 255, 255),
            camera.get_relative_position(self.position.x, self.position.y),
            self.radius*camera.zoom,
            width= 3
        )
    
    def is_on_screen(self) -> bool:
        return motor.api.get_camera().is_point_on_screen(self.position.x, self.position.y)