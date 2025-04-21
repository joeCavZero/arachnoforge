import game.characters
import game.characters.spider
import motor
import motor.animation
import motor.api
import motor.camera
import motor.entity
import pygame as pg
import game.effects.particle

class Item(motor.entity.Entity):
    def __init__(self, name: str, x: float, y: float, texture_path: str, overlapping_message: str = "", tags: list[str] = None):
        if tags is None:
            tags = []
        tags.extend(["item", "web-node-spawn-block"])
        
        super().__init__(
            name=name, 
            layer=10, 
            x=x, y=x, 
            width=32, 
            height=40, 
            angle=0, 
            col_rect_x=0, col_rect_y=0, 
            col_rect_width=32, col_rect_height=40,
            z_index_y_offset=52, 
            tags=tags,
            anchored=True
        )
        self.rotation_direction = 1
        self.texture_path = texture_path
        self.overlapping_message = overlapping_message
    def take(self, player: game.characters.spider.Spider):
        new_particle = game.effects.particle.Particle(
            self.get_center_position().x,
            self.get_center_position().y,
            lifetime=1,
            particle_quantity=10,
        )
        motor.api.get_scene().add_object(new_particle)
        self.destroy()
        
    def init(self):
        self.load_texture(self.texture_path)
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0)
            ],
            0,
            loop=False
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")

    def update(self, delta_time):
        self.rotate(delta_time)
    def rotate(self, delta_time: float):
        if self.angle >= 20:
            self.rotation_direction = -1
        elif self.angle <= -20:
            self.rotation_direction = 1
        self.angle += self.rotation_direction*delta_time*60

    def render_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
        font = motor.api.get_font("assets/fonts/Symtext.ttf")
        font_render = font.render(
            self.overlapping_message,
            False,
            (255, 255, 255)
        )
        value_to_scale = camera.get_relative_scalar(0.5)
        font_render = pg.transform.scale(
            font_render,
            (int(font_render.get_width()*value_to_scale), int(font_render.get_height()*value_to_scale))
        )
        font_rect = font_render.get_rect()
        relative_position = camera.get_relative_position_by_vector2(self.get_center_position())
        font_rect.x = int(relative_position.x - font_rect.width / 2)
        font_rect.y = int(relative_position.y - font_rect.height / 2 - camera.get_relative_scalar(40))
        canvas.blit(font_render, font_rect)