import motor.api
import motor.object
import math
import pygame as pg
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import motor.camera

class Particle:
    def __init__(self, x: int, y: int, angle: float, texture: pg.Surface, speed: float, lifetime: float, width: float = 32, height: float = 32):
        self.x = x
        self.y = y
        self.angle = angle
        self.texture = texture
        self.speed = speed
        self.lifetime = lifetime
        self.offset = pg.Vector2(
            -self.texture.get_width() / 2,
            -self.texture.get_height() / 2
        )
        self.size = pg.Vector2(width, height)

    def update(self, delta_time: float):
        if self.lifetime > 0:
            self.x += self.speed * delta_time * math.cos(math.radians(self.angle))
            self.y += self.speed * delta_time * math.sin(math.radians(self.angle))
            self.lifetime -= delta_time

    def render(self, canvas: pg.Surface, camera: 'motor.camera.Camera'):
        
        relative_position = camera.get_relative_position(self.x+self.offset.x, self.y+self.offset.y)
        scaled_texture = pg.transform.scale(
            self.texture,
            camera.get_relative_size(self.size.x, self.size.y)
        )
        canvas.blit(scaled_texture, relative_position)

class ParticleEmitter(motor.object.Object):
    def __init__(self, name: str, layer: int, x: int, y: int, texture_path: str, speed: float, lifetime: float, particle_quantity: float, width: float = 32, height: float = 32):
        super().__init__(name, layer, x, y, width, height)
        self.texture_path = texture_path
        self.speed = speed
        self.lifetime = lifetime
        self.particle_quantity = particle_quantity
        self.particles: list[Particle] = []

    def init(self):
        texture = motor.api.get_texture(self.texture_path)
 
        int_part = int(self.particle_quantity)
        frac_part = self.particle_quantity - int_part

        for _ in range(int_part):
            particle = Particle(
                self.position.x, self.position.y, 
                random.uniform(0, 360),
                texture, 
                self.speed, 
                self.lifetime,
                width=self.size.x,
                height=self.size.y
            )
            self.particles.append(particle)

        
        if random.random() < frac_part:
            particle = Particle(
                self.position.x, self.position.y, 
                random.uniform(0, 360),
                texture, 
                self.speed, 
                self.lifetime,
                width=self.size.x,
                height=self.size.y
            )
            self.particles.append(particle)
    
    def update(self, delta_time: float):
        for i, particle in enumerate(self.particles):
            particle.update(delta_time)
            if particle.lifetime <= 0:
                self.particles.pop(i)
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            motor.api.get_scene().delete_object_by_uid(self.uid)
    
    def render(self, canvas: pg.Surface, camera: 'motor.camera.Camera'):
        for particle in self.particles:
            particle.render(canvas, camera)