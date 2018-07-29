#!/usr/bin/env python

""" TODO:
- kunai only works on initial screen & not in close range?
- female zombie rect is too large
- damage shouldn't be bound to animations
- sneak attack
- zombie states: idle, following, attacking, dead
- continuous animations while key is pressed?
- fix ninja box displacement on animation change (attack, throw) -> restore to center? individual per animation type?
- have objects fall
- walking interferes with animations
- left edge is constrained but right edge isn't
- game over when player falls to bottomless pit
- scrolling displaces player
"""

from __future__ import print_function, division
import sys, os
import pygame as pg
from collections import defaultdict
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


class Game(object):

    def __init__(self):
        self.screen = pg.display.set_mode(SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.paused = False
        self.debug = False
        self.shift = False
        self.follow = False
        self.minimap = False
        self.FPS = 60
        self.bg = Background(SIZE)
        self.camera = Camera(w=WIDTH, h=HEIGHT)
        self.blocks = []
        self.fading = []
        self.fading_zombies = []
        self.screenshot_counter = 0
        self.destroyers = pg.sprite.Group()
        self.player = Ninja(position=(200, 100), screen=self.bg.rect)
        zombie1 = Zombie((100, 500), self.bg.rect, False)
        zombie2 = Zombie((700, 50), self.bg.rect, True)
        self.zombies = pg.sprite.Group(zombie1, zombie2)

        self.reset()

        self.run()


    def reset(self):
        for char in self.zombies.sprites() + [self.player]:
            char.reset()
            # TODO: readd zombies
        level, deco, self.objects, level_rect, cam_origin = load_level()
        self.fixed_sprites = level + deco + self.objects
        del self.blocks[:]
        self.blocks.extend( [block.rect for block in level] )
        if cam_origin:
            self.camera.reset()
            self.camera.move(*cam_origin)
            self.camera.pos.bottom = min(self.camera.pos.bottom, level_rect.bottom)
        else:
            self.camera.pos.center = level_rect.center
            self.camera.pos.bottom = level_rect.bottom
        self.level_rect = level_rect


    def toggle_debug(self):
        self.debug = not self.debug


    def toggle_paused(self):
        if self.minimap: return

        self.paused = not self.paused


    def toggle_follow(self):
        self.follow = not self.follow


    def toggle_slomo(self):
        # slow motion
        self.FPS = 30 if self.FPS == 60 else 60


    def toggle_minimap(self):
        self.minimap = not self.minimap
        self.paused = self.minimap


    def ranged_attack(self):
        if self.paused: return

        kunai = self.player.throw()
        if kunai:
            self.destroyers.add(kunai)


    def right(self):
        if self.shift:
            self.camera.move(100, 0)
        elif not self.paused:
            self.player.move_right()


    def left(self):
        if self.shift:
            self.camera.move(-100, 0)
        elif not self.paused:
            self.player.move_left()


    def up(self):
        if self.shift:
            self.camera.move(0, -100)
        elif not self.paused:
            self.player.move_up()


    def down(self):
        if self.shift:
            self.camera.move(0, 100)
        elif not self.paused:
            self.player.move_down()


    def screenshot(self):
        filename = "screenshot{c}.jpg".format(c=self.screenshot_counter)
        self.screenshot_counter += 1
        pg.image.save(self.screen, filename)


    def draw(self):
        if self.follow:
            cam = self.camera.pos
            cam.center = self.player.rect.center
            cam.bottom = min(cam.bottom, self.level_rect.bottom)
        # scrolling background
        self.screen.fill(BACKGROUND_COLOR)
        bg_rect = self.camera.apply(self.bg)
        bg_rect.x %= WIDTH
        bg_rect.y = max(bg_rect.y, HEIGHT - bg_rect.h)
        bg_rect.y = min(bg_rect.y, 0)
        self.screen.blit(self.bg.image, bg_rect)
        self.screen.blit(self.bg.image, bg_rect.move(bg_rect.width, 0))
        self.screen.blit(self.bg.image, bg_rect.move(-bg_rect.width, 0))

        # draw sprites
        for sprite in self.fixed_sprites + self.fading:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.destroyers:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.player.draw(self.screen, self.camera, self.debug)
        for zombie in self.zombies.sprites() + self.fading_zombies:
            zombie.draw(self.screen, self.camera, self.debug)

        if self.minimap:
            mm = pg.Rect(100, 60, WIDTH-200, HEIGHT-120)
            map_cam = Camera(*mm)
            map_cam.move(-220, -200) # TODO: dynamic offset & scale factor to fit whole level
            pg.draw.rect(self.screen, pg.Color('gray'), mm, 0)
            for sprite in self.fixed_sprites:
                self.screen.blit(sprite.map_image, map_cam.apply_rect(sprite.map_rect))
            # draw current screen
            cur_screen = self.camera.pos.copy()
            cur_screen.w *= 0.5
            cur_screen.h *= 0.5
            cur_screen.x *= 0.5
            cur_screen.y *= 0.5
            pg.draw.rect(self.screen, pg.Color('red'), map_cam.apply_rect(cur_screen), 1)


    def run(self):
        while self.running:

            dt = self.clock.tick(self.FPS) / 1000  # Amount of seconds between each loop.

            def nop():
                return lambda: None

            def stop():
                if self.paused: return
                self.player.stop()

            keydown_handlers = defaultdict(nop, {
                pg.K_ESCAPE: sys.exit,
                pg.K_F1: self.toggle_debug,
                pg.K_F2: self.toggle_slomo,
                pg.K_F3: self.toggle_follow,
                pg.K_F12: self.screenshot,
                pg.K_RIGHT: self.right,
                pg.K_LEFT: self.left,
                pg.K_UP: self.up,
                pg.K_DOWN: self.down,
                pg.K_SPACE: lambda: None if self.paused else self.player.jump(),
                pg.K_LCTRL: lambda: None if self.paused else self.player.attack(),
                pg.K_x: lambda: None if self.paused else self.player.die(),
                pg.K_c: lambda: None if self.paused else self.player.glide(),
                pg.K_v: self.ranged_attack,
                pg.K_r: self.reset,
                pg.K_p: self.toggle_paused,
                pg.K_m: self.toggle_minimap,
                pg.K_b: lambda: [zombie.die() for zombie in self.zombies],
                pg.K_a: lambda: [zombie.attack() for zombie in self.zombies],
            })
            keyup_handlers = defaultdict(nop, {
                pg.K_RIGHT: stop,
                pg.K_LEFT: stop,
                pg.K_UP: stop,
                pg.K_DOWN: stop,
                # pg.K_DOWN or pg.K_UP: self.player.velocity.y = 0
            })
            for event in pg.event.get():
                mods = pg.key.get_mods()
                self.shift = mods & pg.KMOD_SHIFT
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    keydown_handlers[event.key]()
                elif event.type == pg.KEYUP:
                    keyup_handlers[event.key]()

            if not self.paused:
                # update character geometry
                self.player.fall()
                for zombie in self.zombies:
                    zombie.fall()
                self.player.update(self.blocks + [o.rect for o in self.objects + self.zombies.sprites()], self.camera)
                for zombie in self.zombies:
                    zombie.update(self.blocks + [o.rect for o in self.objects + [self.player]])
                for zombie in self.fading_zombies:
                    zombie.update([])

                # ranged attacks
                for destr in self.destroyers:
                    if destr.update(self.blocks, self.camera):
                        self.destroyers.remove(destr)
                    idx = destr.rect.collidelist(self.objects)
                    if idx != -1:
                        self.destroyers.remove(destr)
                        obj = self.objects[idx]
                        self.fading.append(obj)
                        self.objects.remove(obj)
                        self.fixed_sprites.remove(obj)
                    for zombie in self.zombies:
                        if destr.rect.colliderect(zombie.rect):
                            if zombie.suffer(50):
                                self.zombies.remove(zombie)
                                self.fading_zombies.append(zombie)
                            self.destroyers.remove(destr)

                # melee attack
                death_box = self.player.get_attack_box()
                if death_box:
                    idx = death_box.collidelist(self.objects)
                    if idx != -1:
                        obj = self.objects[idx]
                        self.fading.append(obj)
                        self.objects.remove(obj)
                        self.fixed_sprites.remove(obj)
                    idx = death_box.collidelist([z.rect for z in self.zombies])
                    for zombie in self.zombies:
                        if death_box.colliderect(zombie.rect):
                            if zombie.suffer(2):
                                self.fading_zombies.append(zombie)
                                self.zombies.remove(zombie)

            # fade-outs
            self.fading = [obj for obj in self.fading if not obj.fade()]
            self.fading_zombies = [z for z in self.fading_zombies if not z.fade()]

            self.draw()

            if self.debug:
                # show animation progression
                anim, idx = self.player.get_anim()
                x = y = 20
                scale_factor = -0.5
                for i, a in enumerate(anim):
                    rect = a.get_rect()
                    rect.inflate_ip(rect.w * scale_factor, rect.h * scale_factor)
                    image = pg.transform.scale(a, rect[-2:])
                    rect.move_ip(x, y)
                    x += rect.width
                    self.screen.blit(image, rect)
                    if i == idx + 1:
                        pg.draw.rect(self.screen, RED, rect, 1)

                pg.draw.rect(self.screen, RED, self.camera.apply(self.player), 1)
                for sprite in self.fixed_sprites + self.destroyers.sprites():
                    pg.draw.rect(self.screen, RED, self.camera.apply(sprite), 1)

                if self.player.current_animation == 'Attack':
                    r = self.player.rect.h // 2
                    top = self.player.rect.top
                    x = self.player.rect.right if self.player.facing_right else self.player.rect.left
                    y = top + r
                    pg.draw.circle(self.screen, RED, self.camera.apply_coords( (x, y) ), r, 1)
                    death_box = self.player.get_attack_box()
                    if death_box:
                        pg.draw.rect(self.screen, RED, self.camera.apply_rect(death_box), 1)

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
