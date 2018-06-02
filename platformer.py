#!/usr/bin/env python

""" TODO:
- continuous animations while key is pressed?
- fix kunai wobbling
- destructible objects
- fix double jump
- level bigger than screen & scrolling
"""

from __future__ import print_function, division
import sys, os
from collections import namedtuple
import pygame
from pygame import K_RIGHT, K_LEFT, K_DOWN, K_UP, K_SPACE, K_ESCAPE, K_F1, K_LCTRL, K_x, K_c, K_v
from sprites import Background, load_level
from ninja import Ninja

os.environ['SDL_VIDEO_WINDOW_POS'] = "366,0"
pygame.init()

logo = pygame.image.load('./gfx/logo.png')
pygame.display.set_icon(logo)

SIZE = WIDTH, HEIGHT = 1000, 740
BACKGROUND_COLOR = pygame.Color('black')
FPS = 60

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def main():
    bg = Background(SIZE)
    player = Ninja(position=(200, 100), screen=bg.rect)
    level, objects = load_level()
    fixed_sprites = pygame.sprite.Group(*level)
    fixed_sprites.add(*objects)
    moving_sprites = pygame.sprite.Group()
    blocks = [block.rect for block in level]

    debug = False
    running = True
    while running:

        dt = clock.tick(FPS) / 1000  # Amount of seconds between each loop.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_F1:
                    debug = not debug
                elif event.key == K_RIGHT:
                    player.move_right()
                elif event.key == K_LEFT:
                    player.move_left()
                elif event.key == K_UP:
                    player.move_up()
                elif event.key == K_DOWN:
                    player.move_down()
                elif event.key == K_SPACE:
                    player.jump()
                elif event.key == K_LCTRL:
                    player.attack()
                elif event.key == K_x:
                    player.die()
                elif event.key == K_c:
                    player.glide(blocks)
                elif event.key == K_v:
                    kunai = player.throw()
                    if kunai:
                        moving_sprites.add(kunai)
            elif event.type == pygame.KEYUP:
                if event.key in (K_RIGHT, K_LEFT, K_UP, K_DOWN):
                    player.stop()
                # elif event.key == K_DOWN or event.key == K_UP:
                #     player.velocity.y = 0

        player.fall(blocks)
        player.update(blocks)
        for s in moving_sprites:
            if s.update(blocks):
                moving_sprites.remove(s)

        # screen.fill(BACKGROUND_COLOR)
        screen.blit(bg.image, bg.rect)
        fixed_sprites.draw(screen)
        moving_sprites.draw(screen)
        player.draw(screen, debug)

        if debug:
            # show animation progression
            anim, idx = player.get_anim()
            x = y = 20
            scale_factor = -0.5
            for i, a in enumerate(anim):
                rect = a.get_rect()
                rect.inflate_ip(rect.w * scale_factor, rect.h * scale_factor)
                image = pygame.transform.scale(a, rect[-2:])
                rect.move_ip(x, y)
                x += rect.width
                screen.blit(image, rect)
                if i == idx:
                    pygame.draw.rect(screen, pygame.Color('red'), rect, 1)

            pygame.draw.rect(screen, pygame.Color('red'), player.rect, 1)
            for s in fixed_sprites.sprites() + moving_sprites.sprites():
                pygame.draw.rect(screen, pygame.Color('red'), s.rect, 1)

        pygame.display.update()


if __name__ == '__main__':
    main()
