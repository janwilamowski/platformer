import pygame

# one level block is 64x64px, platforms are 64x46
# we use half steps in the level set up to fill the gaps

LEVEL = """





                    D E E E F





     D E E E E E F
           4

           4
                        0 2             0 2
           4
                        3 5             3 5
           4
0 1 1 1 6 7 9 A 1 1 1 6 7 9 A 1 1 1 1 6 7 9 A 2
"""

class Background(pygame.sprite.Sprite):
    def __init__(self, screen_size):
        super( Background, self).__init__()
        self.image = pygame.image.load('./gfx/bg.png').convert()
        self.rect = self.image.get_rect()
        self.rect.top = screen_size[1] - self.rect.h


def hex2dec(hex_str):
    return int(hex_str, 16)


def load_level():
    images = []
    for y, line in enumerate(LEVEL.splitlines()):
        for x, block in enumerate(line):
            if not block.strip(): continue
            img = LevelBlock(hex2dec(block), (x*32, y*32))
            images.append(img)
    level_size = (x+2)*32, (y+2)*32

    deco = []
    objects = []
    # ground level
    deco.append( Decoration('stone', (120, 568)))
    deco.append( Decoration('cactus1', (600, 530)))

    # first floor
    objects.append( Crate( (450, 334) ) )
    objects.append( Crate( (500, 334) ) )
    objects.append( Crate( (475, 284) ) )

    # second floor
    deco.append( Decoration('skeleton', (700, 144)))

    return images, deco, objects, pygame.Rect((0, 0), level_size)


class LevelBlock(pygame.sprite.Sprite):

    def __init__(self, tile, pos):
        super( LevelBlock, self).__init__()
        scale_factor = -0.5
        image = pygame.image.load('./gfx/tiles/{}.png'.format(tile)).convert_alpha()
        self.rect = image.get_rect()
        self.rect.inflate_ip(self.rect.w * scale_factor, self.rect.h * scale_factor)
        self.image = pygame.transform.scale(image, self.rect[-2:])
        self.rect.x, self.rect.y = pos


class Decoration(pygame.sprite.Sprite):

    def __init__(self, name, pos):
        super(Decoration, self).__init__()
        self.image = pygame.image.load('./gfx/objects/{}.png'.format(name)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class Crate(pygame.sprite.Sprite):

    def __init__(self, pos):
        super(Crate, self).__init__()
        scale_factor = -0.5
        image = pygame.image.load('./gfx/objects/crate.png').convert()
        self.rect = image.get_rect()
        self.rect.inflate_ip(self.rect.w * scale_factor, self.rect.h * scale_factor)
        self.image = pygame.transform.scale(image, self.rect[-2:])
        self.rect.x, self.rect.y = pos
        self.alpha = 255

    def fade(self):
        self.alpha -= 10
        self.image.set_alpha(self.alpha)
        return self.alpha <= 0
