#!/usr/bin/env python

""" TODO:
- continuous animations while key is pressed?
- fix ninja box displacement on animation change (attack, throw) -> restore to center? individual per animation type?
- fix double jump
- have objects fall
- walking interferes with animations
- level bigger than screen & scrolling
"""

from __future__ import print_function, division
import sys, os
from collections import namedtuple
import pygame as pg
from sprites import Background, load_level
from ninja import Ninja
from zombie import Zombie

os.environ['SDL_VIDEO_WINDOW_POS'] = "366,0"
pg.init()

logo = pg.image.load('./gfx/logo.png')
pg.display.set_icon(logo)

SIZE = WIDTH, HEIGHT = 1000, 740
BACKGROUND_COLOR = pg.Color('black')
RED = pg.Color('red')
FPS = 60

screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()


def main():
    bg = Background(SIZE)
    player = Ninja(position=(200, 100), screen=bg.rect)
    zombie = Zombie((100, 500), bg.rect, False)
    level, deco, objects = load_level()
    fixed_sprites = pg.sprite.Group(*level)
    fixed_sprites.add(*deco)
    fixed_sprites.add(*objects)
    destroyers = pg.sprite.Group()
    blocks = [block.rect for block in level]
    fading = pg.sprite.Group()

    debug = False
    running = True
    paused = False
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
                elif event.key == pg.K_RIGHT and not paused:
                    player.move_right()
                elif event.key == pg.K_LEFT and not paused:
                    player.move_left()
                elif event.key == pg.K_UP and not paused:
                    player.move_up()
                elif event.key == pg.K_DOWN and not paused:
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
                    zombie.die()
            elif event.type == pg.KEYUP and not paused:
                if event.key in (pg.K_RIGHT, pg.K_LEFT, pg.K_UP, pg.K_DOWN):
                    player.stop()
                # elif event.key == pg.K_DOWN or event.key == pg.K_UP:
                #     player.velocity.y = 0

        if not paused:
            player.fall(blocks)
            zombie.fall(blocks)
            player.update(blocks + [o.rect for o in objects])
            zombie.update(blocks + [o.rect for o in objects])
            for s in destroyers:
                if s.update(blocks):
                    destroyers.remove(s)
                idx = s.rect.collidelist(objects)
                if idx != -1:
                    destroyers.remove(s)
                    obj = objects[idx]
                    fading.add(obj)
                    objects.remove(obj)
                    fixed_sprites.remove(obj)
            death_box = player.get_attack_box()
            if death_box:
                idx = death_box.collidelist(objects)
                if idx != -1:
                    obj = objects[idx]
                    fading.add(obj)
                    objects.remove(obj)
                    fixed_sprites.remove(obj)

        for obj in fading:
            if obj.fade():
                fading.remove(obj)

        # screen.fill(BACKGROUND_COLOR)
        screen.blit(bg.image, bg.rect)
        fixed_sprites.draw(screen)
        destroyers.draw(screen)
        fading.draw(screen)
        player.draw(screen, debug)
        zombie.draw(screen, debug)

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

            pg.draw.rect(screen, RED, player.rect, 1)
            for s in fixed_sprites.sprites() + destroyers.sprites():
                pg.draw.rect(screen, RED, s.rect, 1)

            if player.current_animation == 'Attack':
                r = player.rect.h // 2
                top = player.rect.top
                x = player.rect.right if player.facing_right else player.rect.left
                y = top + r
                pg.draw.circle(screen, RED, (x, y), r, 1)
                death_box = player.get_attack_box()
                if death_box:
                    pg.draw.rect(screen, RED, death_box, 1)

        pg.display.update()


if __name__ == '__main__':
    main()
