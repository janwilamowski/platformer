#!/usr/bin/env python

import sys
from collections import namedtuple
import pygame
from pygame import K_RIGHT, K_LEFT, K_DOWN, K_UP, K_SPACE, K_ESCAPE, K_F1, K_LCTRL
from sprites import Background, load_level
from ninja import Ninja


pygame.init()

SIZE = WIDTH, HEIGHT = 1000, 740
BACKGROUND_COLOR = pygame.Color('black')
FPS = 60

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def main():
    bg = Background(SIZE)
    player = Ninja(position=(100, 100), screen=bg.rect)
    moving_sprites = pygame.sprite.Group(player)
    level = load_level()
    fixed_sprites = pygame.sprite.Group(*level)
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
            elif event.type == pygame.KEYUP:
                if event.key in (K_RIGHT, K_LEFT, K_UP, K_DOWN):
                    player.stop()
                # elif event.key == K_DOWN or event.key == K_UP:
                #     player.velocity.y = 0

        player.fall(blocks)

        moving_sprites.update(dt)  # Calls the 'update' method on all sprites in the list

        # screen.fill(BACKGROUND_COLOR)
        screen.blit(bg.image, bg.rect)
        fixed_sprites.draw(screen)
        moving_sprites.draw(screen)

        if debug:
            for s in moving_sprites:
                pygame.draw.rect(screen, pygame.Color('red'), s.rect, 1)
            for s in fixed_sprites:
                pygame.draw.rect(screen, pygame.Color('red'), s.rect, 1)

        pygame.display.update()


if __name__ == '__main__':
    main()
