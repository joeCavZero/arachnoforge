import motor.particle_emitter
class Particle(motor.particle_emitter.ParticleEmitter):
    def __init__(self, x: float, y: float, speed: float = 30, lifetime: float = 0.5, particle_quantity: int = 1):
        super().__init__(
            name="particle",
            layer=15,
            x=x, y=y,
            texture_path="assets/images/particle.png",
            speed=speed,
            lifetime=lifetime,
            particle_quantity=particle_quantity,
            width=8,
            height=8
        )