import pygame as pg
import game.characters
import game.characters.bee
import game.characters.beetle
import game.characters.fly
import game.characters.spider
import game.misc
import game.misc.flower
import game.misc.tree
import game.misc.web_node
import motor.api
import motor.camera
import game.tilemaps
import game.tilemaps.main_tilemap
import motor.entity
from motor.scene import Scene
from motor.tilemap.tilemap import Tilemap
from motor.tilemap.tileset import Tileset
import motor.api
import motor.timer
import random
import math

LINE_SHADOW_OFFSET = pg.Vector2(0, 16)
GREEN_SHADOW_COLOR = (0,75,55)

BLACK_COLOR = (0, 0, 0)
HEALTH_COLOR_1 = (0, 231, 86)
HEALTH_COLOR_2 = (255, 163, 0)
HEALTH_COLOR_3 = (255, 240, 36)
HEALTH_COLOR_4 = (255, 0, 77)

SPAWN_DELAY = 1.5

class GameScene(Scene):
    def __init__(self, name: str):
        super().__init__(
            name,
            camera_width=6400 , camera_height=6400,
            camera_zoom=1
        )
        self.paused = False
        self.camera_mode: int = 1
        self.spawn_enemy_timer = motor.timer.Timer()
        self.pause_background: pg.Surface = None
    
    def init(self):
        tilemap = game.tilemaps.main_tilemap.MainTilemap()
        player = game.characters.spider.Spider(400, 128)
        wn1 = game.misc.web_node.WebNode(16,64)
        wn2 = game.misc.web_node.WebNode(128,128)
        wn3 = game.misc.web_node.WebNode(64,64)
        beetle = game.characters.beetle.Beetle(200, 200)
        flower = game.misc.flower.Flower(200, 100)
        tree = game.misc.tree.Tree(32, 0)
        self.add_objects(tilemap, player, wn1, wn2, wn3, flower, tree)
        self.spawn_enemy_timer.restart(SPAWN_DELAY)
    
    def update(self, delta_time):
        if motor.api.is_action_just_pressed("pause"):
            self.paused = not self.paused
            if self.paused:
                bkg = motor.api.get_motor().canvas.copy()
                bkg.set_alpha(55)
                self.pause_background = bkg
            else:
                self.pause_background = None
        if not self.paused:
            self.update_running_game(delta_time)
    def update_running_game(self, delta_time: float):
        self.z_index_layer_by_y(10)
        if motor.api.is_action_just_pressed("camera-mode"):
            self.camera_mode += 1
            if self.camera_mode > 3:
                self.camera_mode = 0

            match self.camera_mode:
                case 0:
                    motor.api.get_camera().zoom = 2
                case 1:
                    motor.api.get_camera().zoom = 1
                case 2:
                    motor.api.get_camera().zoom = 0.5
                case 3:
                    motor.api.get_camera().zoom = 0.25

        if self.spawn_enemy_timer.is_finished():
            tree_list = motor.api.get_scene().get_all_objects_by_name("tree")
            choosen_tree = random.choice(tree_list)
            choosen_tree.spawn( random.choice([0, 1, 2]) )
            self.spawn_enemy_timer.restart(SPAWN_DELAY)

        main_tilemap = motor.api.get_scene().get_object_by_name("main-tilemap")
        if main_tilemap:
            solid_list = motor.api.get_scene().get_all_objects_by_tag("solid")
            motor.entity.Entity.resolve_all_overlaps(main_tilemap, entities= solid_list)
        self.update_objects(delta_time)
        self.spawn_enemy_timer.update(delta_time)

    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        if self.paused:
            canvas.blit(self.pause_background, (0, 0))
        else:
            self.render_shadows(canvas, camera)
            self.render_objects(canvas, camera)
            self.render_gui(canvas, camera)

        
    def render_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
        flower: 'game.misc.flower.Flower' = motor.api.get_scene().get_object_by_name("flower")
        if flower:
            # draw the flower health bar
            background_bar_rect = pg.Rect(
                24, 12,
                224,
                10
            )
            pg.draw.rect(
                canvas,
                BLACK_COLOR,
                background_bar_rect
            )

            percent = flower.health / flower.max_health
            health_bar_rect = pg.Rect(
                24, 12,
                224 * percent,
                10
            )

            health_color = HEALTH_COLOR_1
            if percent < 0.5:
                health_color = HEALTH_COLOR_2
            if percent < 0.25:
                health_color = HEALTH_COLOR_3
            if percent < 0.1:
                health_color = HEALTH_COLOR_4

            pg.draw.rect(
                canvas,
                health_color,
                health_bar_rect
            )
        
            flower_bar = motor.api.get_texture("assets/images/flower-bar.png")
            canvas.blit(
                flower_bar,
                (8, 8)
            )

        player: 'game.characters.spider.Spider' = motor.api.get_scene().get_object_by_name("player")
        if player:
            # draw the player health bar
            background_bar_rect = pg.Rect(
                24, 28,
                192,
                10
            )
            pg.draw.rect(
                canvas,
                BLACK_COLOR,
                background_bar_rect
            )

            percent = player.health / player.max_health
            health_bar_rect = pg.Rect(
                24, 28,
                192 * percent,
                10
            )
            health_color = HEALTH_COLOR_1
            if percent < 0.5:
                health_color = HEALTH_COLOR_2
            if percent < 0.25:
                health_color = HEALTH_COLOR_3
            if percent < 0.1:
                health_color = HEALTH_COLOR_4

            pg.draw.rect(
                canvas,
                health_color,
                health_bar_rect
            )

            spider_bar = motor.api.get_texture("assets/images/spider-bar.png")
            canvas.blit(
                spider_bar,
                (8, 24)
            )
    def render_shadows(self, canvas: pg.Surface, camera: motor.camera.Camera):
        web_line_list = motor.api.get_scene().get_all_objects_by_tag("web-string")
        for web_line in web_line_list:
            if web_line.first_web_node and web_line.second_web_node:
                pg.draw.line(
                    canvas,
                    GREEN_SHADOW_COLOR,
                    camera.get_relative_position_by_vector2(web_line.first_web_node.get_center_position()+LINE_SHADOW_OFFSET),
                    camera.get_relative_position_by_vector2(web_line.second_web_node.get_center_position()+LINE_SHADOW_OFFSET),
                    int(camera.get_relative_scalar(web_line.resistance))
                )
        player: 'game.characters.spider.Spider' = motor.api.get_scene().get_object_by_name("player")
        if player:
            player_rect = player.get_rect()
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect(
                    int(player_rect.x),
                    int(player_rect.y +25),
                    player_rect.width,
                    player_rect.height/2
                )
            )
            for leg in player.legs:
                pg.draw.line(
                    canvas,
                    GREEN_SHADOW_COLOR,
                    camera.get_relative_position_by_vector2(player.get_center_position() + LINE_SHADOW_OFFSET),
                    camera.get_relative_position_by_vector2(leg.position),
                    int(camera.get_relative_scalar(3))
                )
            player_selected_web_node: game.misc.web_node.WebNode = motor.api.get_scene().get_object_by_uid(player.selected_web_node_uid)
            if player_selected_web_node:
                pg.draw.line(
                    canvas,
                    GREEN_SHADOW_COLOR,
                    camera.get_relative_position_by_vector2(player_selected_web_node.get_center_position() + LINE_SHADOW_OFFSET),
                    camera.get_relative_position_by_vector2(player.get_center_position() + pg.Vector2(0, 10)),
                    2
                )
        flower: 'game.misc.flower.Flower' = motor.api.get_scene().get_object_by_name("flower")
        if flower:
            
            shadow_rect = pg.Rect(
                flower.position.x,
                flower.position.y + 50,
                flower.size.x,
                flower.size.y/4
            )
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )
        enemy_list = motor.api.get_scene().get_all_objects_by_tag("enemy")
        for enemy in enemy_list:
            shadow_rect = pg.Rect(
                enemy.position.x,
                enemy.position.y + 60,
                enemy.size.x,
                enemy.size.y/4
            )
            if enemy.name == "beetle":
                shadow_rect.y = enemy.position.y + 28
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )
        
        coin_list = motor.api.get_scene().get_all_objects_by_name("coin")
        for coin in coin_list:
            shadow_rect = pg.Rect(
                coin.position.x,
                coin.position.y + 40,
                coin.size.x,
                coin.size.y/4
            )
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )