import pygame


class  Background(pygame.sprite.Sprite):
    def __init__(self, screen_size):
        super( Background, self).__init__()
        image = pygame.image.load('./gfx/bg.png').convert()
        self.image = pygame.transform.scale(image, screen_size)
        self.rect = self.image.get_rect()


def load_level():
    images = []
    objects = []
    # ground level
    x = 0
    y = 660
    for i in range(16):
        if i == 4:
            block = '7'
        elif i == 5:
            block = '8'
        elif i == 6:
            block = '10'
        elif i == 7:
            block = '11'
        elif i == 11:
            block = '7'
        elif i == 12:
            block = '8'
        elif i == 13:
            block = '10'
        elif i == 14:
            block = '11'
        else:
            block = '2'
        img = LevelBlock(block, (x, y))
        images.append(img)
        x += 64
    objects.append( Decoration('stone', (120, 588)))
    objects.append( Decoration('cactus1', (600, 550)))

    # hill
    images.append( LevelBlock('4', (768, 596)) )
    images.append( LevelBlock('6', (832, 596)) )
    images.append( LevelBlock('1', (768, 532)) )
    images.append( LevelBlock('3', (832, 532)) )

    # first floor
    x = 96
    y = 404
    blocks = ('14', '15', '15', '15', '15', '15', '16')
    for block in blocks:
        x += 64
        images.append( LevelBlock(block, (x, y)) )

    x -= 192
    y += 40 # needs some overlap because we don't have a fitting tile
    images.append( LevelBlock('5', (x, y)) )
    y += 64
    images.append( LevelBlock('5', (x, y)) )
    y += 64
    images.append( LevelBlock('5', (x, y)) )
    y += 64
    images.append( LevelBlock('5', (x, y)) )

    # second floor
    x = 600
    y = 180
    images.append( LevelBlock('14', (x, y)) )
    x += 64
    for i in range(3):
        img = LevelBlock('15', (x, y))
        images.append(img)
        x += 64
    images.append( LevelBlock('16', (x, y)) )
    objects.append( Decoration('skeleton', (700, 132)))

    return images, objects


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


class Kunai(pygame.sprite.Sprite):

    def __init__(self, pos, moving_right, screen):
        super(Kunai, self).__init__()
        scale_factor = -0.7
        image = pygame.image.load('./gfx/ninja/Kunai.png').convert_alpha()
        self.rect = image.get_rect()
        self.rect.inflate_ip(self.rect.w * scale_factor, self.rect.h * scale_factor)
        self.orig_image = pygame.transform.scale(image, self.rect[-2:])
        self.image = self.orig_image
        if moving_right:
            self.rect.x, self.rect.y = pos
        else:
            self.rect.right, self.rect.y = pos
        self.moving_right = moving_right
        self.screen = screen
        self.counter = 0


    def update(self, level):
        """ Returns True if we're off screen and False otherwise """
        dx = 8 if self.moving_right else -8
        self.rect.move_ip(dx, 0)
        self.image = pygame.transform.rotate(self.orig_image, self.counter*10)
        self.counter += 1

        hit = any(self.rect.colliderect(block) for block in level)
        return hit or self.rect.x > self.screen.w or self.rect.right < 0
