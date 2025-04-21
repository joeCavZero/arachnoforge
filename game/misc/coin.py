import motor
import motor.api
import motor.entity
import pygame as pg
import game.effects.particle

class Coin(motor.entity.Entity):
    def __init__(self, x: float, y: float):
        super().__init__(
            name="coin", 
            layer=10, 
            x=x, y=x, 
            width=32, 
            height=32, 
            angle=0, 
            col_rect_x=0, col_rect_y=0, 
            col_rect_width=32, col_rect_height=32,
            z_index_y_offset=42, 
            anchored=True
        )
    
    def init(self):
        self.load_texture("assets/images/coin-sheet.png")
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0),
                pg.Vector2(32, 0),
                pg.Vector2(64, 0),
                pg.Vector2(96, 0),
                pg.Vector2(128, 0),
                pg.Vector2(160, 0)
            ],
            10,
            loop=True
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")
    
    def destroy(self):
        new_particle = game.effects.particle.Particle(
            self.get_center_position().x,
            self.get_center_position().y,
            lifetime=1,
            particle_quantity=10,
        )
        motor.api.get_scene().add_object(new_particle)
        super().destroy()