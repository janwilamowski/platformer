import os, glob
import pygame
from sprites import Kunai


class Vector2():
    """ stand-in for pygame.math.Vector2 """
    def __init__(self, x, y):
        self.x = x
        self.y = y


player_states = {
    'Idle',
    'Run',
    'Climb',
    'Dead',
    'Glide',
    'Attack',
    'Jump',
    'Jump_Attack',
    'Throw',
    'Jump_Throw',
}

FALL_SPEED = 8


class Ninja(pygame.sprite.Sprite):

    def __init__(self, position, screen):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the Ninja.
            images: Images to use in the animation.
        """
        super(Ninja, self).__init__()

        self.screen = screen

        size = (60, 110)  # This should match the size of the images.

        self.rect = pygame.Rect(position, size)
        self.all_images = self.load_images('gfx/ninja')
        self.state = 'Idle'
        self.images = self.all_images[self.state]
        self.index = 0
        self.image = self.images[self.index]  # 'image' is the current image of the animation.

        self.velocity = Vector2(0, 0)

        self.animation_frames = 4 # video frames per animation frame
        self.current_frame = 0
        self.previous_state = 'Idle'

        self.facing_right = True
        self.current_animation = None
        self.frozen = False


    def load_images(self, path, pattern=None):
        """
        Loads all images in directory. The directory must only contain images.

        Args:
            path: The relative or absolute path to the directory to load images from.

        Returns:
            List of images.
        """
        images = {}
        for state in player_states:
            pattern = '{}_?.png'.format(state)
            images[state] = []
            files = glob.glob(os.path.join(path, pattern)) if pattern else os.listdir(path)
            for file_name in sorted(files):
                image = pygame.image.load(file_name).convert_alpha()
                h, l = image.get_rect()[-2:]
                image = pygame.transform.scale(image, (h/4, l/4))
                images[state].append(image)
        return images


    def fall(self, level):
        if self.state == 'Climb': return

        if self.rect.collidelistall(level):
            self.velocity.y = 0
        else:
            self.velocity.y = FALL_SPEED / 4 if self.state == 'Glide' else FALL_SPEED


    def move_right(self):
        self.state = 'Run'
        self.facing_right = True
        self.frozen = False
        self.velocity.x = 4
        self.previous_state = 'Run'


    def move_left(self):
        self.state = 'Run'
        self.facing_right = False
        self.frozen = False
        self.velocity.x = -4
        self.previous_state = 'Run'


    def move_down(self):
        self.state = 'Climb'
        self.frozen = False
        self.velocity.y = 4


    def move_up(self):
        self.state = 'Climb'
        self.frozen = False
        self.velocity.y = -4


    def stop(self):
        if self.state == 'Climb':
            self.frozen = True
        else:
            self.state = 'Idle'
            # self.frozen = False
        self.velocity.x = 0
        self.velocity.y = 0
        self.previous_state = 'Idle'


    def jump(self):
        if self.current_animation: return

        self.current_animation = self.state = 'Jump'
        self.index = -1
        self.current_frame = 0 # make sure each jump frame is the same length


    def attack(self):
        if self.current_animation: return

        self.current_animation = self.state = 'Attack'
        self.index = -1


    def throw(self):
        if self.current_animation: return

        self.current_animation = self.state = 'Throw'
        self.index = -1
        if self.facing_right:
            pos = self.rect.move(self.rect.width, 40)
        else:
            pos = self.rect.move(-10, 40)

        return Kunai(pos[:2], self.facing_right, self.screen)


    def die(self):
        self.current_animation = self.state = 'Dead'
        self.index = -1


    def glide(self, level):
        if self.rect.collidelistall(level): return

        self.current_animation = self.state = 'Glide'
        self.index = -1


    def draw(self, surface, debug=False):
        pos = self.rect
        img_width = self.image.get_rect().width
        # TODO: some of the sprites have a margin
        if not self.facing_right:
            idle_width = 58
            dx = idle_width - img_width
            pos = self.rect.move(dx, 0)
            pos.width = img_width
        surface.blit(self.image, pos)
        if debug:
            pygame.draw.rect(surface, pygame.Color('red'), pos, 1)


    def get_anim(self):
        if self.current_animation:
            return self.images, self.index
        else:
            return [], None


    def update(self, level):
        """
        Updates the image of Sprite every 6 frame (approximately every 0.1 second if frame rate is 60).
        """
        self.images = self.all_images[self.state]
        if not self.facing_right:
            self.images = [pygame.transform.flip(image, True, False) for image in self.images]

        jump_y = [-10.0, -9.511, -8.09, -5.878, -3.09, -0.0, 3.09, 5.878, 8.09, 9.511]
        if not self.frozen:
            self.current_frame += 1
            if self.current_animation == 'Jump':
                self.velocity.y = jump_y[self.index+1]
            if self.current_frame >= self.animation_frames:
                self.current_frame = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
                if self.current_animation:
                    if self.index == len(self.images) - 1:
                        if self.state == 'Dead':
                            self.frozen = True
                        else:
                            self.current_animation = None
                            self.state = self.previous_state

        # collision detection
        self.rect.move_ip(self.velocity.x, 0)
        for block in level:
            if block.colliderect(self.rect):
                if self.facing_right:
                    self.rect.right = block.left
                else:
                    self.rect.left = block.right
        self.rect.move_ip(0, self.velocity.y)
        for block in level:
            if block.colliderect(self.rect):
                if self.velocity.y > 0: # moving down
                    self.rect.bottom = block.top
                else: # moving up
                    self.rect.top = block.bottom

        # correct if off screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > self.screen.w - self.rect.w:
            self.rect.x = self.screen.w - self.rect.w
        if self.rect.y < 0:
            self.rect.y = 0
