import os, glob
import pygame


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

        self.animation_frames = 6
        self.current_frame = 0

        self.current_animation = None
        self.animation_start = None

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
            for file_name in files:
                image = pygame.image.load(file_name).convert_alpha()
                h, l = image.get_rect()[-2:]
                image = pygame.transform.scale(image, (h/4, l/4))
                images[state].append(image)
        return images


    def fall(self, level):
        if self.state == 'Climb': return

        if any(block.collidepoint(self.rect.bottomright) or
                    block.collidepoint(self.rect.bottomleft)
                    for block in level):
            self.velocity.y = 0 # TODO: overshoots boundary
        else:
            self.velocity.y = 8


    def move_right(self):
        self.state = 'Run'
        self.frozen = False
        self.velocity.x = 4


    def move_left(self):
        self.state = 'Run'
        self.frozen = False
        self.velocity.x = -4


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


    def jump(self):
        self.state = 'Jump' # TODO: perform animation (capture x-speed, inc&dec y speed)


    def attack(self):
        if self.current_animation: return

        self.current_animation = 'Attack'
        self.animation_start = self.index = 0
        self.state = 'Attack'


    def update(self, dt):
        """
        Updates the image of Sprite every 6 frame (approximately every 0.1 second if frame rate is 60).
        """
        self.images = self.all_images[self.state]
        self.images_right = self.images
        self.images_left = [pygame.transform.flip(image, True, False) for image in self.images]  # Flipping every image.
        if self.velocity.x > 0:  # Use the right images if sprite is moving right.
            self.images = self.images_right
        elif self.velocity.x < 0:
            self.images = self.images_left

        if not self.frozen:
            self.current_frame += 1
            if self.current_frame >= self.animation_frames:
                self.current_frame = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
                if self.current_animation:
                    print(self.index) # TODO: animation incomplete and choppy
                if self.index == self.animation_start:
                    print('animation over')
                    self.animation_start = None
                    self.current_animation = None
                    self.state = 'Idle' # TODO: reset to previous?

        self.rect.move_ip(self.velocity.x, self.velocity.y)
        # correct if off screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > self.screen.w - self.rect.w:
            self.rect.x = self.screen.w - self.rect.w
        # TODO: check collisions with level
