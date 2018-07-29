import pygame

# one level block is 64x64px, platforms are 64x46
# we use half steps in the level set up to fill the gaps

LEVEL = """
X





                    D E E E F         D E E E F





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
    cam_origin = None
    for y, line in enumerate(LEVEL.splitlines()):
        for x, block in enumerate(line):
            if not block.strip(): continue
            if block == 'X':
                cam_origin = (x*32, y*32)
                continue
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

    return images, deco, objects, pygame.Rect((0, 0), level_size), cam_origin


class LevelSprite(pygame.sprite.Sprite):

    def __init__(self, filename, pos, scale_factor=None):
        super(LevelSprite, self).__init__()
        image = pygame.image.load(filename).convert_alpha()

        self.rect = image.get_rect()
        if scale_factor:
            self.rect.inflate_ip(self.rect.w * scale_factor, self.rect.h * scale_factor)
            self.image = pygame.transform.scale(image, self.rect[-2:])
        else:
            self.image = image
        self.rect.x, self.rect.y = pos

        # smaller version for mini map
        map_scale_factor = -0.5
        self.map_rect = self.rect.copy()
        self.map_rect.inflate_ip(self.map_rect.w * map_scale_factor, self.map_rect.h * map_scale_factor)
        self.map_rect.x, self.map_rect.y = (-map_scale_factor*p for p in pos)
        self.map_image = pygame.transform.scale(image, self.map_rect[-2:])


class LevelBlock(LevelSprite):

    def __init__(self, tile, pos):
        filename = './gfx/tiles/{}.png'.format(tile)
        scale_factor = -0.5
        super(LevelBlock, self).__init__(filename, pos, scale_factor)


class Decoration(LevelSprite):

    def __init__(self, name, pos):
        filename = './gfx/objects/{}.png'.format(name)
        super(Decoration, self).__init__(filename, pos)


class Crate(LevelSprite):

    def __init__(self, pos):
        scale_factor = -0.5
        filename = './gfx/objects/crate.png'
        super(Crate, self).__init__(filename, pos, scale_factor)

    def fade(self):
        self.alpha -= 10
        self.image.set_alpha(self.alpha)
        return self.alpha <= 0
