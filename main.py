import pygame as pg
import game.scenes
import game.scenes.game_scene
import motor.api
import game

def main():
    motor.api.init_motor(480, 280, pixel_scale=1)

    motor.api.load_textures(
        "assets/images/grass-tileset.png",
        "assets/images/particle.png",
        "assets/images/web-node.png",
        "assets/images/spider.png",
        "assets/images/fly-sheet.png",
        "assets/images/flower.png",
        "assets/images/flower-bar.png",
        "assets/images/spider-bar.png",
        "assets/images/bee-sheet.png",
        "assets/images/bee-shoot.png",
        "assets/images/tree.png",
        "assets/images/beetle-sheet.png",
        "assets/images/spider-shoot.png",
        "assets/images/coin-sheet.png"
    )

    motor.api.load_sounds(
        "assets/sounds/shoot.wav",
        "assets/sounds/shoot-hit.wav",
        "assets/sounds/explosion.wav",
        "assets/sounds/hurt.wav",
        "assets/sounds/powerup.wav",
        "assets/sounds/coin.wav",
    )

    motor.api.bind_key_to_action(pg.K_UP, "up")
    motor.api.bind_key_to_action(pg.K_DOWN, "down")
    motor.api.bind_key_to_action(pg.K_LEFT, "left")
    motor.api.bind_key_to_action(pg.K_RIGHT, "right")

    motor.api.bind_key_to_action(pg.K_w, "up")
    motor.api.bind_key_to_action(pg.K_s, "down")
    motor.api.bind_key_to_action(pg.K_a, "left")
    motor.api.bind_key_to_action(pg.K_d, "right")

    motor.api.bind_key_to_action(pg.K_SPACE, "action-1")
    motor.api.bind_mouse_left_click_to_action("action-1")

    motor.api.bind_key_to_action(pg.K_x, "action-2")
    motor.api.bind_mouse_right_click_to_action("action-2")

    motor.api.bind_key_to_action(pg.K_c, "camera-mode")

    motor.api.bind_key_to_action(pg.K_ESCAPE, "pause")

    test_scene = game.scenes.game_scene.GameScene("test-scene")
    motor.api.set_scene(test_scene)

    motor.api.run()

if __name__ == "__main__":
    main()