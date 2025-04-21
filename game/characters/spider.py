import game
import game.characters
import game.characters.character
import pygame.gfxdraw
import game.misc
import game.misc.spider_shoot
import game.misc.web_node
import game.misc.web_string
import motor
import motor.animation
import pygame as pg
import math
import motor.api
import motor.camera
import random
from typing import TYPE_CHECKING

import motor.timer
if TYPE_CHECKING:
    import game.characters.spider

LEG_COLOR_1 = (0,0,0)
LEG_COLOR_2 = (29,43,83)

WEB_NODE_SPAWN_DELAY = 1
INCREASE_WEB_STRING_DELAY = 0.5

MORE_SHOOTS_CARD_PRICE = 200
SHOOT_TIME_CARD_PRICE = 100

class Leg:
    def __init__(self, area_x: float, area_y: float, area_width: float, area_height: float, tight_x: float = 0, tight_y: float = 0, front: bool = False, right: bool = False):
        self.area = pg.FRect(area_x, area_y, area_width, area_height)
        self.target_position = pg.Vector2(0, 0)
        self.position = pg.Vector2(0, 0)
        self.knee_position = pg.Vector2(0, 0)
        self.tight_offset = pg.Vector2(tight_x, tight_y)

        self.length1 = 20
        self.length2 = 20

        self.movement_counter: float = 1

        self.front = front
        self.right = right
    def is_movement_finished(self) -> bool :
        return self.movement_counter <= 0.0
    def update(self, delta_time, player):
        if self.movement_counter > 0.0:
            self.movement_counter -= delta_time

        base_pos = player.get_center_position() + self.tight_offset
        target_pos = self.target_position
        

        def inverse_kinematics(
            base: pg.Vector2,
            target: pg.Vector2,
            l1: float,
            l2: float,
            center_pos: pg.Vector2  # <- referência ainda pode ser útil
        ) -> tuple[pg.Vector2, pg.Vector2]:
            d = target - base
            distance = d.length()
            max_reach = l1 + l2
            min_reach = abs(l1 - l2)

            if distance > max_reach:
                d = d.normalize() * max_reach
                target = base + d
                distance = max_reach
            elif distance < min_reach:
                d = d.normalize() * min_reach if d.length() > 0 else pg.Vector2(0, 0)
                target = base + d
                distance = min_reach

            direction = d.normalize() if d.length() > 0 else pg.Vector2(0, 0)
            mid = base + direction * (distance * 0.5)
            h = math.sqrt(max(l1**2 - (distance * 0.5)**2, 0))

            # Perpendicular
            perp = pg.Vector2(-direction.y, direction.x)

            # Testa os dois lados e escolhe o que mantém o joelho acima
            knee_pos_a = mid + perp * h
            knee_pos_b = mid - perp * h

            # Escolhe aquele cujo Y é menor (mais acima)
            knee_pos = knee_pos_a if knee_pos_a.y < knee_pos_b.y else knee_pos_b

            # Calcula posição do pé
            foot_dir = (target - knee_pos).normalize() if (target - knee_pos).length() > 0 else pg.Vector2(0, 0)
            foot_pos = knee_pos + foot_dir * l2

            return knee_pos, foot_pos

        knee_pos, foot_pos = inverse_kinematics(base_pos, target_pos, self.length1, self.length2, player.get_center_position())
        
        LERP = 0.5
        self.position.x = pg.math.lerp(self.position.x, foot_pos.x,  LERP)
        self.position.y = pg.math.lerp(self.position.y, foot_pos.y, LERP)
        self.knee_position.x = pg.math.lerp(self.knee_position.x, knee_pos.x,  LERP)
        self.knee_position.y = pg.math.lerp(self.knee_position.y,knee_pos.y,  LERP)

    def render(self, canvas: pg.Surface, camera: 'motor.camera.Camera', player: 'game.characters.spider.Spider'):
        
        base_pos = player.get_center_position() + self.tight_offset 

        pg.draw.line(canvas, LEG_COLOR_1, camera.get_relative_position_by_vector2(player.get_center_position()), camera.get_relative_position_by_vector2(base_pos), width=int(camera.get_relative_scalar(5)))

        pg.draw.line(canvas, LEG_COLOR_1, camera.get_relative_position_by_vector2(base_pos), camera.get_relative_position_by_vector2(self.knee_position), width=int(camera.get_relative_scalar(3)))
        pg.draw.line(canvas, LEG_COLOR_1, camera.get_relative_position_by_vector2(self.knee_position), camera.get_relative_position_by_vector2(self.position), width=int(camera.get_relative_scalar(3)))
        pg.draw.circle(canvas, LEG_COLOR_1, camera.get_relative_position_by_vector2(self.knee_position), camera.get_relative_scalar(3))
        pg.draw.circle(canvas, LEG_COLOR_1, camera.get_relative_position_by_vector2(self.position), camera.get_relative_scalar(4))
        
        pg.draw.line(canvas, LEG_COLOR_2, camera.get_relative_position_by_vector2(base_pos), camera.get_relative_position_by_vector2(self.knee_position), width=int(camera.get_relative_scalar(2)))
        pg.draw.line(canvas, LEG_COLOR_2, camera.get_relative_position_by_vector2(self.knee_position), camera.get_relative_position_by_vector2(self.position), width=int(camera.get_relative_scalar(2)))
        pg.draw.circle(canvas, LEG_COLOR_2, camera.get_relative_position_by_vector2(self.knee_position), int(camera.get_relative_scalar(2)))
        pg.draw.circle(canvas, LEG_COLOR_2, camera.get_relative_position_by_vector2(self.position), int(camera.get_relative_scalar(3)))
