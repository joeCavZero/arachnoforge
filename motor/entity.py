import math
import pygame as pg
import motor.animation
import motor.api
from motor.object import Object
from motor.tilemap.tilemap import Tilemap

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import motor.camera
    import motor.entity

class Entity(Object):
    def __init__(self, name: str, layer: int, x: float, y: float, width: float, height: float, angle: float, col_rect_x: int, col_rect_y: int, col_rect_width: int, col_rect_height: int, tags: list[str] = None, z_index_y_offset: float = 0.0, anchored: bool = True):
        super().__init__(
            name, 
            layer, 
            x, y,
            width, height,
            tags=tags,
            z_index_y_offset=z_index_y_offset
        )
        
        self.collision_rect: pg.Rect = pg.Rect(
            col_rect_x,
            col_rect_y,
            col_rect_width,
            col_rect_height
        )
        self.mirrored: bool = False
        self.anchored: bool = anchored
        self.motion = pg.Vector2(0, 0)
        self.angle = angle
        self.texture: pg.Surface = None
        self.animations: list[motor.animation.Animation] = []
        self.animation: motor.animation.Animation = None
    
    def move_and_collide(self, movement: pg.Vector2, tilemap: Tilemap, entities: list['motor.entity.Entity'] = None) -> pg.Vector2:
        moved_direction = pg.Vector2(0, 0)

        # Movimento no eixo X
        if movement.x != 0:
            self.position.x += movement.x
            rect = self.get_collision_rect()

            if tilemap.is_colliding_with(rect.x, rect.y, rect.width, rect.height) or self._is_colliding_with_entities(rect, entities):
                self.position.x -= movement.x
            else:
                moved_direction.x = movement.x

        # Movimento no eixo Y
        if movement.y != 0:
            self.position.y += movement.y
            rect = self.get_collision_rect()

            if tilemap.is_colliding_with(rect.x, rect.y, rect.width, rect.height) or self._is_colliding_with_entities(rect, entities):
                self.position.y -= movement.y
            else:
                moved_direction.y = movement.y

        return moved_direction

    def _is_colliding_with_entities(self, rect: pg.FRect, entities: list['motor.entity.Entity']) -> bool:
        if entities:
            for entity in entities:
                if entity != self and entity.get_collision_rect().colliderect(rect):
                    return True
        return False
    
    def resolve_overlap(self, other_rect: pg.FRect, tilemap: Tilemap, entities: list['motor.entity.Entity'] = None) -> bool:
        if self.anchored:
            return False

        rect = self.get_collision_rect()

        dx = (rect.centerx - other_rect.centerx)
        dy = (rect.centery - other_rect.centery)

        overlap_x = (rect.width / 2 + other_rect.width / 2) - abs(dx)
        overlap_y = (rect.height / 2 + other_rect.height / 2) - abs(dy)

        if overlap_x <= 0 or overlap_y <= 0:
            return False  # Sem sobreposição

        separation = pg.Vector2(0, 0)
        margin = 0.1

        if overlap_x < overlap_y:
            separation.x = (overlap_x + margin) * (-1 if dx < 0 else 1)
        else:
            separation.y = (overlap_y + margin) * (-1 if dy < 0 else 1)

        new_pos = self.position + separation

        test_rect = pg.FRect(
            new_pos.x + self.collision_rect.x,
            new_pos.y + self.collision_rect.y,
            self.collision_rect.width,
            self.collision_rect.height
        )

        if not tilemap.is_colliding_with(test_rect.x, test_rect.y, test_rect.width, test_rect.height):
            self.position = new_pos
            return True

        return False

    @staticmethod
    def resolve_all_overlaps(tilemap: Tilemap, entities: list['motor.entity.Entity'] = None):
        if entities is None:
            return

        max_iterations = 10
        for _ in range(max_iterations):
            moved = False

            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    a = entities[i]
                    b = entities[j]

                    rect_a = a.get_collision_rect()
                    rect_b = b.get_collision_rect()

                    if rect_a.colliderect(rect_b):
                        # Tenta resolver a colisão para o primeiro, se falhar tenta o segundo
                        if not a.anchored and a.resolve_overlap(rect_b, tilemap, entities):
                            moved = True
                        elif not b.anchored and b.resolve_overlap(rect_a, tilemap, entities):
                            moved = True

            if not moved:
                break
    def add_animation(self, animation: motor.animation.Animation):
        self.animations.append(animation)
    
    def set_animation_by_name(self, name: str):
        for animation in self.animations:
            if animation.name == name:
                self.animation = animation
                break

    def get_collision_rect(self) -> pg.FRect:
        return pg.FRect(
            self.position.x + self.collision_rect.x,
            self.position.y + self.collision_rect.y,
            self.collision_rect.width,
            self.collision_rect.height
        )
    
    def get_animation_frame_subtexture(self, camera: 'motor.camera.Camera' = None) -> pg.Surface | None:
        if self.animation is not None:
            if camera is None:
                return self.texture.subsurface(
                    self.animation.get_actual_frame_rect(
                        self.size.x,
                        self.size.y
                    )
                )
            else:
                try:
                    sub_surface = self.texture.subsurface(
                            self.animation.get_actual_frame_rect(
                                self.size.x,
                                self.size.y
                            )
                        )
                    if self.mirrored:
                        sub_surface = pg.transform.flip(sub_surface, True, False)
                    return sub_surface
                except Exception as e:
                    ValueError(f"Animation error with object {self.name}: {e}")
        return None
    
    def update(self, delta_time):
        if self.animation is not None:
            self.animation.update(delta_time)
    
    def render(self, canvas, camera):
        self.render_animation_frame(canvas, camera)
    
    def render_animation_frame(self, canvas: pg.Surface, camera: motor.camera.Camera):
        if not camera.is_rect_on_screen_by_rect(self.get_rect()):
            return
        sub_texture = self.get_animation_frame_subtexture(camera)
        size_to_scale = camera.get_relative_size_by_vector2(self.size)
        size_to_scale.x = math.ceil(size_to_scale.x)
        size_to_scale.y = math.ceil(size_to_scale.y)
        if sub_texture is not None:
            sub_texture = pg.transform.scale(
                        sub_texture,
                        size_to_scale
                    )
            sub_texture = pg.transform.rotate(sub_texture, -self.angle)
            relative_position = camera.get_relative_position(
                self.position.x,
                self.position.y,
            )

            pixel_scale = motor.api.get_motor().pixel_scale
            canvas.blit(
                sub_texture,
                pg.FRect(
                    relative_position.x - (sub_texture.get_width()/2) + (self.size.x/2)*camera.zoom*pixel_scale,
                    relative_position.y - (sub_texture.get_height()/2) + (self.size.y/2)*camera.zoom*pixel_scale,
                    sub_texture.get_width(),
                    sub_texture.get_height()
                )
            )
    
    def is_colliding_with(self, x: int, y: int, width: int, height: int) -> bool:
        return self.get_collision_rect().colliderect(pg.Rect(x, y, width, height))
    
    def is_colliding_with_rect(self, rect: pg.Rect) -> bool:
        return self.is_colliding_with(rect.x, rect.y, rect.width, rect.height)
    
    def is_colliding_with_point(self, x: int, y: int) -> bool:
        return self.get_collision_rect().collidepoint(x, y)
    
    def is_colliding_with_point_by_vector2(self, vector: pg.Vector2) -> bool:
        return self.is_colliding_with_point(vector.x, vector.y)
    
    def load_texture(self, path: str):
        self.texture = motor.api.get_texture(path)
    
    def render_collision_rect(self, canvas: pg.Surface, camera: motor.camera.Camera):
        pg.draw.rect(
            canvas,
            (255, 0, 0),
            camera.get_relative_rect_by_rect(self.get_collision_rect()),
            1
        )