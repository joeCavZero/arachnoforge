import pygame as pg
import pygame.gfxdraw
import game.characters
import game.characters.enemy
import game.effects
import game.effects.particle
import motor
import motor.api
import motor.camera
import motor.entity
import motor.math
import motor.object
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import game.misc.web_node

STRING_COLOR = (255, 255, 255)

class WebString(motor.object.Object):
    def __init__(self, first_web_node_uid: int, second_web_node_uid: int):
        super().__init__(
            name="web-string",
            layer=10,
            x=0, y=0,
            width=0, height=0,
            tags=["web-string"]
        )
        self.resistance = 1
        self.first_web_node_uid: int = first_web_node_uid
        self.second_web_node_uid: int = second_web_node_uid

        self.first_web_node: 'game.misc.web_node.WebNode' | None = None
        self.second_web_node: 'game.misc.web_node.WebNode' | None = None

    def init(self):
        self.first_web_node = motor.api.get_scene().get_object_by_uid(self.first_web_node_uid)
        self.second_web_node = motor.api.get_scene().get_object_by_uid(self.second_web_node_uid)
        self.spawn_particles_on_nodes()

    def update(self, delta_time):
        self.first_web_node: 'game.misc.web_node.WebNode' = motor.api.get_scene().get_object_by_uid(self.first_web_node_uid)
        self.second_web_node: 'game.misc.web_node.WebNode' = motor.api.get_scene().get_object_by_uid(self.second_web_node_uid)
        enemy_list: list['game.characters.enemy.Enemy'] = motor.api.get_scene().get_all_objects_by_tag("enemy")
        for enemy in enemy_list:
            if self.is_colliding_with_rect(enemy.get_collision_rect()) and enemy.trapped_timer.is_finished():
                enemy.damage(1)
                enemy.trapped_timer.restart(1)
                self.decrease_resistance(1)
    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        
        if self.first_web_node and self.second_web_node:
            first_position = camera.get_relative_position_by_vector2(self.first_web_node.get_center_position())
            second_position = camera.get_relative_position_by_vector2(self.second_web_node.get_center_position())
            middle_point = pg.Vector2(
                (self.first_web_node.get_center_position().x + self.second_web_node.get_center_position().x) / 2,
                (self.first_web_node.get_center_position().y + self.second_web_node.get_center_position().y) / 2
            )
            middle_point = camera.get_relative_position_by_vector2(middle_point)

            match self.resistance:
                case 1:
                    middle_point = middle_point + pg.Vector2(0, 20)
                    pygame.gfxdraw.bezier(
                    canvas,
                    [first_position, middle_point, second_position],
                    3,
                    STRING_COLOR
                    )
                case 2:
                    middle_point = middle_point + pg.Vector2(0, 10)
                    pygame.gfxdraw.bezier(
                    canvas,
                    [first_position, middle_point, second_position],
                    3,
                    STRING_COLOR
                    )
                case 3:
                    line_width = int(camera.get_relative_scalar(1))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 4:
                    line_width = int(camera.get_relative_scalar(2))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 5:
                    line_width = int(camera.get_relative_scalar(3))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 6:
                    line_width = int(camera.get_relative_scalar(4))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 7:
                    line_width = int(camera.get_relative_scalar(5))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 8:
                    line_width = int(camera.get_relative_scalar(6))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 9:
                    line_width = int(camera.get_relative_scalar(7))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case 10:
                    line_width = int(camera.get_relative_scalar(8))
                    pg.draw.line(canvas, STRING_COLOR, first_position, second_position, line_width)
                case _:
                    raise ValueError("Invalid resistance value")
    def increase_resistance(self, amount: int = 1):
        self.spawn_particles_on_nodes()
        self.resistance = min(self.resistance + amount, 10)
    def decrease_resistance(self, amount: int = 1):
        self.resistance = max(self.resistance - amount, 0)
        self.spawn_particles_on_nodes()
        if self.resistance <= 0:
            self.destroy()

    def destroy(self):
        motor.api.get_scene().delete_object_by_uid(self.uid)
        
    def is_colliding_with_rect(self, rect: pg.Rect) -> bool:
        if self.first_web_node and self.second_web_node:
            return motor.math.line_rect_collision(
                self.first_web_node.get_center_position(),
                self.second_web_node.get_center_position(),
                rect
            )
        return False
    
    def spawn_particles_on_nodes(self):
        if self.first_web_node and self.second_web_node:
            first_web_node_center = self.first_web_node.get_center_position()
            particle1 = game.effects.particle.Particle(
                first_web_node_center.x,
                first_web_node_center.y,
                particle_quantity=5
            )
            motor.api.get_scene().add_object(particle1)

            second_web_node_center = self.second_web_node.get_center_position()
            particle2 = game.effects.particle.Particle(
                second_web_node_center.x,
                second_web_node_center.y,
                particle_quantity=5
            )
            motor.api.get_scene().add_object(particle2)