class Spider(game.characters.character.Character):
    def __init__(self, x: int, y: int):
        super().__init__(
            "player",
            10,
            x, y,
            40, 40,
            0,
            -16, -8, 72, 48,
            health=100, speed=100,
            tags=["ally"],
            z_index_y_offset=40,
        )

        self.coins: int = 5000

        self.mode: int = 0
        self.selected_web_node_uid: int = -1

        self.shoot_quantity: int = 1
        self.shoot_delay: float = 0.5

        self.web_node_spawn_timer = motor.timer.Timer()
        self.increase_web_string_timer = motor.timer.Timer()
        self.shoot_timer = motor.timer.Timer()
        self.buy_card_timer = motor.timer.Timer()
        self.legs: list[Leg] = [
            Leg(
                -40, -40, 40, 20,
                tight_x=-10,
                tight_y=-10,
                front=False,
                right=False
            ),
            Leg(
                -60, -20, 40, 20,
                tight_x=-15,
                tight_y=-5,
                front=False,
                right=False
            ),
            Leg(
                -60, 0, 40, 20,
                tight_x=-15,
                tight_y=5,
                front=True,
                right=False
            ),
            Leg(
                -40, 20, 40, 20,
                tight_x=-10,
                tight_y=10,
                front=True,
                right=False
            ),

            Leg(
                0, -40, 40, 20,
                tight_x=10,
                tight_y=-10,
                front=False,
                right=True
            ),
            Leg(
                20, -20, 40, 20,
                tight_x=15,
                tight_y=-5,
                front=False,
                right=True
            ),
            Leg(
                20, 0, 40, 20,
                tight_x=15,
                tight_y=5,
                front=True,
                right=True
            ),
            Leg(
                0, 20, 40, 20,
                tight_x=10,
                tight_y=10,
                front=True,
                right=True
            )
        ]
    def init(self):
        self.load_texture("assets/images/spider.png")
        idle_animation = motor.animation.Animation(
            "idle",
            [
                pg.Vector2(0, 0)
            ],
            0,
            loop=False
        )
        self.add_animation(idle_animation)
        self.set_animation_by_name("idle")
    
    def update(self, delta_time):

        player_center = self.get_center_position()
        if motor.api.is_action_pressed("up"):
            self.motion.y = -1
        elif motor.api.is_action_pressed("down"):
            self.motion.y = 1
        else:
            self.motion.y = 0

        if motor.api.is_action_pressed("right"):
            self.motion.x = 1
        elif motor.api.is_action_pressed("left"):
            self.motion.x = -1
        else:
            self.motion.x = 0

        if self.motion.length() > 0:
            self.angle = pg.math.lerp(self.angle, self.motion.x * 30, 0.1)
        else:
            self.angle = pg.math.lerp(self.angle, 0, 0.1)

        motor.api.get_camera().center_position(
            player_center.x,
            player_center.y
        )

        web_nodes_list: list[game.misc.web_node.WebNode] = motor.api.get_scene().get_all_objects_by_tag("web-node")
        web_string_list: list['game.misc.web_string.WebString'] = motor.api.get_scene().get_all_objects_by_tag("web-string")
        for web_node in web_nodes_list:
            if web_node.is_colliding_with_rect(self.get_collision_rect()):
                actual_selected_web_node = motor.api.get_scene().get_object_by_uid(self.selected_web_node_uid)
                if actual_selected_web_node and web_node.uid != self.selected_web_node_uid:
                    web_string_between_nodes = None
                    for web_string in web_string_list:
                        if actual_selected_web_node.uid == web_string.first_web_node_uid and web_node.uid == web_string.second_web_node_uid or \
                            actual_selected_web_node.uid == web_string.second_web_node_uid and web_node.uid == web_string.first_web_node_uid:
                            web_string_between_nodes = web_string
                            break 
                    if web_string_between_nodes is None:
                        motor.api.play_sound("assets/sounds/powerup-3.wav", volume=0.1)
                        new_web_string = game.misc.web_string.WebString(
                            actual_selected_web_node.uid,
                            web_node.uid
                        )
                        motor.api.get_scene().add_object(new_web_string)
                        web_string_list.append(new_web_string)
                    elif self.increase_web_string_timer.is_finished() and web_string_between_nodes.resistance < 10:
                        web_string_between_nodes.increase_resistance()
                        motor.api.play_sound("assets/sounds/powerup.wav", volume=0.1)
                        self.increase_web_string_timer.restart(INCREASE_WEB_STRING_DELAY)
                self.selected_web_node_uid = web_node.uid

        moved_direction = pg.Vector2(0, 0)
        main_tilemap = motor.api.get_scene().get_object_by_name("main-tilemap")
        if main_tilemap: 
            moved_direction = self.move_and_collide(
                self.motion * self.speed * delta_time,
                main_tilemap
            )
        '''
            LEG MOVEMENT
        '''
        for leg in self.legs:
            target_pos = player_center + pg.Vector2(leg.tight_offset.x*3, leg.tight_offset.y*2)
            
            MOVEMENT_FACTOR_X_MIN = 9
            MOVEMENT_FACTOR_X_MAX = 15
            MOVEMENT_FACTOR_Y_MIN = 9
            MOVEMENT_FACTOR_Y_MAX = 13
            if moved_direction.x != 0:
                target_pos.x += moved_direction.x * random.uniform(MOVEMENT_FACTOR_X_MIN, MOVEMENT_FACTOR_X_MAX)
            if moved_direction.y != 0:
                target_pos.y += moved_direction.y * random.uniform(MOVEMENT_FACTOR_Y_MIN, MOVEMENT_FACTOR_Y_MAX)
            #if self.motion.x < 0:
            #    target_pos.x -= MOVEMENT_FACTOR_X
            #if self.motion.x > 0:
            #    target_pos.x += MOVEMENT_FACTOR_X
            #if self.motion.y < 0:
            #    target_pos.y -= MOVEMENT_FACTOR_Y
            #if self.motion.y > 0:
            #    target_pos.y += MOVEMENT_FACTOR_Y

            MOVEMENT_DELAY = 0.5
            distance = (player_center + leg.tight_offset).distance_to( leg.position )
            MAX_DISTANCE = leg.length1 + 20
            if distance > MAX_DISTANCE:
                leg.target_position = target_pos
                leg.movement_counter = MOVEMENT_DELAY
            elif leg.is_movement_finished():
                leg.target_position = target_pos
                leg.movement_counter = MOVEMENT_DELAY

        BUY_CARD_DELAY = 0.5
        if motor.api.is_action_just_pressed("action-2"):
            more_shoots_card_list = motor.api.get_scene().get_all_objects_by_name("more-shoots-card")
            for more_shoots_card in more_shoots_card_list:
                if self.coins >= MORE_SHOOTS_CARD_PRICE and more_shoots_card.is_colliding_with_rect(  self.get_collision_rect()  ):
                    self.shoot_quantity = min( self.shoot_quantity + 1, 3 )
                    self.coins -= MORE_SHOOTS_CARD_PRICE
                    motor.api.play_sound("assets/sounds/powerup-2.wav", volume=0.1)
                    more_shoots_card.take(self.shoot_quantity)
                    self.buy_card_timer.restart(BUY_CARD_DELAY)
            
            shoot_time_card_list = motor.api.get_scene().get_all_objects_by_name("shoot-time-card")
            for shoot_time_card in shoot_time_card_list:
                if self.coins >= SHOOT_TIME_CARD_PRICE and shoot_time_card.is_colliding_with_rect(  self.get_collision_rect()  ):
                    self.shoot_delay = max(0.1, self.shoot_delay - 0.1)
                    self.coins -= SHOOT_TIME_CARD_PRICE
                    motor.api.play_sound("assets/sounds/powerup-2.wav", volume=0.1)
                    shoot_time_card.take(self.shoot_delay)
                    self.buy_card_timer.restart(BUY_CARD_DELAY)
        if motor.api.is_action_pressed("action-2") and self.web_node_spawn_timer.is_finished() and self.buy_card_timer.is_finished():
            
            web_node_spawn_block_list = motor.api.get_scene().get_all_objects_by_tag("web-node-spawn-block")
            is_colliding_with_some_web_node_block = False
            for web_node_block in web_node_spawn_block_list:
                if web_node_block.is_colliding_with_rect(self.get_collision_rect()):
                    is_colliding_with_some_web_node_block = True
                    break
            if is_colliding_with_some_web_node_block:
                pass
            else:
                motor.api.play_sound("assets/sounds/placement.wav", volume=0.3)
                new_web_node = game.misc.web_node.WebNode(
                    self.position.x,
                    self.position.y
                )
                motor.api.get_scene().add_object(new_web_node)
                self.web_node_spawn_timer.restart(WEB_NODE_SPAWN_DELAY)

        

        if motor.api.is_action_pressed("action-1") and self.shoot_timer.is_finished():
            motor.api.play_sound("assets/sounds/laser.wav", volume=0.1)
            
            angle = math.degrees(math.atan2(
                    motor.api.get_mouse_world_position().y - self.position.y - self.size.y / 2,
                    motor.api.get_mouse_world_position().x - self.position.x - self.size.x / 2
                ))
            
            match self.shoot_quantity:
                case 1:
                    new_spider_shoot = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot.center_position_by_position(self.get_center_position())
                    motor.api.get_scene().add_object(new_spider_shoot)
                case 2:
                    new_spider_shoot_1 = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot_2 = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot_1.center_position_by_position( self.get_center_position() + pg.Vector2(0, 10).rotate(angle) )
                    new_spider_shoot_2.center_position_by_position( self.get_center_position() + pg.Vector2(0, -10).rotate(angle) )
                    motor.api.get_scene().add_object(new_spider_shoot_1)
                    motor.api.get_scene().add_object(new_spider_shoot_2)
                case 3:
                    new_spider_shoot_1 = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot_2 = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot_3 = game.misc.spider_shoot.SpiderShoot(0,0,angle)
                    new_spider_shoot_1.center_position_by_position( self.get_center_position() + pg.Vector2(0, -30).rotate(angle) )
                    new_spider_shoot_2.center_position_by_position( self.get_center_position() )
                    new_spider_shoot_3.center_position_by_position( self.get_center_position() + pg.Vector2(0, 30).rotate(angle) )
                    motor.api.get_scene().add_object(new_spider_shoot_1)
                    motor.api.get_scene().add_object(new_spider_shoot_2)
                    motor.api.get_scene().add_object(new_spider_shoot_3)

            self.shoot_timer.restart(self.shoot_delay)

        
        coin_list = motor.api.get_scene().get_all_objects_by_name("coin")
        for coin in coin_list:
            if coin.is_colliding_with_rect(self.get_collision_rect()):
                self.coins += 1
                motor.api.play_sound("assets/sounds/coin.wav", volume=0.1)
                coin.destroy()

        

        selected_web_node = motor.api.get_scene().get_object_by_uid(self.selected_web_node_uid)
        if selected_web_node:
            distance = self.get_center_position().distance_to(selected_web_node.get_center_position())
            if distance > 300:
                self.selected_web_node_uid = -1
        for leg in self.legs:
            leg.update(delta_time, self)
        
        self.web_node_spawn_timer.update(delta_time)
        self.increase_web_string_timer.update(delta_time)
        self.shoot_timer.update(delta_time)
        self.buy_card_timer.update(delta_time)
    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        selected_web_node: game.misc.web_node.WebNode = motor.api.get_scene().get_object_by_uid(self.selected_web_node_uid)
        if selected_web_node:
            distance = self.get_center_position().distance_to(selected_web_node.get_center_position())
            thickness = max(1, 3 - min(int(distance / 50), 5))
            #pg.draw.line(
            #    canvas,
            #    (255,255,255),
            #    camera.get_relative_position_by_vector2(selected_web_node.get_center_position()),
            #    camera.get_relative_position_by_vector2(self.get_center_position()),
            #    width=thickness
            #)
            middle_point = pg.Vector2(
                        (selected_web_node.get_center_position().x + self.get_center_position().x) / 2,
                        (selected_web_node.get_center_position().y + self.get_center_position().y) / 2
                    ) + pg.Vector2(0, 20)
            middle_point = camera.get_relative_position_by_vector2(middle_point)
            pygame.gfxdraw.bezier(
                canvas,
                [
                    camera.get_relative_position_by_vector2(selected_web_node.get_center_position()),
                    middle_point,
                    camera.get_relative_position_by_vector2(self.get_center_position())
                ],
                3,
                (255,255,255)
            )
        for leg in self.legs:
            leg.render(canvas, camera, self)
            
        self.render_animation_frame(canvas, camera)

    def damage(self, damage):
        motor.api.play_sound("assets/sounds/hurt.wav", volume=0.5)
        self.health -= damage