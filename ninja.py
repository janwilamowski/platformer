from sprites import Kunai
from Character import Character


player_states = [
    'Idle',
    'Run',
    'Climb',
    'Dead',
    'Glide',
    'Attack',
    'Jump',
    'JumpAttack',
    'Throw',
    'JumpThrow',
]

class Ninja(Character):

    def __init__(self, position, screen):
        super(Ninja, self).__init__('gfx/ninja', player_states, position, screen)


    def move_down(self):
        self.state = 'Climb'
        self.frozen = False
        self.velocity.y = 4


    def move_up(self):
        self.state = 'Climb'
        self.frozen = False
        self.velocity.y = -4


    def jump(self):
        if self.current_animation: return
        # TODO: only allow if on ground

        self.set_anim('Jump')
        # TODO: delays animation
        self.current_frame = 0 # make sure each jump frame is the same length


    def throw(self):
        if self.current_animation: return

        self.set_anim('Throw')
        self.hidden = False
        if self.facing_right:
            pos = self.rect.move(self.rect.width, 40)
        else:
            pos = self.rect.move(-10, 40)

        kunai = Kunai(pos[:2], self.facing_right, self.screen)
        def activate():
            kunai.rect.x += 1000
            kunai.frozen = False
        self.callbacks.append( (3, activate) )
        return kunai


    def glide(self, level):
        if self.rect.collidelistall(level): return

        self.set_anim('Glide')
