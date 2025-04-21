import motor.camera
from motor.motor import MotorEngine
import motor as motor

import numpy as np
import pandas as pd
import pygame as pg

import motor.scene

motor_engine: MotorEngine = None

def init_motor(canvas_width: int, canvas_height: int, pixel_scale: int = 2):
    global motor_engine
    if motor_engine is not None:
        raise RuntimeError("Motor is already initialized.")
    motor_engine = MotorEngine(canvas_width, canvas_height, pixel_scale)

def run():
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("Motor is not initialized.")
    motor_engine.run()

def set_scene(scene: motor.scene.Scene):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("Motor is not initialized.")
    motor_engine.set_scene(scene)

def get_camera() -> 'motor.camera.Camera':
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("Motor is not initialized.")
    return motor_engine.scene.camera

def is_action_pressed(action: str) -> bool:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.is_action_pressed(action)

def is_action_just_pressed(action: str) -> bool:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.is_action_just_pressed(action)

def bind_key_to_action( key: int, action: str ):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.bind_key_to_action(key, action)

def bind_mouse_wheel_up_to_action(action: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.bind_mouse_wheel_up_to_action(action)

def bind_mouse_wheel_down_to_action(action: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.bind_mouse_wheel_down_to_action(action)

def bind_mouse_left_click_to_action(action: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.bind_mouse_left_click_to_action(action)
def bind_mouse_right_click_to_action(action: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.bind_mouse_right_click_to_action(action)
def read_level_data(path: str) -> np.typing.NDArray[np.uint32]:
    df = pd.read_csv(path, sep=",", header=None)
    df.fillna(0, inplace=True)
    return df.to_numpy().astype(np.uint32)

def get_motor() -> MotorEngine:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine

def get_scene() -> motor.scene.Scene:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.scene

def load_texture(path: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.texture_manager.load_texture(path)

def load_textures(*paths: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    for p in paths:
        motor_engine.texture_manager.load_texture(p)

def get_texture(path: str) -> pg.Surface:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.texture_manager.get_texture(path)

def get_mouse_screen_position() -> pg.Vector2:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.get_mouse_screen_position()

def get_mouse_world_position() -> pg.Vector2:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.get_mouse_world_position()

def load_sound(path: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    motor_engine.sound_manager.load_sound(path)

def load_sounds(*paths: str):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    for p in paths:
        motor_engine.sound_manager.load_sound(p)

def get_sound(path: str) -> pg.mixer.Sound | None:
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.sound_manager.get_sound(path)

def play_sound(path: str, volume: float = 1.0):
    global motor_engine
    if motor_engine is None:
        raise RuntimeError("motor is not initialized.")
    return motor_engine.sound_manager.play_sound(path, volume)