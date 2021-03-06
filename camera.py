import pygame


class Camera(object):
    def __init__(self, x=0, y=0, w=1, h=1):
        self.pos = pygame.Rect(x, y, w, h)

    def move(self, dx, dy):
        self.pos.move_ip(dx, dy)

    def apply(self, entity):
        return self.apply_rect(entity.rect)

    def apply_rect(self, rect):
        return rect.move(-self.pos.left, -self.pos.top)

    def apply_coords(self, (x, y)):
        return (-self.pos.x + x, -self.pos.y + y)

    def reset(self):
        self.pos.x = self.pos.y = 0

    def __repr__(self):
        return 'Camera {}'.format(self.pos)
