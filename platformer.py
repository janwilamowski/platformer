#!/usr/bin/env python

""" TODO:
- female zombie rect is too large
- damage shouldn't be bound to animations
- sneak attack
- zombie states: idle, following, attacking, dead
- continuous animations while key is pressed?
- fix ninja box displacement on animation change (attack, throw) -> restore to center? individual per animation type?
- have objects fall
- walking interferes with animations
- level bigger than screen & initial camera offset
- minimap
- scrolling displaces player -> autoscroll when player moves
"""

from __future__ import print_function, division
import sys, os
from collections import namedtuple
import pygame as pg
from level import load_level, Background
from ninja import Ninja
from zombie import Zombie
from camera import Camera

os.environ['SDL_VIDEO_WINDOW_POS'] = "366,0"
pg.init()

logo = pg.image.load('./gfx/logo.png')
pg.display.set_icon(logo)

SIZE = WIDTH, HEIGHT = 1000, 704
BACKGROUND_COLOR = pg.Color('black')
RED = pg.Color('red')

screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()


def main():
    FPS = 60
    bg = Background(SIZE)
    player = Ninja(position=(200, 100), screen=bg.rect)
    zombie1 = Zombie((100, 500), bg.rect, False)
    zombie2 = Zombie((600, 500), bg.rect, True)
    zombies = pg.sprite.Group(zombie1, zombie2)
    level, deco, objects = load_level()
    fixed_sprites = level + deco + objects
    destroyers = pg.sprite.Group()
    blocks = [block.rect for block in level]
    fading = []
    fading_zombies = []
    screenshot_counter = 0
    camera = Camera()

    debug = False
    running = True
    paused = False
    shift = False

    while running:

        dt = clock.tick(FPS) / 1000  # Amount of seconds between each loop.

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
                elif event.key == pg.K_F1:
                    debug = not debug
                elif event.key == pg.K_F2:
                    # slow motion
                    FPS = 30 if FPS == 60 else 60
                elif event.key == pg.K_F12:
                    filename = "screenshot{c}.jpg".format(c=screenshot_counter)
                    screenshot_counter += 1
                    pg.image.save(screen, filename)
                elif event.key in (pg.K_LSHIFT, pg.K_RSHIFT):
                    shift = True
                elif event.key == pg.K_RIGHT:
                    if shift:
                        camera.move(-100, 0)
                    elif not paused:
                        player.move_right()
                elif event.key == pg.K_LEFT and not paused:
                    if shift:
                        camera.move(100, 0)
                    elif not paused:
                        player.move_left()
                elif event.key == pg.K_UP and not paused:
                    if shift:
                        camera.move(0, 100)
                    elif not paused:
                        player.move_up()
                elif event.key == pg.K_DOWN and not paused:
                    if shift:
                        camera.move(0, -100)
                    elif not paused:
                        player.move_down()
                elif event.key == pg.K_SPACE and not paused:
                    player.jump()
                elif event.key == pg.K_LCTRL and not paused:
                    player.attack()
                elif event.key == pg.K_x and not paused:
                    player.die()
                elif event.key == pg.K_c and not paused:
                    player.glide(blocks)
                elif event.key == pg.K_v and not paused:
                    kunai = player.throw()
                    if kunai:
                        destroyers.add(kunai)
                elif event.key == pg.K_p:
                    paused = not paused
                elif event.key == pg.K_b:
                    zombie1.die()
                elif event.key == pg.K_a:
                    zombie1.attack()
                elif event.key == pg.K_s:
                    # stealth mode
                    player.toggle_hide()
                elif event.key == pg.K_r:
                    # reset
                    for char in zombies.sprites() + [player]:
                        char.state = 'Idle'
                        char.frozen = char.hidden = False
                    player.rect.x, player.rect.y = (200, 100)
                    zombie1 = Zombie((100, 500), bg.rect, False)
                    zombie2 = Zombie((600, 500), bg.rect, True)
                    zombies = pg.sprite.Group(zombie1, zombie2)
                    level, deco, objects = load_level()
                    fixed_sprites = level + deco + objects
                    camera.reset()
            elif event.type == pg.KEYUP:
                if event.key in (pg.K_LSHIFT, pg.K_RSHIFT):
                    shift = False
                elif event.key in (pg.K_RIGHT, pg.K_LEFT, pg.K_UP, pg.K_DOWN) and not paused:
                    player.stop()
                # elif event.key == pg.K_DOWN or event.key == pg.K_UP:
                #     player.velocity.y = 0

        if not paused:
            # update character geometry
            player.fall(blocks)
            for zombie in zombies:
                zombie.fall(blocks)
            player.update(blocks + [o.rect for o in objects + zombies.sprites()], camera)
            for zombie in zombies:
                zombie.update(blocks + [o.rect for o in objects + [player]])
            for zombie in fading_zombies:
                zombie.update([])

            # ranged attacks
            for s in destroyers:
                if s.update(blocks, camera):
                    destroyers.remove(s)
                idx = s.rect.collidelist(objects)
                if idx != -1:
                    destroyers.remove(s)
                    obj = objects[idx]
                    fading.append(obj)
                    objects.remove(obj)
                    fixed_sprites.remove(obj)
                for zombie in zombies:
                    if s.rect.colliderect(zombie.rect):
                        if zombie.suffer(50):
                            zombies.remove(zombie)
                            fading_zombies.append(zombie)
                        destroyers.remove(s)

            # melee attack
            death_box = player.get_attack_box()
            if death_box:
                idx = death_box.collidelist(objects)
                if idx != -1:
                    obj = objects[idx]
                    fading.append(obj)
                    objects.remove(obj)
                    fixed_sprites.remove(obj)
                idx = death_box.collidelist([z.rect for z in zombies])
                for zombie in zombies:
                    if death_box.colliderect(zombie.rect):
                        if zombie.suffer(2):
                            fading_zombies.append(zombie)
                            zombies.remove(zombie)

        # fade-outs
        fading = [obj for obj in fading if not obj.fade()]
        fading_zombies = [z for z in fading_zombies if not z.fade()]

        screen.fill(BACKGROUND_COLOR)
        bg_rect = camera.apply(bg)
        bg_rect.x %= WIDTH
        bg_rect.y = max(bg_rect.y, HEIGHT - bg_rect.h)
        bg_rect.y = min(bg_rect.y, 0)
        screen.blit(bg.image, bg_rect)
        screen.blit(bg.image, bg_rect.move(bg_rect.width, 0))
        screen.blit(bg.image, bg_rect.move(-bg_rect.width, 0))

        for sprite in fixed_sprites + fading:
            screen.blit(sprite.image, camera.apply(sprite))
        for sprite in destroyers:
            screen.blit(sprite.image, camera.apply(sprite))
        player.draw(screen, camera, debug)
        for zombie in zombies.sprites() + fading_zombies:
            zombie.draw(screen, camera, debug)

        if debug:
            # show animation progression
            anim, idx = player.get_anim()
            x = y = 20
            scale_factor = -0.5
            for i, a in enumerate(anim):
                rect = a.get_rect()
                rect.inflate_ip(rect.w * scale_factor, rect.h * scale_factor)
                image = pg.transform.scale(a, rect[-2:])
                rect.move_ip(x, y)
                x += rect.width
                screen.blit(image, rect)
                if i == idx + 1:
                    pg.draw.rect(screen, RED, rect, 1)

            pg.draw.rect(screen, RED, camera.apply(player), 1)
            for sprite in fixed_sprites + destroyers.sprites():
                pg.draw.rect(screen, RED, camera.apply(sprite), 1)

            if player.current_animation == 'Attack':
                r = player.rect.h // 2
                top = player.rect.top
                x = player.rect.right if player.facing_right else player.rect.left
                y = top + r
                pg.draw.circle(screen, RED, camera.apply_coords( (x, y) ), r, 1)
                death_box = player.get_attack_box()
                if death_box:
                    pg.draw.rect(screen, RED, camera.apply_rect(death_box), 1)

        pg.display.update()


if __name__ == '__main__':
    main()
