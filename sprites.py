import pygame


class  Background(pygame.sprite.Sprite):
    def __init__(self, screen_size):
        super( Background, self).__init__()
        image = pygame.image.load('./gfx/bg.png').convert()
        self.image = pygame.transform.scale(image, screen_size)
        self.rect = self.image.get_rect()


def load_level():
    images = []
    # ground level
    x = 0
    y = 660
    for i in range(16):
        img = LevelBlock('2', (x, y))
        images.append(img)
        x += 64

    # first floor
    x = 150
    y = 440
    images.append( LevelBlock('14', (x, y)) )
    x += 64
    for i in range(5):
        img = LevelBlock('15', (x, y))
        images.append(img)
        x += 64
    images.append( LevelBlock('16', (x, y)) )

    # second floor
    x = 600
    y = 220
    images.append( LevelBlock('14', (x, y)) )
    x += 64
    for i in range(3):
        img = LevelBlock('15', (x, y))
        images.append(img)
        x += 64
    images.append( LevelBlock('16', (x, y)) )

    return images


class LevelBlock(pygame.sprite.Sprite):

    def __init__(self, tile, pos):
        super( LevelBlock, self).__init__()
        scale_factor = -0.5
        image = pygame.image.load('./gfx/tiles/{}.png'.format(tile)).convert_alpha()
        self.rect = image.get_rect()
        self.rect.inflate_ip(self.rect.w * scale_factor, self.rect.h * scale_factor)
        self.image = pygame.transform.scale(image, self.rect[-2:])
        self.rect.x, self.rect.y = pos
