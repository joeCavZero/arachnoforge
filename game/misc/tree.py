import game
import game.characters
import game.characters.bee
import game.characters.beetle
import game.characters.fly
import motor
import motor.animation
import motor.api
import motor.entity
import pygame as pg

class Tree(motor.entity.Entity):
    def __init__(self, x: float, y: float):
        super().__init__(
            name="tree",
            layer=10,
            x=x, y=y-16,
            width=256, height=256,
            angle=0,
            col_rect_x=104, col_rect_y=200, col_rect_width=48, col_rect_height=32,
            tags=["tree"],
            z_index_y_offset=240
        )
    
    def init(self):
        self.load_texture("assets/images/tree.png")
        default_animation = motor.animation.Animation(
            "default",
            [
                pg.Vector2(0, 0),
            ],
            0,
            loop=False
        )
        self.add_animation(default_animation)
        self.set_animation_by_name("default")
    def spawn(self, enemy_type: int):
        tree_center = self.get_center_position()
        enemy = None
        match enemy_type:
            case 0:
                enemy = game.characters.fly.Fly(tree_center.x, tree_center.y)
            case 1:
                enemy = game.characters.bee.Bee(tree_center.x, tree_center.y)
            case 2:
                enemy = game.characters.beetle.Beetle(tree_center.x, tree_center.y)
        if enemy:
            motor.api.get_scene().add_object(enemy)