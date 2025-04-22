import pygame as pg
import numpy as np
import game.characters
import pygame.gfxdraw
import game.characters.spider
import game.items.more_shoots_card
import game.items.shoot_time_card
import game.misc
import game.misc.flower
import game.misc.tree
import game.misc.web_node
import game.scenes
import game.scenes.menu_scene
import game.tilemaps.decoration_tilemap
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

MUSIC_PATHS =[
    "assets/musics/walking-around.wav"
]

MUSIC_VOLUME = 0.4

class GameScene(Scene):
    def __init__(self):
        super().__init__(
            "game-scene",
            camera_width=6400 , camera_height=6400,
            camera_zoom=1
        )
        self.paused = False
        self.camera_mode: int = 1

        self.is_raid_mode: bool = False
        self.raid_level: int = 0
        self.raid_info: np.ndarray = None
        self.spawn_enemy_delay = 3
        self.spawn_enemy_timer = motor.timer.Timer()

        self.death_animation_mode = False
        self.death_animation_timer = motor.timer.Timer()

        self.pause_background: pg.Surface = None

        self.playing_music_channel: pg.Channel|None = None

        self.is_mute = False
    
    def init(self):
        world_size = self.camera.border.copy()
        world_center = pg.Vector2(0, 0)
        world_center.x = world_size.x // 2
        world_center.y = world_size.y // 2
        tilemap = game.tilemaps.main_tilemap.MainTilemap()
        decoration_tilemap = game.tilemaps.decoration_tilemap.DecorationTilemap()
        player = game.characters.spider.Spider(0, 0)
        player.center_position(
            world_center.x,
            world_center.y+100
        )
        flower = game.misc.flower.Flower(0, 0)
        flower.center_position(
            world_center.x,
            world_center.y
        )
        tree1 = game.misc.tree.Tree(0, 0)
        tree1.center_position(
            world_center.x,
            256
        )
        tree2 = game.misc.tree.Tree(0, 0)
        tree2.center_position(
            world_size.x - 256,
            world_center.y
        )
        tree3 = game.misc.tree.Tree(0, 0)
        tree3.center_position(
            world_center.x,
            world_size.y - 256
        )
        tree4 = game.misc.tree.Tree(0, 0)
        tree4.center_position(
            256,
            world_center.y
        )
        more_shoot_card = game.items.more_shoots_card.MoreShootsCard(0,0)
        more_shoot_card.center_position(
            world_center.x-500,
            world_center.y
        )
        shoot_time_card = game.items.shoot_time_card.ShootTimeCard(0, 0)
        shoot_time_card.center_position(
            world_center.x+500,
            world_center.y
        )

        self.camera.center_position(
            player.get_center_position().x,
            player.get_center_position().y
        )

        self.add_objects(
            tilemap, decoration_tilemap, 
            player, 
            more_shoot_card, 
            shoot_time_card, 
            flower, 
            tree1,
            tree2,
            tree3,
            tree4
        )

    def update(self, delta_time):
        self.update_music_system()
        if self.death_animation_mode == True:
            motor.api.get_motor().canvas.set_alpha( max(0, min(255, -100 + self.death_animation_timer.time * 300)) )
            self.death_animation_timer.update(delta_time)
            if self.death_animation_timer.is_finished():
                self.playing_music_channel.stop()
                menu_scene = game.scenes.menu_scene.MenuScene()
                motor.api.get_motor().canvas.set_alpha(255)
                motor.api.set_scene(menu_scene)
        else:
            if motor.api.is_action_just_pressed("pause"):
                motor.api.play_sound("assets/sounds/blip.wav", volume=0.2)
                self.paused = not self.paused
                if self.paused:
                    bkg = motor.api.get_motor().canvas.copy()
                    bkg.set_alpha(55)
                    self.pause_background = bkg
                else:
                    self.pause_background = None
        if not self.paused:
            self.update_running_game(delta_time)
            self.check_deaths()
    def update_running_game(self, delta_time: float):
        self.z_index_layer_by_y(10)
        if motor.api.is_action_just_pressed("camera-mode"):
            motor.api.play_sound("assets/sounds/camera.wav", volume=0.2)

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
            player = motor.api.get_scene().get_object_by_name("player")
            motor.api.get_camera().center_position(
                player.get_center_position().x,
                player.get_center_position().y
            )
        enemy_list = motor.api.get_scene().get_all_objects_by_tag("enemy")
        if motor.api.is_action_just_pressed("raid") and self.is_raid_mode == False and len(enemy_list) <= 0:
            motor.api.play_sound("assets/sounds/blow.wav", volume=0.2)
            self.raid_level += 1
            self.start_raid()
        
        if self.is_raid_mode == True:
            if self.enemy_counter <= 0 and len(enemy_list) <= 0:
                motor.api.play_sound("assets/sounds/done.wav", volume=0.2)
                self.is_raid_mode = False

        if self.is_raid_mode == True:
            if self.spawn_enemy_timer.is_finished() and self.enemy_counter > 0:
                tree_list = motor.api.get_scene().get_all_objects_by_name("tree")
                choosen_tree = random.choice(tree_list)
                choosen_tree.spawn( get_random_enemy_spawn_id(self.raid_info) )
                self.spawn_enemy_timer.restart(self.spawn_enemy_delay)
                self.enemy_counter -= 1
            self.spawn_enemy_timer.update(delta_time)
        main_tilemap = motor.api.get_scene().get_object_by_name("main-tilemap")
        if main_tilemap:
            solid_list = motor.api.get_scene().get_all_objects_by_tag("solid")
            motor.entity.Entity.resolve_all_overlaps(main_tilemap, entities= solid_list)
        

        self.update_objects(delta_time)
    def check_deaths(self):
        DEATH_TIMER_DELAY = 2
        LERP = 0.1
        flower: 'game.misc.flower.Flower' = motor.api.get_scene().get_object_by_name("flower")
        player: 'game.characters.spider.Spider' = motor.api.get_scene().get_object_by_name("player")
        if flower and flower.health <= 0:
            if self.death_animation_mode == False:
                self.death_animation_mode = True
                self.death_animation_timer.restart(DEATH_TIMER_DELAY)
            camera = motor.api.get_camera()
            camera.center_position(
                pg.math.lerp(camera.get_center_position().x, flower.get_center_position().x, LERP),
                pg.math.lerp(camera.get_center_position().y, flower.get_center_position().y, LERP)
            )
        elif player and player.health <= 0:
            if self.death_animation_mode == False:
                self.death_animation_mode = True
                self.death_animation_timer.restart(DEATH_TIMER_DELAY)
    
    def update_music_system(self):
        if self.playing_music_channel is None:
            chosen_music = motor.api.get_sound(random.choice(MUSIC_PATHS))
            self.playing_music_channel = chosen_music.play()
            match self.is_mute:
                case True:
                    self.playing_music_channel.set_volume(0)
                case False:
                    self.playing_music_channel.set_volume(MUSIC_VOLUME)
        
        if self.playing_music_channel is not None and self.playing_music_channel.get_busy() == False:
            self.playing_music_channel = None

        if motor.api.is_action_just_pressed("mute"):
            self.is_mute = not self.is_mute
            if self.playing_music_channel is not None:
                match self.is_mute:
                    case True:
                        self.playing_music_channel.set_volume(0)
                    case False:
                        self.playing_music_channel.set_volume(MUSIC_VOLUME)
    def start_raid(self):
        fly_factor = 0
        bee_factor = 0
        beetle_factor = 0
        
        #######
        if self.raid_level >= 1 and self.raid_level <= 3:
            fly_factor = 1
            bee_factor = 0
            beetle_factor = 0
        elif self.raid_level >= 4 and self.raid_level <= 6:
            fly_factor = 5
            bee_factor = 1
            beetle_factor = 0
        elif self.raid_level >= 7 and self.raid_level <= 9:
            fly_factor = 15
            bee_factor = 10
            beetle_factor = 1
        elif self.raid_level >= 10 and self.raid_level <= 12:
            fly_factor = 25
            bee_factor = 20
            beetle_factor = 5
        elif self.raid_level >= 13 and self.raid_level <= 15:
            fly_factor = 35
            bee_factor = 30
            beetle_factor = 30
        elif self.raid_level >= 16 and self.raid_level <= 18:
            fly_factor = 50
            bee_factor = 40
            beetle_factor = 40
        elif self.raid_level >= 19 and self.raid_level <= 30:
            fly_factor = 1
            bee_factor = 1
            beetle_factor = 1
        elif self.raid_level >= 31 and self.raid_level <= 40:
            fly_factor = 1
            bee_factor = 2
            beetle_factor = 1
        elif self.raid_level >= 41 and self.raid_level <= 50:
            fly_factor = 1
            bee_factor = 2
            beetle_factor = 2
        elif self.raid_level >= 51 and self.raid_level <= 70:
            fly_factor = 1
            bee_factor = 3
            beetle_factor = 2
        elif self.raid_level >= 71 and self.raid_level <= 100:
            fly_factor = 1
            bee_factor = 5
            beetle_factor = 5
        elif self.raid_level > 100:
            fly_factor = 1
            bee_factor = 1
            beetle_factor = 1
        #######
        self.raid_info = gen_raid_info(fly_factor, bee_factor, beetle_factor)
        self.spawn_enemy_delay = max( 0.5, 5 - self.raid_level * 0.5)
        self.enemy_counter = int(3 + self.raid_level * 1.5)
        self.spawn_enemy_timer.restart(1)
        self.is_raid_mode = True
    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        if self.paused:
            canvas.blit(self.pause_background, (0, 0))
            font = motor.api.get_font("assets/fonts/Symtext.ttf")
            font_render = font.render(
                "PAUSED, PRESS [ESC] TO CONTINUE",
                False,
                (255, 255, 255)
            )
            value_to_scale = 0.5
            font_render = pg.transform.scale(
                font_render,
                (int(font_render.get_width()*value_to_scale), int(font_render.get_height()*value_to_scale))
            )
            font_rect = font_render.get_rect()
            font_rect.x = (canvas.get_width()//2) - (font_render.get_width()//2)
            font_rect.y = (canvas.get_height()//2) - (font_render.get_height()//2)
            canvas.blit(font_render, font_rect)
        else:
            self.render_shadows(canvas, camera)
            self.render_objects(canvas, camera)
            self.render_gui(canvas, camera)

        
    def render_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
        self.render_flower_gui(canvas, camera)
        self.render_player_gui(canvas, camera)
        self.render_raid_gui(canvas, camera)
    
    def render_shadows(self, canvas: pg.Surface, camera: motor.camera.Camera):
        web_line_list = motor.api.get_scene().get_all_objects_by_tag("web-string")
        for web_line in web_line_list:
            first_web_node: 'game.misc.web_node.WebNode' = motor.api.get_scene().get_object_by_uid(web_line.first_web_node_uid)
            second_web_node: 'game.misc.web_node.WebNode' = motor.api.get_scene().get_object_by_uid(web_line.second_web_node_uid)
            if first_web_node and second_web_node:
                pg.draw.line(
                    canvas,
                    GREEN_SHADOW_COLOR,
                    camera.get_relative_position_by_vector2(first_web_node.get_center_position()+LINE_SHADOW_OFFSET),
                    camera.get_relative_position_by_vector2(second_web_node.get_center_position()+LINE_SHADOW_OFFSET),
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
                flower.position.y + 56,
                flower.size.x,
                flower.size.y/4
            )
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )

        tree_list = motor.api.get_scene().get_all_objects_by_name("tree")
        for tree in tree_list:
            AUX = 56
            shadow_rect = pg.Rect(
                tree.position.x+AUX,
                tree.position.y + 200,
                tree.size.x-AUX*2,
                tree.size.y/4
            )
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )

        shoot_list = motor.api.get_scene().get_all_objects_by_tag("shoot")
        for shoot in shoot_list:
            shadow_rect = pg.Rect(
                shoot.position.x,
                shoot.position.y + 40,
                shoot.size.x,
                shoot.size.y/4
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
    
        item_list = motor.api.get_scene().get_all_objects_by_tag("item")
        for item in item_list:
            shadow_rect = pg.Rect(
                item.position.x,
                item.position.y + 52,
                item.size.x,
                item.size.y/4
            )
            pg.draw.ellipse(
                canvas,
                GREEN_SHADOW_COLOR,
                camera.get_relative_rect_by_rect(shadow_rect)
            )
    def render_flower_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
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

    def render_player_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
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
            
            # draw the percent of the shoot timer
            radius = 16
            
            canvas_size = motor.api.get_motor().canvas_size.copy()
            max_time = player.shoot_delay
            time = player.shoot_timer.time
            percent = max(round(time / max_time, 2), 0)
            angle = int(360 - percent * 360)
            
            x = int(radius + 4)
            y = int(canvas_size.y - radius - 4)
            if percent > 0:
                pygame.gfxdraw.pie(
                    canvas,
                    x, y, 
                    16,
                    0, angle,
                    (255, 255, 255)
                )
            
            # draw the percent of the node placement lol
            node_placement_timer = player.web_node_spawn_timer.time
            percent = max(round(node_placement_timer / game.characters.spider.WEB_NODE_SPAWN_DELAY, 2), 0)
            angle = int(360 - percent * 360)
            x = int(radius*3 + 8)
            y = int(canvas_size.y - radius - 4)
            if percent > 0:
                pygame.gfxdraw.pie(
                    canvas,
                    x, y, 
                    16,
                    0, angle,
                    (255, 255, 255)
                )
            
            # draw the percent of the web string increment
            web_string_timer = player.increase_web_string_timer.time
            percent = max(round(web_string_timer / game.characters.spider.INCREASE_WEB_STRING_DELAY, 2), 0)
            angle = int(360 - percent * 360)
            x = int(radius*5 + 12)
            y = int(canvas_size.y - radius - 4)
            if percent > 0:
                pygame.gfxdraw.pie(
                    canvas,
                    x, y, 
                    16,
                    0, angle,
                    (255, 255, 255)
                )
            
            # draw the coin count
            font = motor.api.get_font("assets/fonts/Symtext.ttf")
            font_render = font.render(
                str(player.coins)+ " coins",
                False,
                (255, 255, 255)
            )
            value_to_scale = 0.5
            font_render = pg.transform.scale(
                font_render,
                (int(font_render.get_width()*value_to_scale), int(font_render.get_height()*value_to_scale))
            )
            font_rect = font_render.get_rect()
            font_rect.x = canvas_size.x - font_render.width - 4
            font_rect.y = 4
            canvas.blit(font_render, font_rect)

            item_list = motor.api.get_scene().get_all_objects_by_tag("item")
            for item in item_list:
                if player.is_colliding_with_rect(item.get_collision_rect()):
                    item.render_gui(canvas, camera)
                    break
    def render_raid_gui(self, canvas: pg.Surface, camera: motor.camera.Camera):
        font = motor.api.get_font("assets/fonts/Symtext.ttf")
        txt = ""
        if self.is_raid_mode == True:
            enemies_left = len(motor.api.get_scene().get_all_objects_by_tag("enemy")) + self.enemy_counter
            txt = "RAID " + str(self.raid_level) + " - " + str(enemies_left) + " ENEMIES LEFT"
        else:
            txt = "PRESS [ENTER] TO START RAID " + str(self.raid_level+1)
        font_render = font.render(
            txt,
            False,
            (255, 255, 255)
        )
        value_to_scale = 0.4
        font_render = pg.transform.scale(
            font_render,
            (int(font_render.get_width()*value_to_scale), int(font_render.get_height()*value_to_scale))
        )
        font_rect = font_render.get_rect()
        font_rect.x = canvas.get_width() - font_render.width - 4
        font_rect.y = canvas.get_height() - font_render.height - 4
        canvas.blit(font_render, font_rect)
def gen_raid_info(fly_factor: int, bee_factor: int, beetle_factor: int) -> np.ndarray:
    raid_info = np.concatenate((
        np.full(fly_factor, 0),
        np.full(bee_factor, 1),
        np.full(beetle_factor, 2)
    ))
    return raid_info

def get_random_enemy_spawn_id(info: np.ndarray) -> int:
    if len(info) == 0:
        return 1
    random_index = random.randint(0, len(info)-1)
    return info[random_index]

