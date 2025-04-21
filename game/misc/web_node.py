import pygame as pg
import motor
import motor.animation
import motor.camera
import motor.entity

class WebNode(motor.entity.Entity):
    def __init__(self, x: float, y: float):
        super().__init__(
            name="web-node",
            layer=10,
            x=x, y=y-16,
            width=32, height=32,
            angle=0,
            col_rect_x=8, col_rect_y=0, col_rect_width=16, col_rect_height=32,
            tags=["web-node"],
            z_index_y_offset=32
        )
    
    def init(self):
        self.load_texture("assets/images/web-node.png")
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

    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        self.render_animation_frame(canvas, camera)