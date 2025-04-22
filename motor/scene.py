import motor
from motor.object import Object
import pygame as pg
import math
import numba
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import motor.camera

class Scene:
    def __init__(
            self, name: str,
            camera_x: int = 0, camera_y: int = 0,
            camera_width: int = 32000, camera_height: int = 32000,
            camera_zoom: float = 1.0,
        ):
        self.name = name
        self.camera = motor.camera.Camera(
            camera_x, camera_y, 
            camera_zoom, 
            camera_width, camera_height
        )
        self.objects: list[Object] = []

        self.uid_counter: int = 0

    def init(self):
        pass

    def update(self, delta_time: float):
        self.update_objects(delta_time)

    def render(self, canvas: pg.Surface, camera: 'motor.camera.Camera'):
        self.render_objects(canvas, camera)

    def update_objects(self, delta_time: float):
        for obj in self.objects:
            obj.update(delta_time)
    
    def render_objects(self, canvas: pg.Surface, camera: 'motor.camera.Camera'):
        sorted_by_layer_object = sorted(self.objects, key=lambda obj: obj.layer)
        for obj in sorted_by_layer_object:
            obj.render(canvas, camera)
    def add_object(self, obj: Object) -> int:
        self.objects.append(obj)
        obj.uid = self.shift_uid()
        obj.init()
        return obj.uid
    def add_objects(self, *objects: Object):
        for obj in objects:
            self.add_object(obj)
    def get_object_by_name(self, name: str) -> Object | None:
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
    
    def get_object_by_uid(self, uid: int) -> Object | None:
        for obj in self.objects:
            if obj.uid == uid:
                return obj
        return None
    
    def delete_object_by_uid(self, uid: int) -> bool:
        for i, obj in enumerate(self.objects):
            if obj.uid == uid:
                del self.objects[i]
                return True
        return False

    def shift_uid(self) -> int:
        self.uid_counter += 1
        return self.uid_counter - 1

    def get_all_objects_by_name(self, *name: str) -> list[Object]:
        objects = []
        for obj in self.objects:
            if obj.name in name:
                objects.append(obj)
        return objects
    def get_all_objects_by_tag(self, *tag: str) -> list[Object]:
        objects = []
        for obj in self.objects:
            for t in tag:
                if obj.has_tag(t):
                    objects.append(obj)
        return objects
    
    
    def z_index_layer_by_y(self, layer: int):
        objects = list(filter(lambda obj: math.floor(obj.layer) == layer, self.objects))
        
        sorted_objects = sorted(objects, key=lambda obj: obj.position.y + obj.z_index_y_offset)
        layer_increment = 1 / 10000
        for i, obj in enumerate(sorted_objects):
            obj.layer = layer + min(i * layer_increment, 1)
    def close(self):
        pass