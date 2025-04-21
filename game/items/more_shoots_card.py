import game.items
import game.items.item
import pygame as pg

class MoreShootsCard(game.items.item.Item):
    def __init__(self, x: float, y: float):
        super().__init__(
            name="more-shoots-card",
            x=x, y=y,
            texture_path="assets/images/more-shoots-card.png",
            overlapping_message="MORE SHOOTS - 200 COINS",
        )
        self.rotation_direction = 1
    
    def take(self, actual_shoot_quantity: int):
        if actual_shoot_quantity >= 3:
            self.destroy()