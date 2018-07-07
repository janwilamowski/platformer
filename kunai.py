import pygame


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
        self.rect.x -= 1000 # hide until active
        self.moving_right = moving_right
        self.screen = screen
        self.counter = 0
        self.frozen = True


    def update(self, level):
        """ Returns True if we're off screen and False otherwise """
        if self.frozen: return

        dx = 8 if self.moving_right else -8
        self.rect.move_ip(dx, 0)
        center = self.rect.center
        angle = 180 + self.counter*10 if self.moving_right else 180 - self.counter*10
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect.w = self.image.get_rect().w
        self.rect.h = self.image.get_rect().h
        self.rect.center = center
        self.counter += 1

        hit = any(self.rect.colliderect(block) for block in level)
        return hit or self.rect.x > self.screen.w or self.rect.right < 0
