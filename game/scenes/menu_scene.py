import motor
import motor.api
import motor.camera
import motor.scene
import pygame as pg
import game.scenes.game_scene

MUSIC_VOLUME = 0.3

class MenuScene(motor.scene.Scene):
    def __init__(self):
        super().__init__(
            name="menu-scene"
        )
        self.menu_music_channel: pg.Channel = None
    
    def init(self):
        music = motor.api.get_sound("assets/musics/foot-inside-the-water.wav")
        if music:
            self.menu_music_channel = music.play(-1)
            self.menu_music_channel.set_volume(MUSIC_VOLUME)
    def render(self, canvas: pg.Surface, camera: motor.camera.Camera):
        LINE_OFFSET = 8
        points = [
            pg.Vector2(LINE_OFFSET, LINE_OFFSET),
            pg.Vector2(canvas.get_width() - LINE_OFFSET, LINE_OFFSET),
            pg.Vector2(canvas.get_width() - LINE_OFFSET, canvas.get_height() - LINE_OFFSET),
            pg.Vector2(LINE_OFFSET, canvas.get_height() - LINE_OFFSET),
            pg.Vector2(LINE_OFFSET, LINE_OFFSET)
        ]
        
        pg.draw.lines(
            canvas, 
            (255, 255, 255), 
            False, 
            points, 
            2
        )
        
        font = motor.api.get_font("assets/fonts/Symtext.ttf")
        font_render = pg.font.Font.render(
            font, 
            "ARACHNOFORGE", 
            True, 
            (255, 255, 255)
        )

        scale = 1.5
        font_render = pg.transform.scale(
            font_render, 
            (int(font_render.get_width() * scale), int(font_render.get_height() * scale))
        )
        canvas.blit(
            font_render, 
            (canvas.get_width() // 2 - font_render.get_width() // 2, 50)
        )

        font_render = pg.font.Font.render(
            font, 
            "Press [ENTER] to start", 
            True, 
            (255, 255, 255)
        )
        scale = 0.5
        font_render = pg.transform.scale(
            font_render, 
            (int(font_render.get_width() * scale), int(font_render.get_height() * scale))
        )
        canvas.blit(
            font_render, 
            (canvas.get_width() // 2 - font_render.get_width() // 2, canvas.get_height() // 2)
        )

        font_render = pg.font.Font.render(
            font, 
            "ALL MADE BY JoeCavZero", 
            True, 
            (255, 255, 255)
        )
        scale = 0.5
        font_render = pg.transform.scale(
            font_render, 
            (int(font_render.get_width() * scale), int(font_render.get_height() * scale))
        )
        canvas.blit(
            font_render, 
            (canvas.get_width() // 2 - font_render.get_width() // 2, canvas.get_height() - font_render.get_height() // 2 - 30)
        )
        

    def update(self, delta_time):
        if motor.api.is_action_just_pressed("raid"):
            self.menu_music_channel.stop()
            game_scene = game.scenes.game_scene.GameScene()
            motor.api.set_scene(game_scene)