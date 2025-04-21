import motor
import motor.entity

class Character(motor.entity.Entity):
    def __init__(self, name: str, layer: int, x: int, y: int,  
                width: int, height: int, angle: float,
                col_rect_x: int, col_rect_y: int, col_rect_width: int, col_rect_height: int,
                health: int, speed: float,
                anchored: bool = False,
                tags: list[str] = None,
                z_index_y_offset: float = 0.0,
                personal_region_x: float = 0.0,
                personal_region_y: float = 0.0,
                personal_region_width: float = 0.0,
                personal_region_height: float = 0.0,
                ):
        if tags is None:
            tags = []
        tags.append("character")
        super().__init__(
            name, layer,
            x, y,
            width, height,
            angle,
            col_rect_x, col_rect_y, col_rect_width, col_rect_height,
            tags=tags,
            z_index_y_offset=z_index_y_offset,
            anchored=anchored,
        )
        self.health = health
        self.max_health = health
        self.speed = speed
    
    def damage(self, damage: int):
        self.health -= damage