import game.items
import game.items.item
import pygame as pg

class ShootTimeCard(game.items.item.Item):
    def __init__(self, x: float, y: float):
        super().__init__(
            name="shoot-time-card",
            x=x, y=y,
            texture_path="assets/images/shoot-time-card.png",
            overlapping_message="LESS SHOOT DELAY - 100 COINS",
        )
        self.rotation_direction = 1

    def take(self, actual_shoot_speed: int):
        if actual_shoot_speed <= 0.1:
            self.destroy()