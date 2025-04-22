import pygame as pg
import game.scenes
import game.scenes.game_scene
import game.scenes.menu_scene
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
        "assets/images/coin-sheet.png",
        "assets/images/decoration.png",
        "assets/images/more-shoots-card.png",
        "assets/images/shoot-time-card.png",
    )

    motor.api.load_sounds(
        "assets/sounds/shoot.wav",
        "assets/sounds/shoot-hit.wav",
        "assets/sounds/explosion.wav",
        "assets/sounds/hurt.wav",
        "assets/sounds/powerup.wav",
        "assets/sounds/coin.wav",
        "assets/sounds/laser.wav",
        "assets/sounds/camera.wav",
        "assets/sounds/high-explosion.wav",
        "assets/sounds/powerup-2.wav",
        "assets/sounds/powerup-3.wav",
        "assets/sounds/placement.wav",
        "assets/sounds/blip.wav",
        "assets/sounds/error.wav",
        "assets/sounds/step.wav",
        "assets/sounds/blow.wav",
        "assets/sounds/done.wav",
        "assets/sounds/crack.wav",

        "assets/musics/walking-around.wav",
        "assets/musics/foot-inside-the-water.wav",
    )

    motor.api.load_font(
        "assets/fonts/Symtext.ttf", 32,
    )

    motor.api.bind_key_to_action(pg.K_UP, "up")
    motor.api.bind_key_to_action(pg.K_DOWN, "down")
    motor.api.bind_key_to_action(pg.K_LEFT, "left")
    motor.api.bind_key_to_action(pg.K_RIGHT, "right")

    motor.api.bind_key_to_action(pg.K_w, "up")
    motor.api.bind_key_to_action(pg.K_s, "down")
    motor.api.bind_key_to_action(pg.K_a, "left")
    motor.api.bind_key_to_action(pg.K_d, "right")

    motor.api.bind_key_to_action(pg.K_z, "action-1")
    motor.api.bind_mouse_left_click_to_action("action-1")

    motor.api.bind_key_to_action(pg.K_x, "action-2")
    motor.api.bind_mouse_right_click_to_action("action-2")

    motor.api.bind_key_to_action(pg.K_c, "camera-mode")

    motor.api.bind_key_to_action(pg.K_ESCAPE, "pause")

    motor.api.bind_key_to_action(pg.K_RETURN, "raid")

    motor.api.bind_key_to_action(pg.K_m, "mute")

    first_scene = game.scenes.menu_scene.MenuScene()
    motor.api.set_scene(first_scene)

    motor.api.run()

if __name__ == "__main__":
    main()