import pygame as pg
import sys
import motor.managers
import motor.managers.font_manager
import motor.managers.texture_manager
import motor.managers.sound_manager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import motor.scene

TARGET_FPS = 60

class MotorEngine:
    def __init__(self, canvas_width: int, canvas_height: int, pixel_scale: int = 2):
        self.canvas_size: pg.Vector2 = pg.Vector2(canvas_width, canvas_height)
        self.window_title: str = ""

        self.window: pg.Surface = None
        self.pixel_scale: int = pixel_scale
        self.canvas: pg.Surface = None
        self.canvas_scale: float = 1.0
        self.clock: pg.time.Clock = None
        self.delta_time: float = 0.0

        self.running: bool = False

        self.scene: motor.scene.Scene = None

        self.texture_manager: motor.managers.texture_manager.TextureManager = None
        self.sound_manager: motor.managers.sound_manager.SoundManager = None
        self.font_manager: motor.managers.font_manager.FontManager = None

        self.input_bindings: dict[int, str] = {}
        self.special_input_bindings: dict[str, str] = {}
        self.actions: dict[str, bool] = {}
        self.just_pressed_input: dict[str, tuple[bool, bool]] = {}

        self._init_core()
    
    def run(self):
        self.running = True

        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.delta_time: float = self.clock.tick(TARGET_FPS)/1000
        
        self._close()
    
    def _init_core(self):
        pg.init()
        pg.display.init()
        self.window = pg.display.set_mode(self.canvas_size, pg.RESIZABLE)
        pg.display.set_caption(self.window_title)
        self.canvas = pg.Surface(self.canvas_size)
        self.clock = pg.time.Clock()
        self.texture_manager = motor.managers.texture_manager.TextureManager()
        self.sound_manager = motor.managers.sound_manager.SoundManager()
        self.font_manager = motor.managers.font_manager.FontManager()
    def _handle_events(self):

        for action in self.actions:
            self.actions[action] = False

        mouse_scroll_y = 0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.MOUSEWHEEL:
                mouse_scroll_y = event.y

        for sib in self.special_input_bindings:
            action: str = self.special_input_bindings[sib]
            match sib:
                case "mouse-wheel-up":
                    self.actions[action] = mouse_scroll_y > 0
                case "mouse-wheel-down":
                    self.actions[action] = mouse_scroll_y < 0
                case "mouse-left-click":
                    self.actions[action] = pg.mouse.get_pressed()[0]
                case "mouse-right-click":
                    self.actions[action] = pg.mouse.get_pressed()[2]
        keys = pg.key.get_pressed()
        for ib in self.input_bindings:
            action = self.input_bindings[ib]
            is_pressed = keys[ib]
            if action not in self.actions:
                self.actions[action] = False
            self.actions[action] = is_pressed or self.actions[action]
        
        
        for action in self.actions:
            if self.actions[action] == True:
                if self.just_pressed_input.get(action) is None or self.just_pressed_input[action][1] == False:
                    self.just_pressed_input[action] = (True, True)  # Just pressed and debounce active
                else:
                    self.just_pressed_input[action] = (False, True)  # Held down, debounce active
            else:
                self.just_pressed_input[action] = (False, False)  # Not pressed, debounce reset

        
                
    
    def _update(self):
        self.scene.update(self.delta_time)

    def _render(self):
        self.window.fill( (0,0,0) )
        self.canvas.fill( (0,100,81) )

        self.scene.render(self.canvas, self.scene.camera)
        self._render_canvas()

        pg.display.flip()
        
    def _render_canvas(self):
        scale_x = self.window.get_width() / self.canvas_size.x
        scale_y = self.window.get_height() / self.canvas_size.y
        
        if scale_x > scale_y:
            self.canvas_scale = scale_y
        else:
            self.canvas_scale = scale_x

        new_canvas = pg.transform.scale(
                self.canvas , 
                (
                    int(self.canvas_size.x * self.canvas_scale) , 
                    int(self.canvas_size.y * self.canvas_scale)
                ) 
            )
        dif_x = self.window.get_width() - new_canvas.get_width()
        dif_y = self.window.get_height() - new_canvas.get_height()

        self.window.blit(
            new_canvas,
            (
                dif_x//2,
                dif_y//2
            )
        )

    def set_scene(self, scene: 'motor.scene.Scene'):
        if self.scene is not None:
            self.scene.close()
        self.scene = scene
        self.scene.init()

    def bind_key_to_action(self, key: int, input: str):
        self.input_bindings[key] = input

    def is_action_pressed(self, input: str) -> bool:
        if self.actions.get(input) is not None:
            return self.actions[input]
        return False
    def is_action_just_pressed(self, input: str) -> bool:
        aux = self.just_pressed_input.get(input)
        if aux is not None:
            return aux[0]
        return False
           
    def bind_mouse_wheel_up_to_action(self, input: str):
        self.special_input_bindings["mouse-wheel-up"] = input
    
    def bind_mouse_wheel_down_to_action(self, input: str):
        self.special_input_bindings["mouse-wheel-down"] = input
    def bind_mouse_left_click_to_action(self, input: str):
        self.special_input_bindings["mouse-left-click"] = input
    def bind_mouse_right_click_to_action(self, input: str):
        self.special_input_bindings["mouse-right-click"] = input
    def get_mouse_screen_position(self) -> pg.Vector2:
        mouse_position = pg.Vector2(pg.mouse.get_pos())
        window_size = pg.Vector2(self.window.get_size())
        
        diff_x = window_size.x - (self.canvas_size.x * self.canvas_scale)
        diff_y = window_size.y - (self.canvas_size.y * self.canvas_scale)
        
        return pg.Vector2(
            (mouse_position.x - diff_x // 2) / self.canvas_scale,
            (mouse_position.y - diff_y // 2) / self.canvas_scale
        )
    def get_mouse_world_position(self) -> pg.Vector2:
        camera = self.scene.camera
        mouse_pos = self.get_mouse_screen_position()
        return pg.Vector2(
            (mouse_pos.x / camera.zoom/ self.pixel_scale) + camera.position.x,
            (mouse_pos.y / camera.zoom/ self.pixel_scale) + camera.position.y
        )

    def load_font(self, path: str, size: int):
        self.font_manager.load_font(path, size)
    def get_font(self, path: str) -> pg.font.Font:
        return self.font_manager.get_font(path)

    def _close(self):
        pg.quit()
        sys.exit(0)
